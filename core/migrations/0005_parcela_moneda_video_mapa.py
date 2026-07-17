from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_planpago'),
    ]

    operations = [
        migrations.AddField(
            model_name='parcela',
            name='moneda',
            field=models.CharField(choices=[('CLP', 'CLP ($)'), ('UF', 'UF')], default='CLP', max_length=3),
        ),
        migrations.AddField(
            model_name='parcela',
            name='video_url',
            field=models.URLField(blank=True, help_text='URL de YouTube (ej: https://youtu.be/XXX)'),
        ),
        migrations.AddField(
            model_name='parcela',
            name='mapa_url',
            field=models.URLField(blank=True, help_text='URL de Google Maps (pega el link de compartir)'),
        ),
    ]
