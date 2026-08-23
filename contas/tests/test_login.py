"""Login e logout."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

SENHA = 'Romaneio!Teste2026'


class LoginTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('operador', password=SENHA)

    def test_login_com_credenciais_validas(self):
        resposta = self.client.post(reverse('contas:entrar'), {
            'username': 'operador', 'password': SENHA,
        }, follow=True)
        self.assertTrue(resposta.context['user'].is_authenticated)

    def test_login_leva_para_a_lista(self):
        resposta = self.client.post(reverse('contas:entrar'), {
            'username': 'operador', 'password': SENHA,
        })
        self.assertRedirects(resposta, reverse('cargas:lista'))

    def test_senha_errada_nao_autentica(self):
        resposta = self.client.post(reverse('contas:entrar'), {
            'username': 'operador', 'password': 'senha-errada',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_usuario_inexistente_nao_autentica(self):
        self.client.post(reverse('contas:entrar'), {
            'username': 'ninguem', 'password': SENHA,
        })
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_pagina_de_login_e_publica(self):
        self.assertEqual(self.client.get(reverse('contas:entrar')).status_code, 200)

    def test_nao_ha_link_publico_de_cadastro(self):
        """Contas só são criadas por quem já está logado."""
        resposta = self.client.get(reverse('contas:entrar'))
        self.assertNotContains(resposta, reverse('contas:registrar'))


class LogoutTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('operador', password=SENHA)
        self.client.force_login(self.usuario)

    def test_logout_por_post(self):
        self.client.post(reverse('contas:sair'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_por_get_nao_desloga(self):
        """Proteção do Django: um link não pode deslogar o usuário."""
        self.client.get(reverse('contas:sair'))
        self.assertIn('_auth_user_id', self.client.session)
