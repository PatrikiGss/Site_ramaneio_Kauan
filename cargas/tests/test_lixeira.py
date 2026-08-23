"""Tela da lixeira: restaurar e excluir definitivamente."""
from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class LixeiraTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.ativa = self.criar_carga(self.usuario, observacoes='ativa')
        self.excluida = self.criar_carga(self.usuario, observacoes='excluida')
        self.excluida.mover_para_lixeira()

    def test_lixeira_lista_apenas_excluidas(self):
        resposta = self.client.get(reverse('cargas:lixeira'))
        self.assertEqual(list(resposta.context['cargas']), [self.excluida])

    def test_restaurar_devolve_para_a_lista(self):
        self.client.post(
            reverse('cargas:restaurar', kwargs={'pk': self.excluida.pk}))
        self.excluida.refresh_from_db()
        self.assertIsNone(self.excluida.excluido_em)
        lista = self.client.get(reverse('cargas:lista'))
        self.assertIn(self.excluida, lista.context['cargas'])

    def test_restaurar_exige_post(self):
        """GET não pode alterar dados (evita restaurar por link/prefetch)."""
        self.client.get(reverse('cargas:restaurar', kwargs={'pk': self.excluida.pk}))
        self.excluida.refresh_from_db()
        self.assertIsNotNone(self.excluida.excluido_em)

    def test_restaurar_carga_ativa_responde_404(self):
        resposta = self.client.post(
            reverse('cargas:restaurar', kwargs={'pk': self.ativa.pk}))
        self.assertEqual(resposta.status_code, 404)

    def test_excluir_definitivo_apaga_de_vez(self):
        self.client.post(
            reverse('cargas:excluir_definitivo', kwargs={'pk': self.excluida.pk}))
        self.assertFalse(Carga.objects.filter(pk=self.excluida.pk).exists())

    def test_excluir_definitivo_so_a_partir_da_lixeira(self):
        """Uma carga ativa não pode ser apagada sem passar pela lixeira."""
        resposta = self.client.post(
            reverse('cargas:excluir_definitivo', kwargs={'pk': self.ativa.pk}))
        self.assertEqual(resposta.status_code, 404)
        self.assertTrue(Carga.objects.filter(pk=self.ativa.pk).exists())

    def test_confirmacao_nao_apaga(self):
        resposta = self.client.get(
            reverse('cargas:excluir_definitivo', kwargs={'pk': self.excluida.pk}))
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(Carga.objects.filter(pk=self.excluida.pk).exists())

    def test_lixeira_vazia_responde_normalmente(self):
        self.excluida.delete()
        resposta = self.client.get(reverse('cargas:lixeira'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(list(resposta.context['cargas']), [])


class FluxoCompletoLixeiraTests(RomaneioTestCase):
    """Percurso real do usuário: excluir -> conferir na lixeira -> restaurar.

    Passa pelas telas (e não pelos métodos do modelo), garantindo que a
    exclusão continue reversível de ponta a ponta.
    """

    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.carga = self.criar_carga(self.usuario, observacoes='romaneio do dia')

    def test_excluir_pela_tela_manda_para_a_lixeira(self):
        self.client.post(reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        # continua existindo...
        self.assertTrue(Carga.objects.filter(pk=self.carga.pk).exists())
        # ...e aparece na lixeira
        lixeira = self.client.get(reverse('cargas:lixeira'))
        self.assertIn(self.carga, lixeira.context['cargas'])

    def test_ciclo_excluir_e_restaurar_preserva_os_dados(self):
        self.client.post(reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        self.client.post(reverse('cargas:restaurar', kwargs={'pk': self.carga.pk}))
        lista = self.client.get(reverse('cargas:lista'))
        self.assertIn(self.carga, lista.context['cargas'])
        self.carga.refresh_from_db()
        self.assertEqual(self.carga.observacoes, 'romaneio do dia')
        self.assertEqual(self.carga.quantidade_caixas, 10)

    def test_totais_voltam_apos_restaurar(self):
        self.client.post(reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        self.assertEqual(
            self.client.get(reverse('cargas:lista')).context['totais']['cargas'], 0)
        self.client.post(reverse('cargas:restaurar', kwargs={'pk': self.carga.pk}))
        self.assertEqual(
            self.client.get(reverse('cargas:lista')).context['totais']['cargas'], 1)
