from django.contrib import admin

from .models import Carga


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'criado_em', 'tipo_maca', 'tamanho', 'quantidade_caixas', 'peso_total')
    list_filter = ('usuario', 'tipo_maca', 'tamanho', 'criado_em')
    search_fields = ('observacoes',)
    date_hierarchy = 'criado_em'
    readonly_fields = ('criado_em', 'atualizado_em')
