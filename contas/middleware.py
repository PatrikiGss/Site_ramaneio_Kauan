from django.shortcuts import redirect
from django.urls import reverse

from .models import Perfil


class TrocaSenhaObrigatoriaMiddleware:
    """Bloqueia a navegação de quem ainda usa a senha provisória.

    Contas criadas por outro usuário nascem com a flag
    `trocar_senha_no_proximo_acesso` ligada. Enquanto ela estiver ligada,
    qualquer página que o usuário tente abrir redireciona para a troca de
    senha — só a própria troca, o logout e o /admin/ (para não travar tarefas
    de suporte) ficam de fora do bloqueio. Arquivos estáticos não passam por
    aqui porque o WhiteNoise os responde antes deste middleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            deve_trocar = Perfil.objects.filter(
                usuario=request.user,
                trocar_senha_no_proximo_acesso=True,
            ).exists()
            if deve_trocar:
                liberadas = (reverse('contas:trocar_senha'), reverse('contas:sair'))
                if request.path not in liberadas and not request.path.startswith('/admin/'):
                    return redirect('contas:trocar_senha')
        return self.get_response(request)
