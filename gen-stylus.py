#!/usr/bin/env python3
"""INK · gen-stylus.py — convierte un export de Stylus de Catppuccin Userstyles a la paleta Ink.

Uso:  python3 gen-stylus.py export.json [import.json]
      python3 gen-stylus.py --help
      python3 build-import.py          # reañade los estilos propios de styles/

Cada userstyle de Catppuccin importa una librería remota (userstyles.catppuccin.com/lib/std/v1.less)
que define la paleta. Aquí se sustituye ese @import por una librería local con los grises de Ink,
así que no hace falta tocar los 134 estilos uno a uno: la paleta vive en PALETTE (abajo) y se
regenera con este script cuando salga un export nuevo.

El archivo de salida se escribe de forma atómica (temporal + os.replace): si algo falla a mitad,
el archivo anterior queda intacto. Se puede usar el mismo archivo como entrada y salida.
Los estilos propios (namespace stylus-ink/extra/…) se conservan; build-import.py se encarga
de regenerarlos desde styles/ después de convertir un export de Catppuccin.

Cambios por estilo:
  · @import remoto  ->  librería local (misma API: #lib.palette/defaults/css-variables/rgbify/hslify
                        y los mapas @catppuccin y @catppuccin-filters; todos los «sabores» valen lo
                        mismo: Ink es solo oscuro)
  · Light/Dark Flavor por defecto = mocha (evita las ramas de latte pensadas para temas claros)
  · se quita @updateURL: si no, Stylus lo actualizaría desde Catppuccin y desharía el cambio
Los estilos ya convertidos conservan su código, pero se les sustituye la librería Ink incrustada
por la de PALETTE: así un cambio de paleta se aplica reejecutando este script (es idempotente).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


class InkError(Exception):
    """Error esperado: se muestra sin traceback."""


# ── Paleta Ink v2 ──────────────────────────────────────────────────────────────────────────────
# Los fondos siguen siendo los de Ink (foot.ini: base #0a0a0a), pero los tonos ya no heredan el
# ANSI de la terminal: se ordenan por la luminosidad real de cada color de Catppuccin (mocha) y se
# reparten en pasos de ~2,2 L* para que se distingan en monocromo. El acento (mauve) queda por
# debajo del texto (#e4e4e4), no por encima. Contrastes sobre base calculados con WCAG.
PALETTE = {
    # tonos · L* aproximado y contraste sobre #0a0a0a
    "rosewater": "#efefef",  # L* 94,4 · 17,2:1
    "flamingo":  "#e3e3e3",  # L* 90,2 · 15,4:1
    "pink":      "#d0d0d0",  # L* 83,5 · 12,8:1
    "mauve":     "#b2b2b2",  # L* 72,6 ·  9,3:1 · acento por defecto
    "red":       "#a0a0a0",  # L* 65,9 ·  7,6:1 · errores
    "maroon":    "#acacac",  # L* 70,4 ·  8,7:1
    "peach":     "#c4c4c4",  # L* 79,2 · 11,4:1
    "yellow":    "#e9e9e9",  # L* 92,3 · 16,3:1
    "green":     "#dddddd",  # L* 88,1 · 14,6:1 · éxito
    "teal":      "#d6d6d6",  # L* 85,6 · 13,6:1
    "sky":       "#cacaca",  # L* 81,3 · 12,1:1
    "sapphire":  "#b8b8b8",  # L* 74,8 · 10,0:1
    "blue":      "#a6a6a6",  # L* 68,1 ·  8,1:1 · enlaces
    "lavender":  "#bebebe",  # L* 77,0 · 10,7:1
    # texto · rampa de ~8-10 L*; overlay1 llega a 4,8:1 (AA)
    "text":      "#e4e4e4",  # foreground de foot · 15,6:1
    "subtext1":  "#c8c8c8",  # 11,8:1
    "subtext0":  "#a8a8a8",  #  8,3:1
    "overlay2":  "#909090",  #  6,2:1
    "overlay1":  "#7d7d7d",  #  4,8:1 (AA)
    "overlay0":  "#646464",  #  3,4:1 · decorativo
    "surface2":  "#464646",
    "surface1":  "#2e2e2e",
    "surface0":  "#1a1a1a",  # tarjetas visibles sobre base
    # fondos
    "base":      "#0a0a0a",  # background de foot
    "mantle":    "#050505",
    "crust":     "#000000",
}
ORDER = list(PALETTE)
FLAVORS = ("latte", "frappe", "macchiato", "mocha")

# Acepta comillas simples/dobles, url(...) y espacios: algunos exports no son idénticos.
OLD_IMPORT = re.compile(
    r"""@import\s+
        (?:\([^)]*\)\s+)?
        (?:url\(\s*)?
        ["']https://userstyles\.catppuccin\.com/lib/std/v1\.less["']
        \s*\)?\s*;""",
    re.I | re.X,
)
INK_MARK = "// ── INK: paleta monocroma local"
UPDATE_URL_RE = re.compile(r"(?m)^[ \t]*@updateURL\b[^\n]*(?:\n|$)")
FLAVOR_LINE_RE = re.compile(r"(?m)^@var select (?:light|dark)Flavor .*$")
BRACE_RE = re.compile(r"[{}]")


def invert_pct(hexcol: str) -> float:
    """Gris #rrggbb -> porcentaje de invert() partiendo de negro (brightness(0))."""
    return round(int(hexcol[1:3], 16) / 255 * 100, 1)


def filtro(hexcol: str) -> str:
    return f'~"brightness(0) saturate(100%) invert({invert_pct(hexcol)}%)"'


def build_lib() -> str:
    flavor_block = "\n".join(f"    @{n}: {c};" for n, c in PALETTE.items())
    mapa = "\n".join(f"  @{f}: {{\n{flavor_block}\n  }};" for f in FLAVORS)
    filt_block = "\n".join(f"    @{n}: {filtro(c)};" for n, c in PALETTE.items())
    mapa_f = "\n".join(f"  @{f}: {{\n{filt_block}\n  }};" for f in FLAVORS)
    pal = "\n".join(f"    @{n}: {c};" for n, c in PALETTE.items())
    fil = "\n".join(f"    @{n}-filter: {filtro(c)};" for n, c in PALETTE.items())
    cssvars = "\n".join(f"    --ctp-{n}: @{n};" for n in ORDER)
    return f"""// ── INK: paleta monocroma local (sustituye a userstyles.catppuccin.com/lib/std/v1.less) ──
// Escala de grises perceptual; el acento queda por debajo del texto.
@catppuccin: {{
{mapa}
}};
@catppuccin-filters: {{
{mapa_f}
}};
#lib {{
  .palette() {{
{pal}
    @accent: @@accentColor;
    @accent-filter-name: "@{{accentColor}}-filter";
    @accent-filter: @@accent-filter-name;
{fil}
  }}
  .defaults() {{
    input, textarea, select {{
      color-scheme: dark;
      &::placeholder {{ color: @subtext0 !important; }}
    }}
    ::selection {{ background-color: fade(@accent, 30%); }}
  }}
  .css-variables() {{
{cssvars}
    --ctp-accent: @accent;
  }}
  .rgbify(@color) {{ @rgb: red(@color), green(@color), blue(@color); }}
  .hslify(@color) {{ @hsl: hue(@color), saturation(@color), lightness(@color); }}
}}"""


def fix_flavor_line(src: str) -> str:
    """Marca mocha como valor por defecto en las líneas @var select lightFlavor/darkFlavor."""
    def fix(m: re.Match[str]) -> str:
        line = m.group(0).replace("*", "")
        return re.sub(r'"mocha:([^"]*)"', r'"mocha:\1*"', line)
    return FLAVOR_LINE_RE.sub(fix, src)


def replace_ink_lib(src: str, lib: str) -> str | None:
    """Sustituye la librería Ink ya incrustada (estilos ya convertidos) por la actual."""
    inicio = src.find(INK_MARK)
    if inicio < 0:
        return None
    bloque = src.find("#lib {", inicio)
    if bloque < 0:
        return None
    depth = 0
    # finditer recorre las llaves en C, no en un bucle Python carácter a carácter.
    for match in BRACE_RE.finditer(src, bloque):
        depth += 1 if match.group() == "{" else -1
        if depth == 0:
            return src[:inicio] + lib + src[match.end():]
        if depth < 0:
            return None
    return None


def looks_like_catppuccin(src: str) -> bool:
    return ("userstyles.catppuccin.com" in src
            or "@catppuccin" in src
            or "@var select darkFlavor" in src)


def convert(style: dict, lib: str) -> str:
    """Convierte un estilo en sitio. Devuelve el estado para el resumen."""
    src = style.get("sourceCode")
    if not isinstance(src, str):
        return "omitido"

    if OLD_IMPORT.search(src):
        src = OLD_IMPORT.sub(lambda _m: lib, src, count=1)
        modo = "convertido"
    else:
        nuevo = replace_ink_lib(src, lib)
        if nuevo is None or nuevo == src:
            return "sin cambios"
        src = nuevo
        modo = "actualizado"

    src = fix_flavor_line(src)
    src = UPDATE_URL_RE.sub("", src)
    style["sourceCode"] = src

    data = style.get("usercssData")
    if isinstance(data, dict):
        variables = data.get("vars")
        if isinstance(variables, dict):
            for key in ("lightFlavor", "darkFlavor"):
                var = variables.get(key)
                if isinstance(var, dict):
                    var["default"] = "mocha"
        data.pop("updateURL", None)

    style.pop("updateUrl", None)
    style.pop("originalDigest", None)   # ya no coincide con el original; sin updateUrl no se usa
    return modo


def detect_indent(raw: str) -> str | None:
    """Conserva la indentación del JSON de entrada (2 espacios, 4, tabulación…)."""
    for line in raw.splitlines()[1:]:
        if not line.strip():
            continue
        match = re.match(r"^([ \t]+)", line)
        return match.group(1) if match else None
    return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")  # tolera el BOM de exports de Windows
    except FileNotFoundError:
        raise InkError(f"{path}: no existe") from None
    except IsADirectoryError:
        raise InkError(f"{path}: es un directorio") from None
    except PermissionError:
        raise InkError(f"{path}: sin permiso de lectura") from None
    except UnicodeDecodeError:
        raise InkError(f"{path}: no es un archivo UTF-8") from None
    except OSError as exc:
        raise InkError(f"{path}: {exc.strerror or exc}") from exc


def write_atomic(path: Path, text: str) -> None:
    """Escribe en un temporal del mismo directorio y lo renombra al final."""
    try:
        mode = path.stat().st_mode & 0o777
    except OSError:
        mode = 0o644
    try:
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    except OSError as exc:
        raise InkError(f"{path}: no se pudo crear el archivo temporal ({exc.strerror or exc})") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        try:
            os.chmod(tmp, mode)  # mkstemp crea 0600; conserva los permisos del archivo previo
        except OSError:
            pass
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gen-stylus.py",
        description="Convierte un export de Stylus de Catppuccin a la paleta monocroma Ink.",
    )
    parser.add_argument("entrada", type=Path, help="export JSON de Stylus/Catppuccin")
    parser.add_argument(
        "salida",
        nargs="?",
        type=Path,
        default=Path("ink-import.json"),
        help="archivo de salida (por defecto: ink-import.json)",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="no mostrar advertencias")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        raw = read_text(args.entrada)
        try:
            datos = json.loads(raw)
        except json.JSONDecodeError as exc:
            return fail(f"{args.entrada}: JSON inválido en línea {exc.lineno}, "
                        f"columna {exc.colno}: {exc.msg}")
        if not isinstance(datos, list):
            return fail(f"{args.entrada}: se esperaba una lista de userstyles")

        lib = build_lib()
        estilos = [e for e in datos if isinstance(e, dict) and "sourceCode" in e]
        resultados = [convert(e, lib) for e in estilos]
        convertidos = resultados.count("convertido")
        actualizados = resultados.count("actualizado")
        omitidos = resultados.count("omitido")
        sin_cambios = resultados.count("sin cambios")

        if not args.quiet:
            avisos = []
            for estilo in estilos:
                src = estilo.get("sourceCode")
                if (isinstance(src, str) and looks_like_catppuccin(src)
                        and (INK_MARK not in src or "#lib {" not in src)):
                    nombre = estilo.get("name") or "(sin nombre)"
                    avisos.append(str(nombre))
            if avisos:
                muestra = ", ".join(avisos[:5])
                extra = f" (y {len(avisos) - 5} más)" if len(avisos) > 5 else ""
                cuantos = ("1 estilo parece" if len(avisos) == 1
                           else f"{len(avisos)} estilos parecen")
                verbo = "no se pudo" if len(avisos) == 1 else "no se pudieron"
                print(f"aviso: {cuantos} de Catppuccin pero {verbo} convertir: "
                      f"{muestra}{extra}", file=sys.stderr)

        indent = detect_indent(raw)
        texto = json.dumps(datos, ensure_ascii=False, indent=indent)
        if raw.endswith("\n"):
            texto += "\n"
        try:
            mismo_archivo = os.path.samefile(args.entrada, args.salida)
        except OSError:
            mismo_archivo = False
        if mismo_archivo and texto == raw:
            print(f"{convertidos} convertidos, {actualizados} actualizados, "
                  f"{sin_cambios} sin cambios -> {args.salida} (ya estaba al día)")
            return 0
        write_atomic(args.salida, texto)
    except InkError as exc:
        return fail(str(exc))
    except OSError as exc:
        return fail(f"{args.salida}: no se pudo escribir ({exc.strerror or exc})")

    resumen = (f"{convertidos} convertidos, {actualizados} actualizados, "
               f"{sin_cambios} sin cambios")
    if omitidos:
        resumen += f", {omitidos} omitidos"
    print(f"{resumen} -> {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
