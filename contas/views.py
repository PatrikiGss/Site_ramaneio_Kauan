from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegistroForm, TrocaSenhaForm
from .models import Perfil


class RegistroView(LoginRequiredMixin, CreateView):
    """Criação de conta para terceiros — restrita a usuários já cadastrados."""

    form_class = RegistroForm
    template_name = 'contas/registro.html'
    success_url = reverse_lazy('cargas:lista')

    def form_valid(self, form):
        # Quem cria a conta é um usuário logado criando para OUTRA pessoa,
        # então não fazemos login na conta nova (o criador perderia a própria
        # sessão). A conta nasce marcada para trocar a senha provisória no
        # primeiro acesso (ver TrocaSenhaObrigatoriaMiddleware).
        resposta = super().form_valid(form)
        Perfil.objects.create(usuario=self.object, trocar_senha_no_proximo_acesso=True)
        messages.success(
            self.request,
            f"Conta '{self.object.username}' criada. Informe a senha provisória "
            f"ao usuário — no primeiro acesso ele deverá definir uma nova senha.",
        )
        return resposta


class TrocarSenhaView(LoginRequiredMixin, PasswordChangeView):
    form_class = TrocaSenhaForm
    template_name = 'contas/trocar_senha.html'
    success_url = reverse_lazy('cargas:lista')

    def form_valid(self, form):
        # O PasswordChangeView do Django já atualiza a sessão para o usuário
        # não ser deslogado ao trocar a própria senha; aqui só desligamos a
        # flag de primeiro acesso para liberar a navegação.
        resposta = super().form_valid(form)
        Perfil.objects.update_or_create(
            usuario=self.request.user,
            defaults={'trocar_senha_no_proximo_acesso': False},
        )
        messages.success(self.request, 'Senha alterada com sucesso!')
        return resposta
