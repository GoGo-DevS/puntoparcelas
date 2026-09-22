"""Ajuste de ciudades de Jorge Urzua (22-09-2026, filas en gris de la hoja
"01 Mapping parcelas"): 12 parcelas cuya ciudad no calzaba con su title/H1.

Solo cambia un campo si TODAVIA tiene el valor que dejo aplicar_seo_jorge el
04-09. Si Leonardo lo edito desde su panel, lo respeta y no lo pisa (asi quedo
fuera Hacienda don Danilo, que el ya corrigio a mano). Reversible.
"""
from django.db import migrations

CAMBIOS = [
    {
        "slug": "brisas-del-arrayan",
        "old_title": "Parcela Brisas del Arrayán en Litueche, O'Higgins | Punto Parcelas",
        "old_h1": "Parcela Brisas del Arrayán en Litueche, O'Higgins",
        "old_ciudad": "Litueche",
        "title": "Parcela Brisas del Arrayán en Pichilemu, O'Higgins | Punto Parcelas",
        "h1": "Parcela Brisas del Arrayán en Pichilemu, O'Higgins",
        "ciudad": "Pichilemu"
    },
    {
        "slug": "fundo-la-puntilla",
        "old_title": "Parcela Fundo la Puntilla en Marchigüe, O'Higgins | Punto Parcelas",
        "old_h1": "Parcela Fundo la Puntilla en Marchigüe, O'Higgins",
        "old_ciudad": "Marchigüe",
        "title": "Parcela Fundo la Puntilla en La Estrella, O'Higgins | Punto Parcelas",
        "h1": "Parcela Fundo la Puntilla en La Estrella, O'Higgins",
        "ciudad": "La Estrella"
    },
    {
        "slug": "fundo-la-quirigua",
        "old_title": "Parcela Fundo la Quirigua en San Javier, Maule | Punto Parcelas",
        "old_h1": "Parcela Fundo la Quirigua en San Javier, Maule",
        "old_ciudad": "San Javier",
        "title": "Parcela Fundo la Quirigua en Lago Vichuquén, Maule | Punto Parcelas",
        "h1": "Parcela Fundo la Quirigua en Lago Vichuquén, Maule",
        "ciudad": "Lago Vichuquén"
    },
    {
        "slug": "fundo-santa-rosa",
        "old_title": "Parcela Fundo Santa Rosa de Bucalemu, Valparaíso | Punto Parcelas",
        "old_h1": "Parcela Fundo Santa Rosa de Bucalemu, Valparaíso",
        "old_ciudad": "Bucalemu",
        "title": "Parcela Fundo Santa Rosa de Santo Domingo, Valparaíso | Punto Parcelas",
        "h1": "Parcela Fundo Santa Rosa de Santo Domingo, Valparaíso",
        "ciudad": "Santo Domingo"
    },
    {
        "slug": "hacienda-don-bastian-parcela-i381-3",
        "old_title": "Parcela Hacienda don Bastian en Litueche, O'Higgins | Punto Parcelas",
        "old_h1": "Parcela Hacienda don Bastian en Litueche, O'Higgins",
        "old_ciudad": "Litueche",
        "title": "Parcela Hacienda don Bastian en La Estrella, O'Higgins | Punto Parcelas",
        "h1": "Parcela Hacienda don Bastian en La Estrella, O'Higgins",
        "ciudad": "La Estrella"
    },
    {
        "slug": "hacienda-don-bastian",
        "old_title": "Parcela Hacienda Don Bastián en Litueche, O'Higgins | Punto Parcelas",
        "old_h1": "Parcela Hacienda Don Bastián en Litueche, O'Higgins",
        "old_ciudad": "Litueche",
        "title": "Parcela Hacienda Don Bastián en La Estrella, O'Higgins | Punto Parcelas",
        "h1": "Parcela Hacienda Don Bastián en La Estrella, O'Higgins",
        "ciudad": "La Estrella"
    },
    {
        "slug": "hacienda-don-felix",
        "old_title": "Parcela Hacienda Don Felix en Algarrobo, Valparaíso | Punto Parcelas",
        "old_h1": "Parcela Hacienda Don Felix en Algarrobo, Valparaíso",
        "old_ciudad": "Algarrobo",
        "title": "Parcela Hacienda Don Felix en Santo Domingo, Valparaíso | Punto Parcelas",
        "h1": "Parcela Hacienda Don Felix en Santo Domingo, Valparaíso",
        "ciudad": "Santo Domingo"
    },
    {
        "slug": "parque-algarrobo",
        "old_title": "Parcela Parque Algarrobo en Algarrobo, Valparaíso | Punto Parcelas",
        "old_h1": "Parcela Parque Algarrobo en Algarrobo, Valparaíso",
        "old_ciudad": "Algarrobo",
        "title": "Parcela Parque Algarrobo en Santo Domingo, Valparaíso | Punto Parcelas",
        "h1": "Parcela Parque Algarrobo en Santo Domingo, Valparaíso",
        "ciudad": "Santo Domingo"
    },
    {
        "slug": "praderas-de-cauquenes",
        "old_title": "Parcela Praderas de Cauquenes en Talca, Maule | Punto Parcelas",
        "old_h1": "Parcela Praderas de Cauquenes en Talca, Maule",
        "old_ciudad": "Talca",
        "title": "Parcela Praderas de Cauquenes en Cauquenes, Maule | Punto Parcelas",
        "h1": "Parcela Praderas de Cauquenes en Cauquenes, Maule",
        "ciudad": "Cauquenes"
    },
    {
        "slug": "proyecto-arbol-grande-2",
        "old_title": "Parcela Proyecto Arbol Grande en Cauquenes, Maule | Punto Parcelas",
        "old_h1": "Parcela Proyecto Arbol Grande en Cauquenes, Maule",
        "old_ciudad": "Cauquenes",
        "title": "Parcela Proyecto Arbol Grande en Curepto, Maule | Punto Parcelas",
        "h1": "Parcela Proyecto Arbol Grande en Curepto, Maule",
        "ciudad": "Curepto"
    },
    {
        "slug": "proyecto-don-guillermo",
        "old_title": "Parcela Proyecto Don Guillermo en Longaví, Maule | Punto Parcelas",
        "old_h1": "Parcela Proyecto Don Guillermo en Longaví, Maule",
        "old_ciudad": "Longaví",
        "title": "Parcela Proyecto Don Guillermo en Hualañe, Maule | Punto Parcelas",
        "h1": "Parcela Proyecto Don Guillermo en Hualañe, Maule",
        "ciudad": "Hualañe"
    },
    {
        "slug": "proyecto-santa-sofia-2",
        "old_title": "Parcela Proyecto Santa Sofia en Cauquenes, Maule | Punto Parcelas",
        "old_h1": "Parcela Proyecto Santa Sofia en Cauquenes, Maule",
        "old_ciudad": "Cauquenes",
        "title": "Parcela Proyecto Santa Sofia en Curico, Maule | Punto Parcelas",
        "h1": "Parcela Proyecto Santa Sofia en Curico, Maule",
        "ciudad": "Curico"
    }
]


def aplicar(apps, schema_editor, reverso=False):
    Parcela = apps.get_model('core', 'Parcela')
    for c in CAMBIOS:
        p = Parcela.objects.filter(slug=c['slug']).first()
        if not p:
            continue
        campos = []
        for campo, viejo, nuevo in (
            ('seo_title', c['title'] if reverso else c['old_title'], c['old_title'] if reverso else c['title']),
            ('seo_h1', c['h1'] if reverso else c['old_h1'], c['old_h1'] if reverso else c['h1']),
            ('ciudad', c['ciudad'] if reverso else c['old_ciudad'], c['old_ciudad'] if reverso else c['ciudad']),
        ):
            if getattr(p, campo) == viejo:
                setattr(p, campo, nuevo)
                campos.append(campo)
        if campos:
            p.save(update_fields=campos)


def revertir(apps, schema_editor):
    aplicar(apps, schema_editor, reverso=True)


class Migration(migrations.Migration):
    dependencies = [('core', '0013_parcela_ciudad_parcela_seo_h1_parcela_seo_title')]
    operations = [migrations.RunPython(aplicar, revertir)]
