from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Informações de conta que o modelo padrão de usuário do Django não tem.

    Hoje guarda apenas a flag de troca obrigatória de senha, marcada quando a
    conta é criada por outro usuário (senha provisória) e desmarcada quando o
    dono define a própria senha.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='usuário',
    )
    trocar_senha_no_proximo_acesso = models.BooleanField(
        'trocar senha no próximo acesso',
        default=False,
    )

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'
