#!/usr/bin/env python3
"""INK · build-import.py — fusiona styles/**/*.user.css en import.json.

Uso:
    python3 build-import.py            # actualiza import.json
    python3 build-import.py --check    # solo comprueba si está al día (código 1 si no)

Los estilos propios llevan el namespace «stylus-ink/extra/…». El script los
elimina y los vuelve a generar desde los archivos .user.css, de modo que
import.json siempre se puede reconstruir y no hay que editarlo a mano.
Los 134 estilos de Catppuccin y el bloque de ajustes se conservan intactos.

La escritura es atómica y los errores de cabecera, namespace o duplicados se
muestran sin traceback. El script es idempotente.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STYLES_DIR = ROOT / "styles"
EXPORT = ROOT / "import.json"
NS_PREFIX = "stylus-ink/extra/"
NS_RE = re.compile(r"^stylus-ink/extra/[a-z0-9][a-z0-9._-]*$")
HEADER_RE = re.compile(r"/\*\s*==UserStyle==(.*?)==/UserStyle==\s*\*/", re.S)
FIELD_RE = re.compile(r"^@([\w-]+)[ \t]+(.+?)[ \t]*$", re.M)
VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,3}(?:[-+][0-9A-Za-z.-]+)?$")


class InkError(Exception):
    """Error esperado: se muestra sin traceback."""


def display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")  # tolera el BOM de exports de Windows
    except FileNotFoundError:
        raise InkError(f"{display(path)}: no existe") from None
    except IsADirectoryError:
        raise InkError(f"{display(path)}: es un directorio") from None
    except PermissionError:
        raise InkError(f"{display(path)}: sin permiso de lectura") from None
    except UnicodeDecodeError:
        raise InkError(f"{display(path)}: no es un archivo UTF-8") from None
    except OSError as exc:
        raise InkError(f"{display(path)}: {exc.strerror or exc}") from exc


def write_atomic(path: Path, text: str) -> None:
    """Escribe en un temporal del mismo directorio y lo renombra al final."""
    try:
        mode = path.stat().st_mode & 0o777
    except OSError:
        mode = 0o644
    try:
        fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    except OSError as exc:
        raise InkError(f"{display(path)}: no se pudo crear el archivo temporal "
                       f"({exc.strerror or exc})") from exc
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


def detect_indent(raw: str) -> str | None:
    """Conserva la indentación del import.json actual (2 espacios, 4, tabulación…)."""
    for line in raw.splitlines()[1:]:
        if not line.strip():
            continue
        match = re.match(r"^([ \t]+)", line)
        return match.group(1) if match else None
    return None


def parse_style(path: Path) -> dict:
    src = read_text(path)
    header = HEADER_RE.search(src)
    if not header:
        raise InkError(f"{display(path)}: falta el bloque "
                       f"/* ==UserStyle== … ==/UserStyle== */")

    meta: dict[str, str] = {}
    for key, value in FIELD_RE.findall(header.group(1)):
        key = key.lower()
        # @var puede repetirse: no es un campo único de la cabecera.
        if key in meta and key not in {"var", "advanced"}:
            raise InkError(f"{display(path)}: @{key} duplicado en la cabecera")
        meta[key] = value.strip()

    for required in ("name", "namespace", "version", "description"):
        if not meta.get(required):
            raise InkError(f"{display(path)}: falta @{required} en la cabecera")

    namespace = meta["namespace"]
    if not namespace.startswith(NS_PREFIX):
        raise InkError(
            f"{display(path)}: el namespace debe empezar por «{NS_PREFIX}» "
            f"(ahora es «{namespace}»)"
        )
    if not NS_RE.match(namespace):
        raise InkError(
            f"{display(path)}: namespace no válido «{namespace}»; usa solo minúsculas, "
            f"números, puntos, guiones y guiones bajos después de «{NS_PREFIX}»"
        )
    if not VERSION_RE.match(meta["version"]):
        raise InkError(
            f"{display(path)}: versión no válida «{meta['version']}» "
            f"(se espera algo como 1.0.0)"
        )

    usercss = {
        "name": meta["name"],
        "namespace": namespace,
        "version": meta["version"],
        "description": meta["description"],
        "author": meta.get("author", "Ink"),
        "license": meta.get("license", "MIT"),
        "preprocessor": "default",
    }
    return {
        "enabled": True,
        "name": meta["name"],
        "description": meta["description"],
        "author": meta.get("author", "Ink"),
        "usercssData": usercss,
        "sourceCode": src,
    }


def find_duplicates(values: list[str], campo: str) -> None:
    counts = Counter(value.casefold() for value in values)
    duplicates = sorted({value for value in values if counts[value.casefold()] > 1})
    if duplicates:
        raise InkError(f"{campo} duplicado(s) en styles/: {', '.join(duplicates)}")


def build() -> tuple[list[dict], dict[str, int]]:
    raw = read_text(EXPORT)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InkError(f"{display(EXPORT)}: JSON inválido en línea {exc.lineno}, "
                       f"columna {exc.colno}: {exc.msg}") from None
    if not isinstance(data, list):
        raise InkError(f"{display(EXPORT)}: se esperaba una lista")

    if not STYLES_DIR.is_dir():
        raise InkError(f"{display(STYLES_DIR)}: no existe el directorio de estilos")

    paths = sorted(STYLES_DIR.rglob("*.user.css"))
    if not paths:
        raise InkError(f"{display(STYLES_DIR)}/: no se encontró ningún archivo .user.css")

    extras = [parse_style(path) for path in paths]
    find_duplicates([e["name"] for e in extras], "nombre")
    find_duplicates([e["usercssData"]["namespace"] for e in extras], "namespace")

    # Conserva ajustes y estilos de Catppuccin; reemplaza solo los extras.
    kept: list[dict] = []
    removed = 0
    for item in data:
        if not isinstance(item, dict):
            continue
        ns = (item.get("usercssData") or {}).get("namespace", "")
        if isinstance(ns, str) and ns.startswith(NS_PREFIX):
            removed += 1
            continue
        kept.append(item)

    # Un extra no puede pisar el nombre o el namespace de un estilo ya presente.
    def norm(value: object) -> str:
        return value.casefold() if isinstance(value, str) else ""

    kept_names = {
        norm((item.get("usercssData") or {}).get("name"))
        for item in kept if isinstance(item, dict)
    }
    kept_namespaces = {
        norm((item.get("usercssData") or {}).get("namespace"))
        for item in kept if isinstance(item, dict)
    }
    for path, extra in zip(paths, extras):
        if extra["name"].casefold() in kept_names:
            raise InkError(f"{display(path)}: el nombre «{extra['name']}» ya existe "
                           f"en import.json")
        if extra["usercssData"]["namespace"].casefold() in kept_namespaces:
            raise InkError(f"{display(path)}: el namespace "
                           f"«{extra['usercssData']['namespace']}» ya existe en import.json")

    stats = {
        "ink": len(extras),
        "catppuccin": sum(1 for item in kept
                          if isinstance(item, dict) and "sourceCode" in item),
        "settings": sum(1 for item in kept
                        if isinstance(item, dict) and "settings" in item),
        "removed": removed,
    }
    return kept + extras, stats


def serialize(data: list[dict], raw: str) -> str:
    indent = detect_indent(raw)
    output = json.dumps(data, ensure_ascii=False, indent=indent)
    if raw.endswith("\n"):
        output += "\n"
    return output


def summary(stats: dict[str, int]) -> str:
    ajustes = stats["settings"]
    etiqueta = "ajuste" if ajustes == 1 else "ajustes"
    return (f"{stats['ink']} estilos Ink + {stats['catppuccin']} Catppuccin "
            f"+ {ajustes} {etiqueta}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="build-import.py",
        description="Fusiona styles/**/*.user.css en import.json de forma idempotente.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="solo comprueba si import.json está al día (código 1 si no)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        data, stats = build()
        raw = read_text(EXPORT)
        output = serialize(data, raw)

        if args.check:
            if raw != output:
                print("import.json está desactualizado: ejecuta python3 build-import.py",
                      file=sys.stderr)
                return 1
            print(f"import.json al día: {summary(stats)}")
            return 0

        if raw == output:
            print(f"import.json ya estaba al día: {summary(stats)}")
            return 0

        write_atomic(EXPORT, output)
    except InkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {display(EXPORT)}: no se pudo escribir "
              f"({exc.strerror or exc})", file=sys.stderr)
        return 1

    print(f"{summary(stats)} fusionados en import.json")
    if stats["removed"] and stats["removed"] != stats["ink"]:
        print(f"aviso: se reemplazaron {stats['removed']} estilos Ink anteriores "
              f"por {stats['ink']} actuales", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
