"""Validações dos formulários de carga."""
from cargas.forms import CargaForm, FiltroCargaForm
from cargas.models import Carga

from .base import RomaneioTestCase


def dados_validos(**sobrescreve):
    dados = {
        'tipo_maca': Carga.TipoMaca.FUJI,
        'tamanho': Carga.Tamanho.MEDIA,
        'quantidade_caixas': 10,
        'peso_total': '180.50',
        'observacoes': '',
    }
    dados.update(sobrescreve)
    return dados


class CargaFormTests(RomaneioTestCase):
    def test_dados_validos_sao_aceitos(self):
        self.assertTrue(CargaForm(data=dados_validos()).is_valid())

    def test_observacoes_sao_opcionais(self):
        form = CargaForm(data=dados_validos(observacoes=''))
        self.assertTrue(form.is_valid())

    def test_quantidade_zero_e_rejeitada(self):
        form = CargaForm(data=dados_validos(quantidade_caixas=0))
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_caixas', form.errors)

    def test_peso_zero_e_rejeitado(self):
        form = CargaForm(data=dados_validos(peso_total='0'))
        self.assertFalse(form.is_valid())
        self.assertIn('peso_total', form.errors)

    def test_peso_negativo_e_rejeitado(self):
        form = CargaForm(data=dados_validos(peso_total='-5'))
        self.assertFalse(form.is_valid())
        self.assertIn('peso_total', form.errors)

    def test_campos_obrigatorios(self):
        form = CargaForm(data={})
        self.assertFalse(form.is_valid())
        for campo in ('tipo_maca', 'tamanho', 'quantidade_caixas', 'peso_total'):
            self.assertIn(campo, form.errors)

    def test_tipo_fora_da_lista_e_rejeitado(self):
        form = CargaForm(data=dados_validos(tipo_maca='PINK_LADY'))
        self.assertFalse(form.is_valid())
        self.assertIn('tipo_maca', form.errors)


class OpcoesCadastroTests(RomaneioTestCase):
    """Trava as opções combinadas com o cliente contra mudanças acidentais."""

    def test_tipos_de_maca_esperados(self):
        rotulos = [rotulo for _, rotulo in Carga.TipoMaca.choices]
        self.assertEqual(rotulos, ['Fuji', 'Gala', 'Mishima', 'Golden', 'Outra'])

    def test_tamanhos_esperados(self):
        rotulos = [rotulo for _, rotulo in Carga.Tamanho.choices]
        self.assertEqual(rotulos, ['Pequena', 'Média', 'Grande', 'Extra grande'])


class FiltroCargaFormTests(RomaneioTestCase):
    def test_filtro_vazio_e_valido(self):
        """Sem nenhum filtro a lista deve funcionar normalmente."""
        self.assertTrue(FiltroCargaForm(data={}).is_valid())

    def test_data_invalida_e_rejeitada(self):
        form = FiltroCargaForm(data={'data_inicio': '31/02/2026'})
        self.assertFalse(form.is_valid())
