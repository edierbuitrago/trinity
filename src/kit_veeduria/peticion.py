"""Generador del derecho de petición ciudadano.

El texto legal es FIJO (se escribe aquí, no lo genera el modelo). El modelo solo
elige el tipo de solicitud y aporta la entidad y lo que se pide. Los datos
personales NO pasan por el servidor: la carta sale con marcadores entre
corchetes que la persona rellena en su propio equipo.
"""
import os
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

PLACEHOLDERS = ["[NOMBRE COMPLETO]", "[NÚMERO DE CÉDULA]", "[CORREO ELECTRÓNICO DE RESPUESTA]"]

# clave -> (nombre en la referencia, plazo en días hábiles, descripción corta)
TIPOS = {
    "informacion": ("Solicitud de información pública", 10,
                    "pedir datos o respuestas sobre lo que hace la entidad"),
    "copia_documentos": ("Solicitud de copia de documentos", 10,
                         "pedir copia de contratos, actas, resoluciones, etc."),
    "consulta": ("Consulta", 30,
                 "preguntar a la autoridad cómo interpreta o aplica sus funciones"),
    "solicitud_general": ("Derecho de petición", 15,
                          "queja, reclamo o solicitud de una actuación"),
}

CABEZOTE = (
    "{nombre}, identificado(a) con cédula de ciudadanía número {cedula}, en ejercicio "
    "del derecho de petición y de acceso a la información pública, consagrados en los "
    "artículos 20, 23 y 74 de la Constitución Política, regulados por la Ley 1437 de "
    "2011 (Código de Procedimiento Administrativo y de lo Contencioso Administrativo, "
    "en la forma sustituida por la Ley 1755 de 2015) y por la Ley 1712 de 2014, "
    "respetuosamente me dirijo a ustedes para garantizar el desarrollo material de mis "
    "derechos constitucionales; extiendo la siguiente solicitud:"
)

FUNDAMENTOS = """\
**FUNDAMENTOS DE DERECHO**

1. Constitución Política:
   a. Artículo 23, el cual consagra que “toda persona tiene derecho a presentar peticiones respetuosas a las autoridades por motivos de interés general o particular y a obtener pronta resolución. El legislador podrá reglamentar su ejercicio ante organizaciones privadas para garantizar los derechos fundamentales.”
   b. Artículo 74, el cual indica que “todas las personas tienen derecho a acceder a los documentos públicos salvo los casos que establezca la ley. El secreto profesional es inviolable.”
2. Ley 1437 de 2011, por medio de la cual se expide el Código de Procedimiento Administrativo y de lo Contencioso Administrativo:
   a. Artículo 13, que establece que “Toda persona tiene derecho a presentar peticiones respetuosas a las autoridades, en los términos señalados en este código, por motivos de interés general o particular, y a obtener pronta resolución completa y de fondo sobre la misma.(...)”
3. Ley de Transparencia, 1712 de 2014:
   a. Artículo 24, que indica “toda persona tiene derecho a solicitar y recibir información de cualquier sujeto obligado, en la forma y condiciones que establece esta ley y la Constitución.”

Si la Entidad considera que la información solicitada constituye información pública sujeta a clasificación o reserva, solicito que en virtud del artículo 28 de la Ley 1712 de 2014 se me informe sobre: i) el fundamento constitucional o legal que justifica la clasificación o la reserva, señalando expresamente la norma, artículo, inciso o párrafo que la ampara; ii) la excepción que, dentro de las previstas en los artículos 18 y 19 de la Ley 1712 de 2014, cobija la calificación de la información como reservada o clasificada; y iii) la explicación de la forma en la que la revelación de la información causaría un daño presente, probable y específico que excede el interés público que representa el acceso a dicha información.

Así mismo, solicito tener en cuenta que, de conformidad con el artículo 21 de la Ley 1712 de 2014, “[e]n aquellas circunstancias en que la totalidad de la información contenida en un documento no esté protegida por una excepción contenida en la presente ley, debe hacerse una versión pública que mantenga la reserva únicamente de la parte indispensable” y que “[l]a reserva de acceso a la información opera respecto del contenido de un documento público pero no de su existencia”."""

ORDINALES = ["PRIMERO", "SEGUNDO", "TERCERO", "CUARTO", "QUINTO", "SEXTO",
             "SÉPTIMO", "OCTAVO", "NOVENO", "DÉCIMO"]
MAX_ITEMS = 10
MAX_TEXTO = 1500


def tipos() -> str:
    lineas = ["Tipos de solicitud (usa la clave exacta):"]
    for clave, (_, plazo, desc) in TIPOS.items():
        lineas.append(f"- {clave}: {desc}. Plazo legal de respuesta: {plazo} días hábiles.")
    return "\n".join(lineas)


def _armar(tipo, entidad, solicitud, items, formato):
    """Devuelve (carta, nota, plazo, entidad, solicitud, nombre_tipo) o lanza ValueError con un mensaje útil."""
    tipo = (tipo or "").strip().lower()
    if tipo not in TIPOS:
        raise ValueError(f"Tipo '{tipo}' no válido. Claves válidas: {', '.join(TIPOS)}.")
    entidad = (entidad or "").strip()
    solicitud = (solicitud or "").strip()
    if not entidad or not solicitud:
        raise ValueError("Faltan datos: se necesita 'entidad' (a quién va dirigida) y 'solicitud' (qué se pide).")
    if len(solicitud) > MAX_TEXTO or any(len(i) > MAX_TEXTO for i in (items or [])):
        raise ValueError(f"Texto demasiado largo (máximo {MAX_TEXTO} caracteres por campo). Resume y vuelve a intentar.")
    items = [i.strip() for i in (items or []) if i and i.strip()][:MAX_ITEMS]
    nombre_tipo, plazo, _ = TIPOS[tipo]

    hoy = date.today()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
    fecha = f"[CIUDAD], {hoy.day} de {meses[hoy.month - 1]} de {hoy.year}"

    partes = [
        fecha, "",
        "Señores", f"**{entidad}**", "",
        f"**Referencia:** {nombre_tipo}", "",
        CABEZOTE.format(nombre=PLACEHOLDERS[0], cedula=PLACEHOLDERS[1]), "",
        "**PETICIÓN**", "",
        "Por medio del presente documento solicito respetuosamente me envíen al correo "
        "electrónico indicado en el acápite de notificaciones lo siguiente:", "",
        f"**PRIMERO.** {solicitud}",
    ]
    if items:
        partes.append("")
        partes += [f"   {chr(97 + i)}. {t}" for i, t in enumerate(items)]
    if formato.strip():
        partes += ["", f"Solicito que la respuesta se entregue en formato: {formato.strip()}."]
    partes += ["", FUNDAMENTOS, "",
               "**NOTIFICACIONES**", "",
               f"Se puede notificar al peticionario y enviar la respuesta al correo electrónico: {PLACEHOLDERS[2]}",
               "", "Muy cordialmente,", "", PLACEHOLDERS[0], f"C.C. {PLACEHOLDERS[1]}"]
    carta = "\n".join(partes)

    nota = (
        "\n\n---\nAntes de enviar: reemplaza los datos entre corchetes ([CIUDAD], "
        "[NOMBRE COMPLETO], [NÚMERO DE CÉDULA], [CORREO ELECTRÓNICO DE RESPUESTA]) en tu "
        f"equipo; la herramienta no los recibe ni los guarda. La entidad tiene {plazo} días "
        "hábiles para responder. Guarda la constancia de envío. "
        "Borrador de orientación, pendiente de revisión jurídica."
    )
    return carta, nota, plazo, entidad, solicitud, nombre_tipo


def generar(tipo: str, entidad: str, solicitud: str,
            items: list[str] | None = None, formato: str = "") -> str:
    """Devuelve el texto completo de la carta (útil para pruebas y clientes que lo muestren)."""
    try:
        carta, nota, *_ = _armar(tipo, entidad, solicitud, items, formato)
    except ValueError as e:
        return str(e)
    return carta + nota


def carpeta_salida() -> Path:
    """Carpeta donde se guardan los borradores (variable KIT_VEEDURIA_SALIDA o Documentos/Peticiones)."""
    ruta = os.environ.get("KIT_VEEDURIA_SALIDA")
    return Path(ruta) if ruta else Path.home() / "Documents" / "Peticiones"


def _a_docx(carta: str, destino: Path) -> None:
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    doc.styles["Normal"].font.name = "Arial"
    doc.styles["Normal"].font.size = Pt(11)
    for linea in carta.split("\n"):
        p = doc.add_paragraph()
        for i, trozo in enumerate(linea.split("**")):
            if trozo:
                p.add_run(trozo).bold = (i % 2 == 1)
    doc.save(str(destino))


def guardar(tipo: str, entidad: str, solicitud: str,
            items: list[str] | None = None, formato: str = "") -> str:
    """Escribe la carta en un archivo (Word si hay python-docx, si no texto) y devuelve un aviso corto."""
    try:
        carta, nota, plazo, entidad, solicitud, nombre_tipo = _armar(
            tipo, entidad, solicitud, items, formato)
    except ValueError as e:
        return str(e)
    carpeta = carpeta_salida()
    carpeta.mkdir(parents=True, exist_ok=True)
    base = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFD", entidad.lower())
                  .encode("ascii", "ignore").decode()).strip("-")[:40] or "entidad"
    sello = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        destino = carpeta / f"peticion_{base}_{sello}.docx"
        _a_docx(carta, destino)
    except ImportError:
        destino = carpeta / f"peticion_{base}_{sello}.txt"
        destino.write_text(carta.replace("**", ""), encoding="utf-8")
    return (
        f"Borrador guardado en este archivo: {destino}\n"
        f"Es un {nombre_tipo.lower()} dirigido a {entidad}. La entidad tiene {plazo} días hábiles "
        "para responder.\n"
        f"Dile a la persona, con estas palabras: 1) abre el archivo {destino}; 2) reemplaza los datos entre "
        "corchetes ([CIUDAD], [NOMBRE COMPLETO], [NÚMERO DE CÉDULA], [CORREO ELECTRÓNICO DE "
        "RESPUESTA]) en su equipo, nadie más los recibe; 3) envíalo y guarda la constancia de envío.\n"
        "No repitas ni resumas el texto de la carta: está en el archivo. "
        "Es un borrador de orientación, pendiente de revisión jurídica."
    )
