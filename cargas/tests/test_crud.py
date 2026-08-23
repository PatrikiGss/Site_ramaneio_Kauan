"""Cadastro, edição e exclusão de cargas pelas telas."""
from decimal import Decimal

from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class CadastroTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)

    def test_cadastra_carga(self):
        resposta = self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'GALA', 'tamanho': 'G',
            'quantidade_caixas': 120, 'peso_total': '2160.50',
            'observacoes': 'caminhao ABC1D23',
        }, follow=True)
        self.assertEqual(resposta.status_code, 200)
        carga = Carga.objects.get()
        self.assertEqual(carga.tipo_maca, 'GALA')
        self.assertEqual(carga.quantidade_caixas, 120)
        self.assertEqual(carga.peso_total, Decimal('2160.50'))
        self.assertEqual(carga.observacoes, 'caminhao ABC1D23')

    def test_data_e_hora_sao_automaticas(self):
        self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 5, 'peso_total': '50.00',
        })
        self.assertIsNotNone(Carga.objects.get().criado_em)

    def test_dono_e_definido_no_servidor(self):
        """O dono nunca vem do formulário — senão seria falsificável."""
        outro = self.criar_usuario('outro')
        self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 5, 'peso_total': '50.00',
            'usuario': outro.pk,  # tentativa de forjar o dono
        })
        self.assertEqual(Carga.objects.get().usuario, self.usuario)

    def test_dados_invalidos_nao_criam_carga(self):
        resposta = self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 0, 'peso_total': '10.00',
        })
        self.assertEqual(resposta.status_code, 200)  # volta com erro no form
        self.assertFalse(Carga.objects.exists())

    def test_mensagem_de_sucesso(self):
        resposta = self.client.post(reverse('cargas:nova'), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 5, 'peso_total': '50.00',
        }, follow=True)
        self.assertContains(resposta, 'sucesso')


class EdicaoTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.carga = self.criar_carga(self.usuario)

    def test_edita_carga(self):
        self.client.post(reverse('cargas:editar', kwargs={'pk': self.carga.pk}), {
            'tipo_maca': 'GOLDEN', 'tamanho': 'GG',
            'quantidade_caixas': 77, 'peso_total': '777.00',
            'observacoes': 'corrigida',
        })
        self.carga.refresh_from_db()
        self.assertEqual(self.carga.tipo_maca, 'GOLDEN')
        self.assertEqual(self.carga.tamanho, 'GG')
        self.assertEqual(self.carga.quantidade_caixas, 77)
        self.assertEqual(self.carga.observacoes, 'corrigida')

    def test_edicao_nao_troca_o_dono(self):
        outro = self.criar_usuario('outro')
        self.client.post(reverse('cargas:editar', kwargs={'pk': self.carga.pk}), {
            'tipo_maca': 'FUJI', 'tamanho': 'M',
            'quantidade_caixas': 10, 'peso_total': '100.00',
            'usuario': outro.pk,
        })
        self.carga.refresh_from_db()
        self.assertEqual(self.carga.usuario, self.usuario)

    def test_detalhe_mostra_a_carga(self):
        resposta = self.client.get(
            reverse('cargas:detalhe', kwargs={'pk': self.carga.pk}))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['carga'], self.carga)


class ExclusaoTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.carga = self.criar_carga(self.usuario)

    def test_excluir_move_para_lixeira_sem_apagar(self):
        self.client.post(reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        self.carga.refresh_from_db()
        self.assertIsNotNone(self.carga.excluido_em)
        self.assertTrue(Carga.objects.filter(pk=self.carga.pk).exists())

    def test_carga_excluida_some_da_lista_e_do_detalhe(self):
        self.client.post(reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        lista = self.client.get(reverse('cargas:lista'))
        detalhe = self.client.get(
            reverse('cargas:detalhe', kwargs={'pk': self.carga.pk}))
        self.assertNotIn(self.carga, lista.context['cargas'])
        self.assertEqual(detalhe.status_code, 404)

    def test_get_apenas_confirma_sem_excluir(self):
        """Abrir a tela de confirmação não pode excluir nada."""
        resposta = self.client.get(
            reverse('cargas:excluir', kwargs={'pk': self.carga.pk}))
        self.carga.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertIsNone(self.carga.excluido_em)
