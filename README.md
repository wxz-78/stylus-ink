# stylus-ink

Tema oscuro **monocromo** para [Stylus](https://add0n.com/stylus.html), pensado para quien
quiere una web en grises coherente con una terminal oscura. No es un tema «pastel»: todos los
colores de Catppuccin se han sustituido por una escala de grises perceptual con contraste
suficiente para leer y distinguir estados.

El repositorio contiene un único `import.json` listo para instalar en Stylus:

| Contenido | Cantidad |
|---|---|
| Estilos de Catppuccin convertidos a Ink | **134** |
| Estilos propios para sitios sin port oficial | **47** |
| **Total de userstyles** | **181** |

---

## Contenido

- [Instalación rápida](#instalación-rápida)
- [La paleta Ink](#la-paleta-ink)
- [Sitios incluidos](#sitios-incluidos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Scripts](#scripts)
- [Añadir un sitio nuevo](#añadir-un-sitio-nuevo)
- [Accesibilidad](#accesibilidad)
- [Problemas frecuentes](#problemas-frecuentes)
- [Créditos y licencia](#créditos-y-licencia)
- [Changelog](CHANGELOG.md)

---

## Instalación rápida

1. Instala la extensión **Stylus**:
   - [Firefox](https://addons.mozilla.org/firefox/addon/styl-us/)
   - [Chrome / Edge / Brave / Opera](https://chromewebstore.google.com/detail/stylus/1d6hnmodoibeecdmjhacpjjjhggljjbb)
2. Abre el panel de Stylus y entra en **Administrar → Importar**.
3. Selecciona el archivo `import.json` de este repositorio.
4. Revisa el informe de importación: los estilos se añaden **desactivados o activados** según
   el export. Puedes activar solo los que quieras desde la lista.

> Los estilos de Catppuccin se importan con el «sabor» **mocha** forzado. Todos los sabores
> (`latte`, `frappe`, `macchiato`, `mocha`) apuntan a la misma paleta Ink, así que el selector
> de sabor de Stylus no rompe el tema.

### Actualizar desde el repositorio

Vuelve a importar `import.json`. Stylus reconoce los estilos por nombre/namespace y actualiza
solo los que hayan cambiado; no duplica los existentes.

---

## La paleta Ink

Los fondos vienen de `foot.ini` (`base = #0a0a0a`). Los tonos están ordenados por luminosidad
real (L\*) y repartidos en pasos de ~2,2 L\*, de modo que se distinguen incluso en monocromo.
El acento (`mauve`) queda **por debajo** del texto para no competir con la lectura.

### Tonos y acentos

| Token | Hex | Uso habitual | Contraste sobre base |
|---|---|---|---|
| `rosewater` | `#efefef` | brillo máximo, títulos | 17,2:1 |
| `flamingo` | `#e3e3e3` | texto destacado | 15,4:1 |
| `pink` | `#d0d0d0` | adornos | 12,8:1 |
| `mauve` | `#b2b2b2` | **acento por defecto** | 9,3:1 |
| `red` | `#a0a0a0` | errores | 7,6:1 |
| `maroon` | `#acacac` | avisos suaves | 8,7:1 |
| `peach` | `#c4c4c4` | avisos | 11,4:1 |
| `yellow` | `#e9e9e9` | atención | 16,3:1 |
| `green` | `#dddddd` | éxito | 14,6:1 |
| `teal` | `#d6d6d6` | información | 13,6:1 |
| `sky` | `#cacaca` | información | 12,1:1 |
| `sapphire` | `#b8b8b8` | enlaces secundarios | 10,0:1 |
| `blue` | `#a6a6a6` | enlaces | 8,1:1 |
| `lavender` | `#bebebe` | etiquetas | 10,7:1 |

### Texto y superficies

| Token | Hex | Uso | Contraste sobre base |
|---|---|---|---|
| `text` | `#e4e4e4` | texto principal (`foreground` de foot) | 15,6:1 |
| `subtext1` | `#c8c8c8` | texto secundario | 11,8:1 |
| `subtext0` | `#a8a8a8` | texto atenuado | 8,3:1 |
| `overlay2` | `#909090` | iconos | 6,2:1 |
| `overlay1` | `#7d7d7d` | placeholders | 4,8:1 (AA) |
| `overlay0` | `#646464` | decorativo, deshabilitado | 3,4:1 |
| `surface2` | `#464646` | bordes fuertes | — |
| `surface1` | `#2e2e2e` | bordes | — |
| `surface0` | `#1a1a1a` | tarjetas y campos | — |
| `base` | `#0a0a0a` | fondo principal | — |
| `mantle` | `#050505` | barras laterales y cabeceras | — |
| `crust` | `#000000` | fondo profundo | — |

> `overlay0` es decorativo a propósito: no lo uses para texto que deba leerse.
> Si necesitas más contraste, sube a `overlay1` o `subtext0`.

---

## Sitios incluidos

### Estilos de Catppuccin convertidos (134)

Cubren, entre otros: GitHub, Reddit, YouTube, X/Twitter, Instagram, WhatsApp Web, Wikipedia,
Gmail, Google Drive, Google Photos, Google Gemini, ChatGPT, Claude, Perplexity, DeepSeek,
Proton, Tutanota, DuckDuckGo, Startpage, Brave Search, Ecosia, SearXNG, Stack Overflow,
Hacker News, MDN, DevDocs, npm, PyPI, crates.io, Arch Wiki, NixOS, Codeberg, Mastodon, Bluesky,
Twitch, Spotify, LinkedIn, Pinterest, Snapchat, Substack, Lichess, Chess.com, Desmos, Quizlet,
Canvas LMS y un largo etcétera.

La lista completa está en `import.json`. Los estilos originales viven en
[catppuccin/userstyles](https://github.com/catppuccin/userstyles) y se distribuyen con
licencia MIT.

### Estilos propios «Ink» (47)

Pensados para sitios muy usados que no tienen port oficial en Catppuccin. Son estilos
*best-effort*: se apoyan en las variables CSS públicas de cada sitio y en selectores estables.
Si un rediseño los rompe, abre un issue con una captura y el nombre del estilo.

| Categoría | Sitios |
|---|---|
| **Social** | Facebook / Messenger / Threads, TikTok, Telegram Web, Discord, Slack, Tumblr, Quora, Medium |
| **Productividad** | Notion, Google Calendar, Google Keep, Google Translate, Google Maps, Outlook Web / Teams / OneDrive, Trello, Jira / Confluence / Bitbucket, Figma, Canva, Zoom Web |
| **Entretenimiento** | Netflix, Prime Video, Disney+, SoundCloud, Steam, IMDb, Letterboxd, Goodreads, MyAnimeList |
| **Compras** | Amazon, eBay, AliExpress, Mercado Libre |
| **Viajes** | Booking.com, Airbnb |
| **Herramientas** | GitLab, Duolingo, Khan Academy, Coursera, Udemy, PayPal, Wise, TradingView, Dropbox, Copilot, Hugging Face |
| **Noticias** | BBC, El País |

> **Google Maps** invierte el mapa con un filtro de escala de grises para que las teselas
> claras no deslumbren. Si prefieres el mapa original, desactiva ese estilo o elimina el bloque
> `.widget-scene-canvas` del archivo.

> **Google Docs, Sheets y Slides** no están incluidos: el documento se dibuja en un `canvas` y
> un userstyle no puede recolorear el texto sin invertir también imágenes y gráficos. Usa el
> modo oscuro nativo de la aplicación o una extensión específica para editores de oficina.

---

## Estructura del repositorio

```
stylus-ink/
├── import.json              # export listo para Stylus (181 estilos + ajustes)
├── gen-stylus.py            # convierte un export de Catppuccin a la paleta Ink
├── build-import.py          # fusiona styles/**/*.user.css en import.json
├── styles/                  # fuente de los estilos propios
│   ├── social/
│   ├── productivity/
│   ├── entertainment/
│   ├── shopping/
│   ├── travel/
│   ├── tools/
│   └── news/
└── README.md
```

Cada archivo de `styles/` es un userstyle **autónomo**: se puede abrir, copiar o instalar
directamente en Stylus sin pasar por `build-import.py`.

---

## Scripts

No hay dependencias externas: solo Python 3.8 o superior.

### `build-import.py` — reconstruir el export

```bash
python3 build-import.py          # reescribe import.json con los estilos de styles/
python3 build-import.py --check  # comprueba si import.json está al día (CI)
```

El script:

- Conserva el bloque de ajustes y los 134 estilos de Catppuccin.
- Elimina los estilos con namespace `stylus-ink/extra/…` y los regenera desde `styles/`.
- Valida cabeceras, namespaces, versiones y nombres/namespaces duplicados.
- Es idempotente: ejecutarlo dos veces produce el mismo archivo.
- Escribe de forma atómica y conserva los permisos: si falla, `import.json` queda intacto.
- **No crea copias `.bak`**: escribe directamente sobre `import.json`.

### `gen-stylus.py` — convertir un export nuevo de Catppuccin

```bash
python3 gen-stylus.py export-catppuccin.json import.json
python3 gen-stylus.py --help          # opciones (-q para silenciar avisos)
python3 build-import.py
```

`gen-stylus.py` sustituye el `@import` remoto de Catppuccin por una librería LESS local con la
paleta Ink, fuerza `mocha` como sabor por defecto y elimina `@updateURL` para que Stylus no
sobrescriba el tema con la versión pastel. Es idempotente: los estilos ya convertidos se
actualizan a la paleta actual sin duplicarse. También conserva la indentación y los permisos del
archivo, escribe de forma atómica y avisa de los estilos que parecen de Catppuccin pero no pudo
convertir.

Flujo recomendado al salir una versión nueva de Catppuccin:

1. Exporta tus estilos desde Stylus como JSON (o descarga el export completo de Catppuccin).
2. `python3 gen-stylus.py export.json import.json`
3. `python3 build-import.py` (reañade los 47 estilos propios).
4. Revisa el diff de `import.json` y vuelve a importarlo en Stylus.

---

## Añadir un sitio nuevo

1. Crea `styles/<categoría>/<slug>.user.css` con este esqueleto:

```css
/* ==UserStyle==
@name Mi Sitio Ink
@namespace stylus-ink/extra/mi-sitio
@version 1.0.0
@description Tema oscuro monocromo Ink para Mi Sitio.
@author Ink
@license MIT
==/UserStyle== */

@-moz-document domain("misitio.com") {
  :root {
    color-scheme: dark;
    --ink-base: #0a0a0a;
    --ink-mantle: #050505;
    --ink-surface: #1a1a1a;
    --ink-surface-2: #2e2e2e;
    --ink-border: #2e2e2e;
    --ink-text: #e4e4e4;
    --ink-muted: #a8a8a8;
    --ink-accent: #b2b2b2;
  }

  html,
  body {
    background-color: var(--ink-base) !important;
    color: var(--ink-text) !important;
  }

  input,
  textarea,
  select {
    color-scheme: dark;
  }

  * {
    scrollbar-color: #464646 #050505;
  }
}
```

2. Ejecuta `python3 build-import.py`.
3. Importa `import.json` en Stylus y prueba el sitio en claro y en oscuro.

### Reglas de estilo

- **Usa la paleta de arriba**; no inventes grises nuevos sin actualizar también `PALETTE` en
  `gen-stylus.py`.
- **Prioriza las variables CSS del sitio** (`--color-*`, `--ds-*`, `--gm3-*`, `--sk_*`, etc.)
  antes que los selectores de clase. Las variables sobreviven mejor a los rediseños.
- **No apliques filtros ni `background` a `img`, `video`, `canvas` o `svg`** salvo que sea
  imprescindible (la excepción documentada es el mapa de Google Maps).
- **Mantén `color-scheme: dark`** en `:root` para que los controles nativos y los scrollbars
  se rendericen en oscuro.
- **Evita `* { background: … !important }`**: rompe imágenes, tarjetas y estados de hover.
- **No añadas `@updateURL`**: este repositorio se actualiza reimportando `import.json`.
- **`domain()` solo acepta dominios**, no rutas. Para una ruta concreta usa
  `url-prefix("https://sitio.com/ruta")`.
- **Prueba siempre**: portada, resultado de búsqueda, ficha de detalle, formularios, menús
  desplegables y modo móvil/estrecho.

---

## Accesibilidad

- El texto principal (`#e4e4e4` sobre `#0a0a0a`) supera AAA con amplio margen.
- `overlay1` es el mínimo para placeholders (AA); `overlay0` es solo decorativo.
- El acento no se usa para texto pequeño sobre fondo claro; los botones de acento llevan texto
  oscuro (`#0a0a0a`) para mantener el contraste.
- Los estados no dependen solo del color: se mantienen bordes, iconos y cambios de superficie.
- Si un sitio impone texto claro sobre fondo claro, abre un issue con la URL y el selector.

---

## Problemas frecuentes

| Síntoma | Qué probar |
|---|---|
| El tema no se aplica | Comprueba que el estilo está activo y que la URL coincide con el `@-moz-document`. |
| Se ve «a medias» | Otro userstyle o una extensión de modo oscuro está ganando. Desactiva el otro estilo. |
| Texto ilegible | Suele ser una variable del sitio que cambió. Inspecciona el elemento y añade la variable a `:root` con los tokens Ink. |
| El mapa de Google Maps se ve raro | Desactiva el estilo o elimina el filtro `.widget-scene-canvas`. |
| Stylus marca el estilo como actualizable | Los estilos propios no llevan `@updateURL`; si aparece, elimínalo. |
| Un sitio rediseñado rompe el estilo | Abre un issue indicando estilo, URL, navegador y captura. |

---

## Créditos y licencia

- Estilos originales: [Catppuccin Userstyles](https://github.com/catppuccin/userstyles),
  licencia MIT.
- Conversión a Ink, estilos propios y documentación: licencia MIT (ver `LICENSE`).

Catppuccin es una paleta comunitaria; este proyecto no está afiliado a Catppuccin ni a Stylus.
