"""Listagem: filtros, busca, totais e paginação."""
from decimal import Decimal

from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class FiltrosTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.fuji = self.criar_carga(
            self.usuario, tipo_maca=Carga.TipoMaca.FUJI,
            tamanho=Carga.Tamanho.MEDIA, quantidade_caixas=10,
            peso_total='100.00', observacoes='carga da manha',
            criado_em=self.momento(dias_atras=0))
        self.gala = self.criar_carga(
            self.usuario, tipo_maca=Carga.TipoMaca.GALA,
            tamanho=Carga.Tamanho.GRANDE, quantidade_caixas=20,
            peso_total='200.00', observacoes='carga da tarde',
            criado_em=self.momento(dias_atras=10))

    def cargas_em(self, **filtros):
        resposta = self.client.get(reverse('cargas:lista'), filtros)
        return list(resposta.context['cargas'])

    def test_sem_filtro_lista_tudo(self):
        self.assertCountEqual(self.cargas_em(), [self.fuji, self.gala])

    def test_filtra_por_tipo(self):
        self.assertEqual(self.cargas_em(tipo_maca='FUJI'), [self.fuji])

    def test_filtra_por_tamanho(self):
        self.assertEqual(self.cargas_em(tamanho='G'), [self.gala])

    def test_filtra_por_periodo(self):
        hoje = self.momento().date().isoformat()
        self.assertEqual(self.cargas_em(data_inicio=hoje), [self.fuji])

    def test_filtra_por_data_final(self):
        limite = self.momento(dias_atras=5).date().isoformat()
        self.assertEqual(self.cargas_em(data_fim=limite), [self.gala])

    def test_busca_no_texto_das_observacoes(self):
        self.assertEqual(self.cargas_em(busca='manha'), [self.fuji])

    def test_busca_por_numero_encontra_pelo_id(self):
        self.assertEqual(self.cargas_em(busca=str(self.gala.pk)), [self.gala])

    def test_filtros_combinados(self):
        self.assertEqual(self.cargas_em(tipo_maca='GALA', tamanho='G'), [self.gala])
        self.assertEqual(self.cargas_em(tipo_maca='GALA', tamanho='M'), [])

    def test_lixeira_fica_fora_da_lista(self):
        self.gala.mover_para_lixeira()
        self.assertEqual(self.cargas_em(), [self.fuji])


class TotaisTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.FUJI,
                         quantidade_caixas=10, peso_total='100.00')
        self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.GALA,
                         quantidade_caixas=25, peso_total='250.50')

    def test_totais_somam_o_resultado(self):
        totais = self.client.get(reverse('cargas:lista')).context['totais']
        self.assertEqual(totais['cargas'], 2)
        self.assertEqual(totais['caixas'], 35)
        self.assertEqual(totais['peso'], Decimal('350.50'))

    def test_totais_respeitam_o_filtro(self):
        totais = self.client.get(
            reverse('cargas:lista'), {'tipo_maca': 'FUJI'}).context['totais']
        self.assertEqual(totais['cargas'], 1)
        self.assertEqual(totais['caixas'], 10)

    def test_totais_ignoram_a_lixeira(self):
        Carga.objects.filter(tipo_maca='GALA').first().mover_para_lixeira()
        totais = self.client.get(reverse('cargas:lista')).context['totais']
        self.assertEqual(totais['cargas'], 1)
        self.assertEqual(totais['caixas'], 10)


class PaginacaoTests(RomaneioTestCase):
    """A lista pagina de 15 em 15; os totais continuam somando tudo."""

    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        for _ in range(16):
            self.criar_carga(self.usuario, quantidade_caixas=1, peso_total='1.00')

    def test_primeira_pagina_tem_quinze(self):
        resposta = self.client.get(reverse('cargas:lista'))
        self.assertTrue(resposta.context['is_paginated'])
        self.assertEqual(len(resposta.context['cargas']), 15)
        self.assertEqual(resposta.context['page_obj'].paginator.num_pages, 2)

    def test_segunda_pagina_tem_o_resto(self):
        resposta = self.client.get(reverse('cargas:lista'), {'page': 2})
        self.assertEqual(len(resposta.context['cargas']), 1)

    def test_totais_consideram_todas_as_paginas(self):
        totais = self.client.get(reverse('cargas:lista')).context['totais']
        self.assertEqual(totais['cargas'], 16)
        self.assertEqual(totais['caixas'], 16)

    def test_querystring_preserva_filtros_sem_o_page(self):
        """Sem isso, trocar de página perderia o filtro aplicado."""
        resposta = self.client.get(
            reverse('cargas:lista'), {'tipo_maca': 'FUJI', 'page': 2})
        querystring = resposta.context['querystring']
        self.assertIn('tipo_maca=FUJI', querystring)
        self.assertNotIn('page', querystring)


class ContadorLixeiraTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)

    def test_contador_reflete_itens_na_lixeira(self):
        carga = self.criar_carga(self.usuario)
        self.assertEqual(
            self.client.get(reverse('cargas:lista')).context['total_lixeira'], 0)
        carga.mover_para_lixeira()
        self.assertEqual(
            self.client.get(reverse('cargas:lista')).context['total_lixeira'], 1)
