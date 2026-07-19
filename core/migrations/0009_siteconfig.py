from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0008_alter_parcela_geo_pdf_storage')]

    operations = [
        migrations.CreateModel(
            name='SiteConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto_contacto', models.ImageField(blank=True, help_text='Foto de Leonardo en /contacto/', upload_to='config/')),
            ],
            options={'verbose_name': 'Configuración del sitio'},
        ),
    ]
