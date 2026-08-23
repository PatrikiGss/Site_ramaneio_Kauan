"""Resumo do período (fechamento): totais agrupados por tipo, tamanho e dia."""
from decimal import Decimal

from django.urls import reverse

from cargas.models import Carga

from .base import RomaneioTestCase


class ResumoTests(RomaneioTestCase):
    def setUp(self):
        self.usuario = self.criar_usuario()
        self.client.force_login(self.usuario)
        self.hoje = self.momento().date()
        # Hoje: 2 Fuji (uma Média, uma Grande) + 1 Gala Média
        self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.FUJI,
                         tamanho=Carga.Tamanho.MEDIA, quantidade_caixas=10,
                         peso_total='100.00', criado_em=self.momento())
        self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.FUJI,
                         tamanho=Carga.Tamanho.GRANDE, quantidade_caixas=20,
                         peso_total='200.00', criado_em=self.momento())
        self.criar_carga(self.usuario, tipo_maca=Carga.TipoMaca.GALA,
                         tamanho=Carga.Tamanho.MEDIA, quantidade_caixas=5,
                         peso_total='50.00', criado_em=self.momento())
        # Fora do período padrão (10 dias atrás)
        self.antiga = self.criar_carga(
            self.usuario, tipo_maca=Carga.TipoMaca.GOLDEN,
            quantidade_caixas=999, peso_total='999.00',
            criado_em=self.momento(dias_atras=10))

    def resumo(self, **parametros):
        return self.client.get(reverse('cargas:resumo'), parametros)

    def por_rotulo(self, linhas):
        return {linha['label']: linha for linha in linhas}

    def test_periodo_padrao_e_hoje(self):
        contexto = self.resumo().context
        self.assertEqual(contexto['inicio'], self.hoje)
        self.assertEqual(contexto['fim'], self.hoje)
        self.assertEqual(contexto['geral']['n'], 3)

    def test_totais_gerais_do_periodo(self):
        geral = self.resumo().context['geral']
        self.assertEqual(geral['caixas'], 35)
        self.assertEqual(geral['peso'], Decimal('350.00'))

    def test_agrupamento_por_tipo(self):
        tipos = self.por_rotulo(self.resumo().context['por_tipo'])
        self.assertEqual(tipos['Fuji']['n'], 2)
        self.assertEqual(tipos['Fuji']['caixas'], 30)
        self.assertEqual(tipos['Gala']['caixas'], 5)
        self.assertNotIn('Golden', tipos)

    def test_agrupamento_por_tamanho(self):
        tamanhos = self.por_rotulo(self.resumo().context['por_tamanho'])
        self.assertEqual(tamanhos['Média']['n'], 2)
        self.assertEqual(tamanhos['Média']['caixas'], 15)
        self.assertEqual(tamanhos['Grande']['caixas'], 20)

    def test_agrupamento_por_dia(self):
        por_dia = self.resumo().context['por_dia']
        self.assertEqual(len(por_dia), 1)
        self.assertEqual(por_dia[0]['dia'], self.hoje)
        self.assertEqual(por_dia[0]['caixas'], 35)

    def test_periodo_maior_inclui_registros_antigos(self):
        inicio = self.momento(dias_atras=30).date().isoformat()
        contexto = self.resumo(data_inicio=inicio,
                               data_fim=self.hoje.isoformat()).context
        self.assertEqual(contexto['geral']['n'], 4)
        self.assertEqual(len(contexto['por_dia']), 2)

    def test_lixeira_fica_fora_do_resumo(self):
        Carga.objects.filter(tipo_maca='GALA').first().mover_para_lixeira()
        geral = self.resumo().context['geral']
        self.assertEqual(geral['n'], 2)
        self.assertEqual(geral['caixas'], 30)

    def test_datas_invertidas_sao_corrigidas(self):
        """Se o usuário inverte De/Até, o sistema entende em vez de zerar."""
        contexto = self.resumo(
            data_inicio=self.hoje.isoformat(),
            data_fim=self.momento(dias_atras=30).date().isoformat()).context
        self.assertEqual(contexto['inicio'], self.momento(dias_atras=30).date())
        self.assertEqual(contexto['fim'], self.hoje)
        self.assertEqual(contexto['geral']['n'], 4)

    def test_data_invalida_cai_no_padrao(self):
        contexto = self.resumo(data_inicio='banana').context
        self.assertEqual(contexto['inicio'], self.hoje)

    def test_periodo_sem_cargas_fica_zerado(self):
        contexto = self.resumo(data_inicio='2000-01-01', data_fim='2000-01-02').context
        self.assertEqual(contexto['geral']['n'], 0)
        self.assertIsNone(contexto['geral']['caixas'])
        self.assertEqual(list(contexto['por_tipo']), [])

    def test_atalhos_de_periodo_no_contexto(self):
        contexto = self.resumo().context
        self.assertEqual(contexto['hoje'], self.hoje)
        self.assertEqual(contexto['inicio_mes'], self.hoje.replace(day=1))
