from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'contas'

urlpatterns = [
    path(
        'entrar/',
        auth_views.LoginView.as_view(
            template_name='contas/login.html',
            authentication_form=LoginForm,
            # Quem já está logado e acessa /contas/entrar/ vai direto para a lista
            redirect_authenticated_user=True,
        ),
        name='entrar',
    ),
    # Por segurança o Django só aceita logout via POST (evita deslogar alguém
    # com um simples link malicioso); o botão "Sair" no menu é um form.
    path('sair/', auth_views.LogoutView.as_view(), name='sair'),
    path('registrar/', views.RegistroView.as_view(), name='registrar'),
    path('trocar-senha/', views.TrocarSenhaView.as_view(), name='trocar_senha'),
]
