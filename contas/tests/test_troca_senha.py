"""Troca de senha e o bloqueio de primeiro acesso (middleware)."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from contas.models import Perfil

SENHA_PROVISORIA = 'Provisoria!2026x'
SENHA_NOVA = 'MinhaNovaSenha!2026'


class PrimeiroAcessoTests(TestCase):
    """Quem está com senha provisória só navega depois de trocá-la."""

    def setUp(self):
        self.usuario = User.objects.create_user('novato', password=SENHA_PROVISORIA)
        Perfil.objects.create(usuario=self.usuario, trocar_senha_no_proximo_acesso=True)
        self.client.force_login(self.usuario)

    def test_navegacao_e_redirecionada_para_a_troca(self):
        for rota in (reverse('cargas:lista'), reverse('cargas:nova'),
                     reverse('cargas:resumo')):
            with self.subTest(rota=rota):
                resposta = self.client.get(rota)
                self.assertRedirects(resposta, reverse('contas:trocar_senha'))

    def test_tela_de_troca_fica_acessivel(self):
        resposta = self.client.get(reverse('contas:trocar_senha'))
        self.assertEqual(resposta.status_code, 200)

    def test_logout_continua_liberado(self):
        """Senão o usuário ficaria preso sem conseguir sair."""
        self.client.post(reverse('contas:sair'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_trocar_senha_libera_a_navegacao(self):
        self.client.post(reverse('contas:trocar_senha'), {
            'old_password': SENHA_PROVISORIA,
            'new_password1': SENHA_NOVA,
            'new_password2': SENHA_NOVA,
        })
        self.assertFalse(
            Perfil.objects.get(usuario=self.usuario).trocar_senha_no_proximo_acesso)
        self.assertEqual(self.client.get(reverse('cargas:lista')).status_code, 200)

    def test_usuario_segue_logado_apos_trocar(self):
        self.client.post(reverse('contas:trocar_senha'), {
            'old_password': SENHA_PROVISORIA,
            'new_password1': SENHA_NOVA,
            'new_password2': SENHA_NOVA,
        })
        self.assertIn('_auth_user_id', self.client.session)

    def test_senha_nova_passa_a_valer(self):
        self.client.post(reverse('contas:trocar_senha'), {
            'old_password': SENHA_PROVISORIA,
            'new_password1': SENHA_NOVA,
            'new_password2': SENHA_NOVA,
        })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(SENHA_NOVA))
        self.assertFalse(self.usuario.check_password(SENHA_PROVISORIA))


class TrocaSenhaTests(TestCase):
    """Troca de senha comum, sem a flag de primeiro acesso."""

    def setUp(self):
        self.usuario = User.objects.create_user('operador', password=SENHA_PROVISORIA)
        self.client.force_login(self.usuario)

    def test_usuario_sem_perfil_navega_normalmente(self):
        self.assertEqual(self.client.get(reverse('cargas:lista')).status_code, 200)

    def test_senha_antiga_errada_e_rejeitada(self):
        self.client.post(reverse('contas:trocar_senha'), {
            'old_password': 'errada',
            'new_password1': SENHA_NOVA,
            'new_password2': SENHA_NOVA,
        })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(SENHA_PROVISORIA))

    def test_confirmacao_divergente_e_rejeitada(self):
        self.client.post(reverse('contas:trocar_senha'), {
            'old_password': SENHA_PROVISORIA,
            'new_password1': SENHA_NOVA,
            'new_password2': 'outra-diferente-2026',
        })
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password(SENHA_PROVISORIA))

    def test_anonimo_nao_acessa_troca_de_senha(self):
        self.client.logout()
        resposta = self.client.get(reverse('contas:trocar_senha'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('contas:entrar'), resposta.url)
