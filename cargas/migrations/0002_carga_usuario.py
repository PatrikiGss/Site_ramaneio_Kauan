from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cargas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carga',
            name='usuario',
            # default=1 existe só para preencher as cargas que já estavam no banco
            # antes da autenticação (ficam com o superusuário admin, id 1).
            # preserve_default=False garante que novos registros NÃO herdam esse default.
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cargas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='usuário',
            ),
            preserve_default=False,
        ),
    ]
