"""Base e utilidades compartilhadas pelos testes do app cargas."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from cargas.models import Carga

# Senha usada nos testes: precisa passar pelos validadores do Django
# (tamanho mínimo, não ser comum, não ser só números).
SENHA_PADRAO = 'Romaneio!Teste2026'


class RomaneioTestCase(TestCase):
    """TestCase com atalhos para criar usuários e cargas nos testes."""

    def criar_usuario(self, username='operador', senha=SENHA_PADRAO, **extra):
        return User.objects.create_user(username=username, password=senha, **extra)

    def criar_carga(self, usuario, *, tipo_maca=Carga.TipoMaca.FUJI,
                    tamanho=Carga.Tamanho.MEDIA, quantidade_caixas=10,
                    peso_total='100.00', observacoes='', criado_em=None):
        """Cria uma carga; `criado_em` permite simular registros de outros dias."""
        carga = Carga.objects.create(
            usuario=usuario,
            tipo_maca=tipo_maca,
            tamanho=tamanho,
            quantidade_caixas=quantidade_caixas,
            peso_total=Decimal(peso_total),
            observacoes=observacoes,
        )
        if criado_em is not None:
            # criado_em usa auto_now_add, que ignora atribuição direta:
            # a única forma de datar o registro no passado é um UPDATE.
            Carga.objects.filter(pk=carga.pk).update(criado_em=criado_em)
            carga.refresh_from_db()
        return carga

    def momento(self, dias_atras=0, hora=12):
        """Datetime ciente de fuso, N dias atrás, no fuso local do projeto."""
        alvo = timezone.localtime() - timedelta(days=dias_atras)
        return alvo.replace(hour=hora, minute=0, second=0, microsecond=0)
