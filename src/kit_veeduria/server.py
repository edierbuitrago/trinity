"""Servidor MCP del kit de veeduría (stdio, local).

Pocas herramientas, respuestas cortas, menú cerrado: pensado para modelos pequeños.
Ejecutar:  python -m kit_veeduria.server
"""
try:  # SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Servidor
except ImportError:  # SDK 1.x
    from mcp.server.fastmcp import FastMCP as _Servidor

from typing import Literal

from . import fichas, peticion

INSTRUCCIONES = (
    "Kit de veeduría ciudadana de Colombia. Responde SOLO con lo que devuelvan estas "
    "herramientas; si el tema no está, dilo y no inventes normas, plazos ni enlaces. "
    "Ante una pregunta sobre derechos o trámites, elige el tema que corresponda y llama a "
    "ficha(tema); responde con esa ficha, citando su nombre. Si ningún tema corresponde, "
    "no llames a la herramienta: di que el kit no cubre ese tema. Solo si la persona pide "
    "que le redactes una petición, usa generar_peticion: el servidor guarda la carta en un "
    "archivo y tú solo le dices la ruta; no escribas ni resumas la carta. Nunca pidas ni "
    "escribas datos personales de la persona en las herramientas."
)

mcp = _Servidor("kit-veeduria", instructions=INSTRUCCIONES)

TipoPeticion = Literal["informacion", "copia_documentos", "consulta", "solicitud_general"]
# Menú cerrado dentro de la propia herramienta: el modelo elige entre pocas opciones válidas.
Tema = Literal[tuple(fichas.cargar())]


@mcp.tool(description=(
    "Devuelve la ficha del tema que responde a la pregunta de la persona. Temas:" + chr(10)
    + fichas.resumen_temas() + chr(10)
    + "Si ningún tema corresponde, no uses esta herramienta y di que el kit no cubre ese tema."))
def ficha(tema: Tema) -> str:
    return fichas.ficha(tema)


@mcp.tool()
def generar_peticion(tipo: TipoPeticion, entidad: str, solicitud: str,
                     formato: str = "") -> str:
    """Redacta un derecho de petición y lo guarda en un archivo; devuelve la ruta.

    tipo: informacion (pedir datos; 10 días hábiles), copia_documentos (copia de contratos,
    actas, informes; 10 días), consulta (cómo interpreta una norma; 30 días),
    solicitud_general (queja, reclamo o actuación; 15 días).
    entidad: a quién va dirigida. solicitud: lo que se pide, en una o dos frases.
    formato: déjalo vacío salvo que la persona haya pedido un formato (Excel, PDF).
    Úsala solo cuando la persona pida que le redactes una petición.
    No incluyas datos personales.
    """
    return peticion.guardar(tipo, entidad, solicitud, None, formato)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
