from django.contrib import admin

from .models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    """Permite ao suporte forçar nova troca de senha marcando a flag."""

    list_display = ('usuario', 'trocar_senha_no_proximo_acesso')
    list_filter = ('trocar_senha_no_proximo_acesso',)
    search_fields = ('usuario__username',)
