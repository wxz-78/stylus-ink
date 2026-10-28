# Changelog

Todas las fechas usan el formato AAAA-MM-DD.

## [1.1.1] — 2026-10-28

### Optimizado

- Los 46 estilos propios que fijaban `scrollbar-color` con el selector universal `*` ahora lo
  declaran en `:root`. La propiedad es heredada, así que el resultado visual no cambia y el
  navegador evita evaluar el selector en cada elemento del documento.
- `build-import.py` usa `Counter` para detectar duplicados (antes era O(n²)) y no reescribe
  `import.json` si no hay cambios.

### Corregido

- `gen-stylus.py` y `build-import.py` muestran errores claros (archivo inexistente, JSON inválido,
  permisos, cabeceras mal formadas) en lugar de terminar con un traceback.
- Escritura atómica en ambos scripts: un fallo a mitad deja intacto el archivo anterior; también
  se conservan la indentación, el salto de línea final y los permisos.
- `gen-stylus.py` acepta el `@import` remoto con comillas simples, `url(...)` y espacios, elimina
  `@updateURL` aunque esté al final del archivo y avisa de los estilos que no pudo convertir.
- `build-import.py` valida también el formato del namespace y la versión, detecta duplicados de
  nombre/namespace contra los estilos ya presentes y cuenta correctamente el bloque de ajustes.
- `README.md`: se eliminan las referencias a `wallpapers/`, un directorio que no forma parte del
  repositorio.

## [1.1.0] — 2026-10-24

### Añadido

- **47 userstyles propios** para sitios sin port oficial de Catppuccin, organizados por
  categoría en `styles/`:
  - Social: Meta (Facebook/Messenger/Threads), TikTok, Telegram Web, Discord, Slack, Tumblr,
    Quora y Medium.
  - Productividad: Notion, Google Calendar, Google Keep, Google Translate, Google Maps,
    Microsoft 365 (Outlook/Teams/OneDrive), Trello, Atlassian (Jira/Confluence/Bitbucket),
    Figma, Canva y Zoom Web.
  - Entretenimiento: Netflix, Prime Video, Disney+, SoundCloud, Steam, IMDb, Letterboxd,
    Goodreads y MyAnimeList.
  - Compras: Amazon, eBay, AliExpress y Mercado Libre.
  - Viajes: Booking.com y Airbnb.
  - Herramientas: GitLab, Duolingo, Khan Academy, Coursera, Udemy, PayPal, Wise, TradingView,
    Dropbox, Copilot y Hugging Face.
  - Noticias: BBC y El País.
- `build-import.py`: fusiona `styles/**/*.user.css` en `import.json` de forma idempotente,
  valida cabeceras y admite `--check`.
- `LICENSE` (MIT).
- Documentación completa en `README.md`: instalación, paleta con contrastes, catálogo de
  sitios, estructura, flujo de actualización, plantilla para nuevos estilos, reglas de
  accesibilidad y resolución de problemas.

### Cambiado

- `import.json` pasa de 134 a **181 userstyles** (134 de Catppuccin + 47 propios).
- `gen-stylus.py` documenta el flujo completo con `build-import.py` y recuerda que no genera
  copias `.bak`.

## [1.0.0] — 2026-10-23

- Importación inicial de 134 userstyles de Catppuccin convertidos a la paleta monocroma Ink.
