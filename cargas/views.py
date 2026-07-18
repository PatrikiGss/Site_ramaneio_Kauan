from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import CargaForm, FiltroCargaForm
from .models import Carga


class CargaDoUsuarioMixin(LoginRequiredMixin):
    """Exige login e limita o queryset às cargas ATIVAS do próprio usuário.

    É este mixin que garante o isolamento de dados: como Detail/Update/Delete
    buscam o objeto dentro do queryset, uma carga de outro usuário (ou já na
    lixeira) resulta em 404 (como se não existisse) em vez de vazar informação.
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            usuario=self.request.user, excluido_em__isnull=True,
        )


class CargaLixeiraMixin(LoginRequiredMixin):
    """Base das telas da lixeira: cargas do usuário que estão excluídas."""

    def get_queryset(self):
        return Carga.objects.filter(
            usuario=self.request.user, excluido_em__isnull=False,
        )


class CargaListView(CargaDoUsuarioMixin, ListView):
    model = Carga
    paginate_by = 15
    context_object_name = 'cargas'

    def get_queryset(self):
        # super() já devolve apenas as cargas ativas do usuário logado (mixin);
        # aqui aplicamos por cima os filtros opcionais vindos da URL (?tipo=...).
        queryset = super().get_queryset()
        self.filtro = FiltroCargaForm(self.request.GET or None)
        if self.filtro.is_valid():
            dados = self.filtro.cleaned_data
            if dados['busca']:
                # Busca textual nas observações; se o usuário digitou só números,
                # tenta também casar com o nº (id) da carga.
                filtro_busca = Q(observacoes__icontains=dados['busca'])
                if dados['busca'].isdigit():
                    filtro_busca |= Q(pk=int(dados['busca']))
                queryset = queryset.filter(filtro_busca)
            if dados['tipo_maca']:
                queryset = queryset.filter(tipo_maca=dados['tipo_maca'])
            if dados['tamanho']:
                queryset = queryset.filter(tamanho=dados['tamanho'])
            # __date compara só a parte da data do campo datetime, ignorando a hora
            if dados['data_inicio']:
                queryset = queryset.filter(criado_em__date__gte=dados['data_inicio'])
            if dados['data_fim']:
                queryset = queryset.filter(criado_em__date__lte=dados['data_fim'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro'] = self.filtro
        # Totais calculados sobre o resultado JÁ filtrado (todas as páginas),
        # e não apenas sobre os itens da página atual.
        context['totais'] = self.object_list.aggregate(
            cargas=Count('id'),
            caixas=Sum('quantidade_caixas'),
            peso=Sum('peso_total'),
        )
        # Recria a querystring sem o parâmetro "page" para que os links de
        # paginação preservem os filtros ativos (?tipo=FUJI&page=2).
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        context['querystring'] = parametros.urlencode()
        context['total_lixeira'] = Carga.objects.filter(
            usuario=self.request.user, excluido_em__isnull=False,
        ).count()
        return context


class CargaDetailView(CargaDoUsuarioMixin, DetailView):
    model = Carga
    context_object_name = 'carga'


class CargaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Carga
    form_class = CargaForm
    success_message = 'Carga registrada com sucesso!'

    def form_valid(self, form):
        # O dono não vem do formulário (seria falsificável): é sempre
        # definido no servidor como o usuário autenticado da requisição.
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CargaUpdateView(CargaDoUsuarioMixin, SuccessMessageMixin, UpdateView):
    model = Carga
    form_class = CargaForm
    success_message = 'Carga atualizada com sucesso!'


class CargaDeleteView(CargaDoUsuarioMixin, DeleteView):
    """"Excluir" move a carga para a lixeira (reversível), não apaga de vez."""

    model = Carga
    context_object_name = 'carga'
    success_url = reverse_lazy('cargas:lista')

    def form_valid(self, form):
        # self.object já foi carregado no post(); em vez de deletar, marcamos
        # como excluída. A exclusão definitiva fica na tela da lixeira.
        self.object.mover_para_lixeira()
        messages.success(self.request, f'Carga #{self.object.pk} movida para a lixeira.')
        return redirect(self.success_url)


class LixeiraListView(CargaLixeiraMixin, ListView):
    model = Carga
    paginate_by = 15
    context_object_name = 'cargas'
    template_name = 'cargas/lixeira.html'

    def get_queryset(self):
        return super().get_queryset().order_by('-excluido_em')


class RestaurarCargaView(CargaLixeiraMixin, View):
    """Tira a carga da lixeira (POST)."""

    def post(self, request, pk):
        carga = get_object_or_404(self.get_queryset(), pk=pk)
        carga.restaurar()
        messages.success(request, f'Carga #{carga.pk} restaurada.')
        return redirect('cargas:lixeira')


class ExcluirDefinitivoView(CargaLixeiraMixin, DeleteView):
    """Exclusão DEFINITIVA (irreversível), só a partir da lixeira."""

    model = Carga
    context_object_name = 'carga'
    template_name = 'cargas/carga_confirm_delete_definitivo.html'
    success_url = reverse_lazy('cargas:lixeira')

    def form_valid(self, form):
        messages.success(self.request, f'Carga #{self.object.pk} excluída definitivamente.')
        return super().form_valid(form)


class ResumoView(LoginRequiredMixin, TemplateView):
    """Fechamento por período: totais agrupados por tipo, por tamanho e por dia."""

    template_name = 'cargas/resumo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.localdate()

        def parse(nome, padrao):
            valor = parse_date(self.request.GET.get(nome, '') or '')
            return valor or padrao

        inicio = parse('data_inicio', hoje)
        fim = parse('data_fim', hoje)
        if inicio > fim:
            inicio, fim = fim, inicio

        base = Carga.objects.filter(
            usuario=self.request.user,
            excluido_em__isnull=True,
            criado_em__date__gte=inicio,
            criado_em__date__lte=fim,
        )

        # Uma única expressão de agregação reaproveitada no geral e nos grupos
        agg = dict(caixas=Sum('quantidade_caixas'), peso=Sum('peso_total'), n=Count('id'))

        tipos = dict(Carga.TipoMaca.choices)
        tamanhos = dict(Carga.Tamanho.choices)

        def rotular(linhas, campo, mapa):
            # Substitui o código (ex.: 'FUJI') pelo rótulo legível ('Fuji')
            saida = []
            for linha in linhas:
                item = dict(linha)
                item['label'] = mapa.get(linha[campo], linha[campo])
                saida.append(item)
            return saida

        context['inicio'] = inicio
        context['fim'] = fim
        context['geral'] = base.aggregate(**agg)
        context['por_tipo'] = rotular(
            base.values('tipo_maca').annotate(**agg).order_by('-caixas'), 'tipo_maca', tipos)
        context['por_tamanho'] = rotular(
            base.values('tamanho').annotate(**agg).order_by('-caixas'), 'tamanho', tamanhos)
        context['por_dia'] = list(
            base.annotate(dia=TruncDate('criado_em')).values('dia').annotate(**agg).order_by('-dia'))
        # Atalhos de período para os botões rápidos
        context['hoje'] = hoje
        context['inicio_semana'] = hoje - timedelta(days=6)
        context['inicio_mes'] = hoje.replace(day=1)
        return context
