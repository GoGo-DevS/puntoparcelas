# -*- coding: utf-8 -*-
"""El buscador del catalogo, tolerante a como escribe la gente.

Leonardo, 30-10-2026: "si busco cualquier proyecto y no coloco aunque sea un
punto como sale el titulo no lo muestra". El buscador era un `icontains`, que
en Postgres distingue tildes y no perdona nada: "marchigue" no encontraba
"Marchigüe", "panguipuli" no encontraba "Panguipulli".

Ahora el texto se normaliza antes de comparar (minusculas, sin tildes ni
dieresis, sin puntuacion) y cada palabra buscada tiene que aparecer en la
parcela. Si una palabra no aparece tal cual, se acepta la palabra de la
parcela mas parecida (difflib), para los errores de tipeo.

Se filtra en Python y no en SQL porque el catalogo son ~55 parcelas: traerlas
es una consulta, y asi la misma regla vale igual en SQLite (pruebas) y en
Postgres (produccion), sin depender de la extension unaccent.
"""
import difflib
import re
import unicodedata

# Bajo esto dos palabras ya no son "la misma mal escrita": "rapel" y "rupanco"
# dan 0,5; "panguipuli" y "panguipulli", 0,95.
PARECIDO_MINIMO = 0.8
# Palabras de 1-3 letras ("de", "en", "la") no se corrigen: con tan pocas
# letras casi cualquier cosa se parece y se colarian resultados al azar.
LARGO_MINIMO_APROXIMADO = 4


def normalizar(texto):
    """'Marchigüe, O'Higgins' -> 'marchigue o higgins'."""
    texto = unicodedata.normalize('NFKD', texto or '')
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r'[^0-9a-z]+', ' ', texto.lower())
    return ' '.join(texto.split())


def _palabras(texto):
    return set(normalizar(texto).split())


def _calza(palabra, texto_normal, palabras):
    if palabra in texto_normal:
        return True
    if len(palabra) < LARGO_MINIMO_APROXIMADO:
        return False
    return bool(difflib.get_close_matches(palabra, palabras, n=1, cutoff=PARECIDO_MINIMO))


def coincide(q, *campos):
    """True si cada palabra de la busqueda aparece (o casi) en los campos."""
    buscadas = normalizar(q).split()
    if not buscadas:
        return True
    texto_normal = normalizar(' '.join(c or '' for c in campos))
    palabras = list(set(texto_normal.split()))
    return all(_calza(p, texto_normal, palabras) for p in buscadas)


def filtrar(qs, q):
    """El mismo queryset, solo con las parcelas que calzan, en el mismo orden."""
    if not normalizar(q):
        return qs
    ids = [p.pk for p in qs.only('pk', 'nombre', 'sector', 'ciudad', 'descripcion')
           if coincide(q, p.nombre, p.sector, p.ciudad, p.descripcion)]
    return qs.filter(pk__in=ids)
