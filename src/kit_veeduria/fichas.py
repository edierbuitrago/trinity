"""Carga de las fichas (menú cerrado de temas). Sin dependencias externas."""
from pathlib import Path

DIR = Path(__file__).resolve().parent / "fichas"
AVISO = ("Borrador de orientación, pendiente de revisión jurídica. "
         "No reemplaza la asesoría de un abogado.")


def _leer(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    _, cabecera, cuerpo = texto.split("---", 2)
    ficha = {}
    for linea in cabecera.strip().splitlines():
        clave, _, valor = linea.partition(":")
        ficha[clave.strip()] = valor.strip()
    ficha["cuerpo"] = cuerpo.strip()
    return ficha


def cargar() -> dict:
    """Devuelve {id: ficha} en orden alfabético estable por id."""
    fichas = {}
    for ruta in sorted(DIR.glob("*.md")):
        f = _leer(ruta)
        fichas[f["id"]] = f
    return fichas


def menu() -> str:
    fichas = cargar()
    lineas = ["Temas disponibles (usa ficha con el id exacto):"]
    for n, (id_, f) in enumerate(fichas.items(), 1):
        lineas.append(f"{n}. {id_}: {f['resumen']}")
    return "\n".join(lineas)


def resumen_temas() -> str:
    """Una línea por ficha: «- id: resumen». Se muestra dentro de la descripción de la herramienta."""
    return chr(10).join(f"- {id_}: {f['resumen']}" for id_, f in cargar().items())


def ficha(id_o_numero: str) -> str:
    fichas = cargar()
    clave = str(id_o_numero).strip().lower()
    if clave.isdigit() and 1 <= int(clave) <= len(fichas):
        clave = list(fichas)[int(clave) - 1]
    if clave not in fichas:
        validos = ", ".join(fichas)
        return f"No existe la ficha '{id_o_numero}'. Ids válidos: {validos}."
    f = fichas[clave]
    return (f"# {f['titulo']}\n\n{f['cuerpo']}\n\n"
            f"Fuentes: {f['fuentes']}\n{AVISO}")
