from django.conf import settings
from django.db import models
from django.urls import reverse


class Carga(models.Model):
    class TipoMaca(models.TextChoices):
        GALA = 'GALA', 'Gala'
        FUJI = 'FUJI', 'Fuji'
        EVA = 'EVA', 'Eva'
        PINK_LADY = 'PINK_LADY', 'Pink Lady'
        CRIPPS_PINK = 'CRIPPS_PINK', 'Cripps Pink'
        GRANNY_SMITH = 'GRANNY_SMITH', 'Granny Smith'
        RED_DELICIOUS = 'RED_DELICIOUS', 'Red Delicious'
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

    class Meta:
        verbose_name = 'carga'
        verbose_name_plural = 'cargas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Carga #{self.pk} - {self.get_tipo_maca_display()} ({self.criado_em:%d/%m/%Y %H:%M})'

    def get_absolute_url(self):
        return reverse('cargas:detalhe', kwargs={'pk': self.pk})
