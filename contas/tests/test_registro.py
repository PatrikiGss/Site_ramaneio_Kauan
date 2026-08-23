"""Criação de contas: restrita a usuários já logados (não há auto-cadastro)."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from contas.models import Perfil

SENHA = 'Romaneio!Teste2026'
SENHA_PROVISORIA = 'Provisoria!2026x'


class RegistroRestritoTests(TestCase):
    def test_anonimo_e_mandado_para_o_login(self):
        resposta = self.client.get(reverse('contas:registrar'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resposta.url)

    def test_anonimo_nao_consegue_criar_conta(self):
        self.client.post(reverse('contas:registrar'), {
            'username': 'invasor',
            'password1': SENHA_PROVISORIA,
            'password2': SENHA_PROVISORIA,
        })
        self.assertFalse(User.objects.filter(username='invasor').exists())


class RegistroPorUsuarioLogadoTests(TestCase):
    def setUp(self):
        self.criador = User.objects.create_user('criador', password=SENHA)
        self.client.force_login(self.criador)

    def registrar(self, username='operador2', senha=SENHA_PROVISORIA, **extra):
        dados = {'username': username, 'password1': senha, 'password2': senha}
        dados.update(extra)
        return self.client.post(reverse('contas:registrar'), dados, follow=True)

    def test_cria_a_conta(self):
        self.registrar()
        self.assertTrue(User.objects.filter(username='operador2').exists())

    def test_criador_permanece_na_propria_sessao(self):
        """Criar conta para terceiro não pode deslogar quem criou."""
        resposta = self.registrar()
        self.assertEqual(resposta.context['user'], self.criador)

    def test_conta_nova_nasce_exigindo_troca_de_senha(self):
        self.registrar()
        novo = User.objects.get(username='operador2')
        self.assertTrue(
            Perfil.objects.filter(usuario=novo,
                                  trocar_senha_no_proximo_acesso=True).exists())

    def test_senha_provisoria_funciona_no_primeiro_login(self):
        self.registrar()
        self.assertTrue(
            self.client.login(username='operador2', password=SENHA_PROVISORIA))

    def test_username_duplicado_e_rejeitado(self):
        self.registrar(username='criador')
        self.assertEqual(User.objects.filter(username='criador').count(), 1)

    def test_senhas_diferentes_sao_rejeitadas(self):
        self.client.post(reverse('contas:registrar'), {
            'username': 'operador3',
            'password1': SENHA_PROVISORIA,
            'password2': 'outra-coisa-2026',
        })
        self.assertFalse(User.objects.filter(username='operador3').exists())

    def test_senha_fraca_e_rejeitada(self):
        self.client.post(reverse('contas:registrar'), {
            'username': 'operador4', 'password1': '123', 'password2': '123',
        })
        self.assertFalse(User.objects.filter(username='operador4').exists())
