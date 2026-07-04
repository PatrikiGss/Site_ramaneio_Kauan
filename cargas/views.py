from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CargaForm, FiltroCargaForm
from .models import Carga


class CargaDoUsuarioMixin(LoginRequiredMixin):
    """Exige login e limita o queryset às cargas do próprio usuário.

    É este mixin que garante o isolamento de dados: como Detail/Update/Delete
    buscam o objeto dentro do queryset, uma carga de outro usuário resulta em
    404 (como se não existisse) em vez de vazar informação de que o registro
    existe mas é de outra pessoa.
    """

    def get_queryset(self):
        return super().get_queryset().filter(usuario=self.request.user)


class CargaListView(CargaDoUsuarioMixin, ListView):
    model = Carga
    paginate_by = 15
    context_object_name = 'cargas'

    def get_queryset(self):
        # super() já devolve apenas as cargas do usuário logado (mixin acima);
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
    model = Carga
    context_object_name = 'carga'
    success_url = reverse_lazy('cargas:lista')

    def form_valid(self, form):
        messages.success(self.request, f'Carga #{self.object.pk} excluída com sucesso.')
        return super().form_valid(form)
