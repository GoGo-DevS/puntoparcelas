from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_add_mapa_embed_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcela',
            name='geo_pdf',
            field=models.FileField(
                blank=True,
                help_text='Plano GEO en PDF',
                storage=core.models._geo_pdf_storage,
                upload_to='geo/',
            ),
        ),
    ]
