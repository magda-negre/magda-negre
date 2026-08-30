#!/usr/bin/env python3
"""Genera la capa estática de la web a partir de content.json.

Escribe una página HTML real por cada escrito (obra/<slug>.html), un índice
completo (biblioteca.html) y el sitemap.xml. Todo el contenido queda dentro del
HTML, sin depender de JavaScript, que es lo que necesitan los buscadores.

La web interactiva (index.html y las tres secciones .dc.html) no se toca: el
modo edición y la publicación desde el navegador siguen funcionando igual.

Uso:  python3 build.py
"""

import json
import os
import re
import shutil
import unicodedata
from html import escape

BASE = "https://magda-negre.github.io/magda-negre"
ROOT = os.path.dirname(os.path.abspath(__file__))
OBRA_DIR = os.path.join(ROOT, "obra")
PLACEHOLDER = "Escribe aquí el texto."

# clave, nombre, subtítulo, archivo de la sección, texto del enlace de vuelta
SECCIONES = [
    ("novelas", "Novelas", "Narración larga", "Novelas.dc.html", "Todas las novelas"),
    ("cuentos", "Cuentos", "Narrativa breve", "Cuentos.dc.html", "Todos los cuentos"),
    ("misterio", "Relatos de misterio", "Historias de intriga y misterio",
     "Misterio.dc.html", "Todos los relatos"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500'
    '&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">'
)

CSS = """
  html,body{margin:0;padding:0}
  body{background:#f6f1e7;color:#2b2420;font-family:'EB Garamond',Georgia,serif;
       -webkit-font-smoothing:antialiased;line-height:1.6}
  a{color:#a15a3a}
  a:hover{color:#7d4229}
  .nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;
       gap:24px;flex-wrap:wrap;padding:22px 48px;background:rgba(246,241,231,0.92);
       backdrop-filter:blur(6px);border-bottom:1px solid rgba(43,36,32,0.14)}
  .nav .marca{font-style:italic;font-size:21px;color:#2b2420;text-decoration:none}
  .nav .enlaces{display:flex;align-items:center;gap:30px;flex-wrap:wrap}
  .nav .enlaces a{font-family:'Jost',sans-serif;font-size:12.5px;text-transform:uppercase;
                  letter-spacing:0.09em;color:#8a7d6c;text-decoration:none}
  .wrap{max-width:780px;margin:0 auto;padding:70px 48px 130px}
  .wrap-ancho{max-width:1120px;margin:0 auto;padding:70px 48px 130px}
  .volver{display:inline-block;margin-bottom:44px;font-family:'Jost',sans-serif;font-size:12px;
          text-transform:uppercase;letter-spacing:0.09em;color:#8a7d6c;text-decoration:none}
  .kicker{font-family:'Jost',sans-serif;font-size:13px;text-transform:uppercase;
          letter-spacing:0.1em;color:#a15a3a;margin-bottom:14px}
  h1{font-family:'EB Garamond',serif;font-weight:600;font-size:42px;line-height:1.15;margin:0 0 36px}
  h2{font-family:'EB Garamond',serif;font-weight:500;font-style:italic;font-size:34px;margin:0 0 6px}
  .sub{font-size:17px;color:#8a7d6c;margin:0 0 4px}
  .cuenta{font-family:'Jost',sans-serif;font-size:12.5px;letter-spacing:0.06em;color:#8a7d6c}
  .texto p{font-size:19px;line-height:1.8;color:#4a4038;margin:0 0 1.5em;
           white-space:pre-line;text-wrap:pretty}
  .rejilla{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:24px;margin:36px 0 0}
  .ficha{display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:26px;
         border:1px solid rgba(43,36,32,0.14);border-top:2px solid #a15a3a;border-radius:2px;
         background:#efe6d6;color:#2b2420;text-decoration:none}
  .ficha:hover{background:#e9ded0;color:#2b2420}
  .ficha .t{font-size:24px;line-height:1.25;font-weight:600}
  .ficha .m{font-family:'Jost',sans-serif;font-size:11.5px;text-transform:uppercase;
            letter-spacing:0.09em;color:#a15a3a;margin-top:22px}
  .seccion{margin:0 0 80px}
  .paso{display:flex;justify-content:space-between;gap:24px;flex-wrap:wrap;
        margin-top:80px;padding-top:32px;border-top:1px solid rgba(43,36,32,0.14)}
  .paso a{font-family:'Jost',sans-serif;font-size:12px;text-transform:uppercase;
          letter-spacing:0.09em;text-decoration:none;max-width:46%}
  .galeria{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:28px;margin-top:36px}
  .galeria figure{margin:0}
  .galeria img{width:100%;height:auto;display:block;border:1px solid rgba(43,36,32,0.14)}
  .galeria figcaption{font-family:'Jost',sans-serif;font-size:12.5px;letter-spacing:0.04em;
                      color:#8a7d6c;margin-top:10px}
  .bio{font-size:19px;line-height:1.8;color:#4a4038;white-space:pre-line;max-width:720px}
  .pie{max-width:1120px;margin:0 auto;padding:0 48px 90px;font-family:'Jost',sans-serif;
       font-size:12.5px;letter-spacing:0.04em;color:#8a7d6c}
  @media (max-width:640px){
    .nav{padding:18px 22px;gap:16px}
    .nav .enlaces{gap:18px}
    .wrap,.wrap-ancho{padding:48px 22px 90px}
    .pie{padding:0 22px 60px}
    h1{font-size:32px}
    h2{font-size:27px}
    .texto p{font-size:18px}
  }
"""


def slugify(texto):
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "sin-titulo"


def limpio(texto):
    """Texto plano en una línea, para descripciones."""
    return re.sub(r"\s+", " ", texto or "").strip()


def es_placeholder(item):
    return limpio(item.get("text", "")) in ("", PLACEHOLDER)


def anyo_del_titulo(titulo):
    """La fecha real está al final del título ('El premio  1990'); el campo
    `year` guarda la fecha de subida, así que no sirve."""
    m = re.search(r"\b(1[89]\d{2}|20\d{2})\s*$", titulo.strip())
    return m.group(1) if m else None


def parrafos(texto):
    """Divide en párrafos por líneas en blanco. No reúne líneas dentro de un
    párrafo: el texto viene con saltos duros de Word y unirlos podría alterar
    la prosa. Se conservan con white-space:pre-line, igual que en la web."""
    bloques = re.split(r"\n\s*\n", (texto or "").strip())
    return [b.strip() for b in bloques if b.strip()]


def nav(activa=None, prefijo="./"):
    items = [
        ("Biografía", prefijo + "index.html#bio"),
        ("Novelas", prefijo + "Novelas.dc.html"),
        ("Cuentos", prefijo + "Cuentos.dc.html"),
        ("Relatos de misterio", prefijo + "Misterio.dc.html"),
        ("Arte", prefijo + "index.html#arte"),
        ("Contacto", prefijo + "index.html#contacto"),
    ]
    enlaces = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' style="color:#a15a3a"' if n == activa else "", n)
        for n, h in items
    )
    return (
        '<nav class="nav"><a class="marca" href="%sindex.html">Magda Negre</a>'
        '<div class="enlaces">%s</div></nav>' % (prefijo, enlaces)
    )


def documento(titulo, descripcion, canonical, cuerpo, jsonld=None, noindex=False):
    partes = [
        "<!DOCTYPE html>",
        '<html lang="es">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % escape(titulo),
        '<meta name="description" content="%s">' % escape(descripcion),
        '<link rel="canonical" href="%s">' % escape(canonical),
        '<meta name="author" content="Magda Negre">',
    ]
    if noindex:
        partes.append('<meta name="robots" content="noindex,follow">')
    partes += [
        '<meta property="og:type" content="article">',
        '<meta property="og:locale" content="es_ES">',
        '<meta property="og:site_name" content="Magda Negre">',
        '<meta property="og:title" content="%s">' % escape(titulo),
        '<meta property="og:description" content="%s">' % escape(descripcion),
        '<meta property="og:url" content="%s">' % escape(canonical),
        '<meta name="twitter:card" content="summary">',
        FONTS,
        "<style>%s</style>" % CSS,
    ]
    if jsonld:
        partes.append(
            '<script type="application/ld+json">%s</script>'
            % json.dumps(jsonld, ensure_ascii=False, indent=2)
        )
    partes += ["</head>", "<body>", cuerpo, "</body>", "</html>"]
    return "\n".join(partes) + "\n"


def autor_jsonld(datos):
    return {
        "@type": "Person",
        "name": datos["author"]["name"],
        # Publica sus libros como «Magda Negre Chauveau»: se lo decimos a
        # Google para que asocie la web con las fichas de sus obras.
        "alternateName": "Magda Negre Chauveau",
        "url": BASE + "/",
    }


def construir():
    with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
        datos = json.load(f)

    # --- asignar un slug único a cada escrito -----------------------------
    usados = set()
    fichas = {}
    for clave, _, _, _, _ in SECCIONES:
        lista = []
        for item in datos.get(clave, []):
            base = slugify(item.get("title", ""))
            slug, n = base, 2
            while slug in usados:
                slug, n = "%s-%d" % (base, n), n + 1
            usados.add(slug)
            lista.append(
                {
                    "slug": slug,
                    "title": limpio(item.get("title", "")) or "Sin título",
                    "text": item.get("text", ""),
                    "vacio": es_placeholder(item),
                    "url": "%s/obra/%s.html" % (BASE, slug),
                }
            )
        fichas[clave] = lista

    if os.path.isdir(OBRA_DIR):
        shutil.rmtree(OBRA_DIR)
    os.makedirs(OBRA_DIR)

    indexables = []

    # --- una página por escrito ------------------------------------------
    for clave, nombre, _, archivo, volver in SECCIONES:
        lista = fichas[clave]
        for i, obra in enumerate(lista):
            anterior = lista[i - 1] if i > 0 else None
            siguiente = lista[i + 1] if i + 1 < len(lista) else None

            cuerpo_txt = "".join(
                "<p>%s</p>" % escape(p) for p in parrafos(obra["text"])
            ) or "<p><em>Texto pendiente de publicar.</em></p>"

            resumen = limpio(obra["text"])
            if obra["vacio"]:
                descripcion = "%s, de la sección %s de Magda Negre, escritora y escultora de Barcelona." % (
                    obra["title"],
                    nombre.lower(),
                )
            else:
                descripcion = resumen[:155].rsplit(" ", 1)[0] + "…"

            anyo = anyo_del_titulo(obra["title"])
            ld = {
                "@context": "https://schema.org",
                "@type": "ShortStory" if clave != "novelas" else "Book",
                "name": obra["title"],
                "headline": obra["title"],
                "inLanguage": "es",
                "author": autor_jsonld(datos),
                "url": obra["url"],
                "isPartOf": {
                    "@type": "CreativeWorkSeries",
                    "name": nombre,
                    "url": "%s/%s" % (BASE, archivo),
                },
            }
            if anyo:
                ld["datePublished"] = anyo
            if not obra["vacio"]:
                ld["description"] = descripcion

            paso = []
            if anterior:
                paso.append('<a href="./%s.html">← %s</a>' % (anterior["slug"], escape(anterior["title"])))
            else:
                paso.append("<span></span>")
            if siguiente:
                paso.append(
                    '<a href="./%s.html" style="text-align:right">%s →</a>'
                    % (siguiente["slug"], escape(siguiente["title"]))
                )
            paso_html = '<div class="paso">%s</div>' % "".join(paso)

            cuerpo = "".join(
                [
                    nav(nombre, prefijo="../"),
                    '<main class="wrap">',
                    '<a class="volver" href="../%s">← %s</a>' % (archivo, escape(volver)),
                    '<div class="kicker">%s</div>' % escape(nombre),
                    "<h1>%s</h1>" % escape(obra["title"]),
                    '<div class="texto">%s</div>' % cuerpo_txt,
                    paso_html,
                    "</main>",
                    '<footer class="pie">'
                    '<a href="../biblioteca.html">Índice completo de la obra</a> · '
                    '<a href="../index.html">Magda Negre</a></footer>',
                ]
            )

            with open(os.path.join(OBRA_DIR, obra["slug"] + ".html"), "w", encoding="utf-8") as f:
                f.write(
                    documento(
                        "%s — Magda Negre" % obra["title"],
                        descripcion,
                        obra["url"],
                        cuerpo,
                        jsonld=ld,
                        # Los textos que aún son un marcador de posición no se
                        # indexan: páginas vacías y casi idénticas perjudican.
                        noindex=obra["vacio"],
                    )
                )
            if not obra["vacio"]:
                indexables.append(obra["url"])

    # --- índice completo estático ----------------------------------------
    partes = [
        nav(),
        '<main class="wrap-ancho">',
        '<div class="kicker">Índice</div>',
        "<h1>Toda la obra de Magda Negre</h1>",
        '<div class="bio">%s</div>' % escape(limpio(datos["author"]["bio"])),
    ]
    for clave, nombre, subtitulo, archivo, _ in SECCIONES:
        lista = fichas[clave]
        tarjetas = "".join(
            '<a class="ficha" href="./obra/%s.html"><span class="t">%s</span>'
            '<span class="m">Leer →</span></a>' % (o["slug"], escape(o["title"]))
            for o in lista
        )
        partes.append(
            '<section class="seccion"><h2><a href="./%s" style="color:inherit;text-decoration:none">%s</a></h2>'
            '<p class="sub">%s</p><div class="cuenta">%d</div>'
            '<div class="rejilla">%s</div></section>'
            % (archivo, escape(nombre), escape(subtitulo), len(lista), tarjetas)
        )

    arte = datos.get("arte", [])
    if arte:
        figuras = "".join(
            '<figure><img src="./%s" alt="%s" loading="lazy" width="600" height="800">'
            "<figcaption>%s</figcaption></figure>"
            % (
                escape(o["image"]),
                escape(limpio(o.get("caption", "")) or "Obra de Magda Negre"),
                escape(limpio(o.get("caption", "")) or "Obra de Magda Negre"),
            )
            for o in arte
            if o.get("image")
        )
        partes.append(
            '<section class="seccion"><h2>Arte</h2>'
            '<p class="sub">Principalmente escultura</p>'
            '<div class="galeria">%s</div></section>' % figuras
        )

    partes += [
        "</main>",
        '<footer class="pie"><a href="./index.html">Volver a la portada</a> · '
        '<a href="mailto:%s">%s</a></footer>' % (escape(datos["author"]["email"]), escape(datos["author"]["email"])),
    ]

    with open(os.path.join(ROOT, "biblioteca.html"), "w", encoding="utf-8") as f:
        f.write(
            documento(
                "Índice completo — Magda Negre",
                "Todas las novelas, cuentos, relatos de misterio y esculturas de Magda Negre, "
                "escritora y escultora de Barcelona.",
                BASE + "/biblioteca.html",
                "".join(partes),
                jsonld={
                    "@context": "https://schema.org",
                    "@type": "CollectionPage",
                    "name": "Índice completo — Magda Negre",
                    "url": BASE + "/biblioteca.html",
                    "about": autor_jsonld(datos),
                },
            )
        )

    # --- sitemap ----------------------------------------------------------
    urls = [
        (BASE + "/", "1.0"),
        (BASE + "/biblioteca.html", "0.9"),
    ]
    urls += [("%s/%s" % (BASE, a), "0.8") for _, _, _, a, _ in SECCIONES]
    urls += [(u, "0.7") for u in indexables]

    filas = "".join(
        "  <url><loc>%s</loc><priority>%s</priority></url>\n" % (escape(u), p) for u, p in urls
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "%s</urlset>\n" % filas
        )

    total = sum(len(fichas[c]) for c, _, _, _, _ in SECCIONES)
    vacios = total - len(indexables)
    print("obra/       %d páginas (%d sin indexar por estar sin texto)" % (total, vacios))
    print("biblioteca.html  índice completo")
    print("sitemap.xml      %d URLs" % len(urls))


if __name__ == "__main__":
    construir()
