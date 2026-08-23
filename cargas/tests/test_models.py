"""Comportamento do modelo Carga (incluindo a lixeira)."""
from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class CargaModelTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()

    def test_str_identifica_carga(self):
        carga = self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.GALA)
        texto = str(carga)
        self.assertIn(f'#{carga.pk}', texto)
        self.assertIn('Gala', texto)

    def test_get_absolute_url_aponta_para_detalhe(self):
        carga = self.criar_carga(self.usuario)
        self.assertEqual(
            carga.get_absolute_url(),
            reverse('cargas:detalhe', kwargs={'pk': carga.pk}),
        )

    def test_datas_preenchidas_automaticamente(self):
        carga = self.criar_carga(self.usuario)
        self.assertIsNotNone(carga.criado_em)
        self.assertIsNotNone(carga.atualizado_em)

    def test_ordenacao_mais_recente_primeiro(self):
        antiga = self.criar_carga(self.usuario, criado_em=self.momento(dias_atras=5))
        recente = self.criar_carga(self.usuario, criado_em=self.momento(dias_atras=1))
        self.assertEqual(list(Carga.objects.all()), [recente, antiga])


class LixeiraModelTests(RomaneioTestCase):
    """A exclusão reversível é a proteção contra apagar registro sem querer."""

    def setUp(self):
        self.usuario = self.criar_usuario()
        self.carga = self.criar_carga(self.usuario)

    def test_carga_nova_nao_esta_na_lixeira(self):
        self.assertIsNone(self.carga.excluido_em)
        self.assertFalse(self.carga.na_lixeira)

    def test_mover_para_lixeira_marca_data_sem_apagar(self):
        self.carga.mover_para_lixeira()
        self.carga.refresh_from_db()
        self.assertIsNotNone(self.carga.excluido_em)
        self.assertTrue(self.carga.na_lixeira)
        # o registro continua existindo no banco: é isso que torna reversível
        self.assertTrue(Carga.objects.filter(pk=self.carga.pk).exists())

    def test_restaurar_devolve_carga(self):
        self.carga.mover_para_lixeira()
        self.carga.restaurar()
        self.carga.refresh_from_db()
        self.assertIsNone(self.carga.excluido_em)
        self.assertFalse(self.carga.na_lixeira)
