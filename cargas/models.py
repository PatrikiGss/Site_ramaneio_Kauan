from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Carga(models.Model):
    class TipoMaca(models.TextChoices):
        FUJI = 'FUJI', 'Fuji'
        GALA = 'GALA', 'Gala'
        MISHIMA = 'MISHIMA', 'Mishima'
        GOLDEN = 'GOLDEN', 'Golden'
        OUTRA = 'OUTRA', 'Outra'

    class Tamanho(models.TextChoices):
        PEQUENA = 'P', 'Pequena'
        MEDIA = 'M', 'Média'
        GRANDE = 'G', 'Grande'
        EXTRA_GRANDE = 'GG', 'Extra grande'

    # Dono do registro: todo o isolamento de dados do sistema parte deste campo.
    # As views filtram sempre por ele, então um usuário nunca enxerga cargas de outro.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário',
        on_delete=models.CASCADE,
        related_name='cargas',
    )
    criado_em = models.DateTimeField('data e hora do cadastro', auto_now_add=True)
    atualizado_em = models.DateTimeField('última atualização', auto_now=True)
    tipo_maca = models.CharField('tipo da maçã', max_length=20, choices=TipoMaca.choices)
    tamanho = models.CharField('tamanho da maçã', max_length=2, choices=Tamanho.choices)
    quantidade_caixas = models.PositiveIntegerField('quantidade de caixas')
    peso_total = models.DecimalField('peso total (kg)', max_digits=10, decimal_places=2)
    observacoes = models.TextField('observações', blank=True)
    # Lixeira (exclusão reversível): quando preenchido, a carga está "na lixeira"
    # e some das telas normais; NULL = carga ativa. As views filtram por este
    # campo (ativas x lixeira). Ver mover_para_lixeira() / restaurar().
    excluido_em = models.DateTimeField('excluído em', null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = 'carga'
        verbose_name_plural = 'cargas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Carga #{self.pk} - {self.get_tipo_maca_display()} ({self.criado_em:%d/%m/%Y %H:%M})'

    def get_absolute_url(self):
        return reverse('cargas:detalhe', kwargs={'pk': self.pk})

    @property
    def na_lixeira(self):
        return self.excluido_em is not None

    def mover_para_lixeira(self):
        self.excluido_em = timezone.now()
        # atualizado_em é auto_now: precisa entrar no update_fields para atualizar
        self.save(update_fields=['excluido_em', 'atualizado_em'])

    def restaurar(self):
        self.excluido_em = None
        self.save(update_fields=['excluido_em', 'atualizado_em'])
