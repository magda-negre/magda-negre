# Web personal de Magda Negre

Web estática publicada con GitHub Pages. El contenido (biografía, escritos, obras de arte) vive en `content.json` y se edita desde la propia web.

## Archivos

| Archivo | Qué es |
| --- | --- |
| `index.html` | Portada: biografía, enlaces a las secciones, arte y contacto |
| `Novelas.dc.html` · `Cuentos.dc.html` · `Misterio.dc.html` | Las tres secciones de escritos |
| `content.json` | **Todo el contenido de la web** |
| `assets/` | Fotografías subidas desde la web |
| `site-data.js` | Carga del contenido y publicación en GitHub |
| `support.js` | Motor de la página (no tocar) |
| `build.py` | Genera la versión estática (no tocar) |
| `obra/` · `biblioteca.html` · `sitemap.xml` | **Generados automáticamente — no editar a mano** |

## Por qué hay una versión estática

La web se monta en el navegador con JavaScript, y los buscadores no leen bien
ese contenido: Google solo veía el título de la página, ni una línea de los
textos. Por eso `build.py` genera además una copia en HTML puro:

- `obra/<titulo>.html` — una página por cada novela, cuento y relato, con el
  texto completo dentro del HTML y su propia dirección para poder compartirla.
- `biblioteca.html` — índice de toda la obra, también sin JavaScript.
- `sitemap.xml` — la lista de direcciones que se le da a Google.

**No hace falta hacer nada:** al pulsar «Publicar cambios» en la web, GitHub
regenera estas páginas solo, en un minuto. Los textos que aún ponen «Escribe
aquí el texto.» se generan pero se marcan para que Google no los indexe, y
pasan a ser visibles en cuanto se les escriba el contenido.

Para regenerarlas a mano hace falta Python: `python3 build.py`.

## Publicar la web (una sola vez)

1. En este repositorio: **Settings → Pages**.
2. En *Source* elige **Deploy from a branch**, rama `main`, carpeta `/ (root)`. Guardar.
3. Al minuto la web estará en `https://magda-negre.github.io/magda-negre/`.

## Editar la web

1. Abrir la web publicada.
2. Pulsar **Modo edición** (abajo a la derecha) e introducir el código: `magda2026`.
3. Escribir sobre cualquier texto; usar **+ Añadir novela / cuento / relato / obra** y **Elegir fotografía**.
4. Pulsar **Publicar cambios**. La primera vez pedirá la clave de publicación (ver abajo).
5. En ~1 minuto los cambios se ven para todo el mundo.

## Clave de publicación (una sola vez)

1. En GitHub: **Settings** (de la cuenta) → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → *Generate new token*.
2. *Repository access*: **Only select repositories** → `magda-negre/magda-negre`.
3. *Permissions* → *Repository permissions* → **Contents: Read and write**.
4. Generar, copiar la clave y pegarla en la web cuando la pida. Queda guardada en ese navegador.

Si la clave caduca, la web la volverá a pedir: solo hay que generar una nueva.
