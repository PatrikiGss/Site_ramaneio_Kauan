"""Exigência de login e isolamento de dados entre usuários.

São os testes mais importantes do sistema: cada operador só pode ver e mexer
nas próprias cargas. Uma regressão aqui vaza dados de um cliente para outro.
"""
from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class LoginObrigatorioTests(RomaneioTestCase):
    """Nenhuma tela do romaneio pode ficar aberta para anônimos."""

    def setUp(self):
        self.usuario = self.criar_usuario()
        self.carga = self.criar_carga(self.usuario)

    def test_todas_as_rotas_exigem_login(self):
        rotas = [
            reverse('cargas:lista'),
            reverse('cargas:nova'),
            reverse('cargas:resumo'),
            reverse('cargas:lixeira'),
            reverse('cargas:detalhe', kwargs={'pk': self.carga.pk}),
            reverse('cargas:editar', kwargs={'pk': self.carga.pk}),
            reverse('cargas:excluir', kwargs={'pk': self.carga.pk}),
            reverse('cargas:restaurar', kwargs={'pk': self.carga.pk}),
            reverse('cargas:excluir_definitivo', kwargs={'pk': self.carga.pk}),
        ]
        login = reverse('contas:entrar')
        for rota in rotas:
            with self.subTest(rota=rota):
                resposta = self.client.get(rota)
                self.assertEqual(resposta.status_code, 302)
                self.assertIn(login, resposta.url)

    def test_anonimo_nao_cria_carga(self):
        self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 1, 'peso_total': '1.00',
        })
        self.assertEqual(Carga.objects.count(), 1)  # segue só a do setUp


class IsolamentoEntreUsuariosTests(RomaneioTestCase):
    def setUp(self):
        self.dono = self.criar_usuario('dono')
        self.intruso = self.criar_usuario('intruso')
        self.carga = self.criar_carga(self.dono, observacoes='carga do dono')
        self.client.force_login(self.intruso)

    def test_carga_alheia_responde_404(self):
        """404 (e não 403) para não revelar que o registro existe."""
        rotas = [
            reverse('cargas:detalhe', kwargs={'pk': self.carga.pk}),
            reverse('cargas:editar', kwargs={'pk': self.carga.pk}),
            reverse('cargas:excluir', kwargs={'pk': self.carga.pk}),
        ]
        for rota in rotas:
            with self.subTest(rota=rota):
                self.assertEqual(self.client.get(rota).status_code, 404)

    def test_nao_edita_carga_alheia(self):
        resposta = self.client.post(
            reverse('cargas:editar', kwargs={'pk': self.carga.pk}),
            {'tipo_maca': 'GALA', 'tamanho': 'G',
             'quantidade_caixas': 999, 'peso_total': '999.00'},
        )
        self.assertEqual(resposta.status_code, 404)
        self.carga.refresh_from_db()
        self.assertEqual(self.carga.quantidade_caixas, 10)

    def test_nao_exclui_carga_alheia(self):
        resposta = self.client.post(
            reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        self.assertEqual(resposta.status_code, 404)
        self.carga.refresh_from_db()
        self.assertIsNone(self.carga.excluido_em)

    def test_lista_nao_mostra_carga_alheia(self):
        resposta = self.client.get(reverse('cargas:lista'))
        self.assertNotIn(self.carga, resposta.context['cargas'])
        self.assertNotContains(resposta, 'carga do dono')

    def test_totais_ignoram_cargas_alheias(self):
        resposta = self.client.get(reverse('cargas:lista'))
        self.assertEqual(resposta.context['totais']['cargas'], 0)

    def test_resumo_ignora_cargas_alheias(self):
        resposta = self.client.get(reverse('cargas:resumo'))
        self.assertEqual(resposta.context['geral']['n'], 0)

    def test_lixeira_nao_mostra_carga_alheia(self):
        self.carga.mover_para_lixeira()
        resposta = self.client.get(reverse('cargas:lixeira'))
        self.assertNotIn(self.carga, resposta.context['cargas'])

    def test_nao_restaura_nem_apaga_carga_alheia_da_lixeira(self):
        self.carga.mover_para_lixeira()
        restaurar = self.client.post(
            reverse('cargas:restaurar', kwargs={'pk': self.carga.pk}))
        apagar = self.client.post(
            reverse('cargas:excluir_definitivo', kwargs={'pk': self.carga.pk}))
        self.assertEqual(restaurar.status_code, 404)
        self.assertEqual(apagar.status_code, 404)
        self.carga.refresh_from_db()
        self.assertIsNotNone(self.carga.excluido_em)
        self.assertTrue(Carga.objects.filter(pk=self.carga.pk).exists())
