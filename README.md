# Kit de veeduría — a civic-oversight kit for small, local language models

**Status: working prototype (v0.1, November 2026). Draft content, not legally reviewed.**

A small [MCP](https://modelcontextprotocol.io) server designed so that a *small* language model
(roughly 4B–14B parameters, running on the citizen's own computer) can help people in Colombia understand how the
State is organized and ask it for public information — without the model ever being the
source of legal facts.

> Spanish summary: kit básico de veeduría ciudadana. Fichas escritas por personas
> (derecho de petición, acceso a la información, tutela, estructura del Estado…) y un
> generador de derechos de petición con texto legal fijo. Funciona con un modelo local.

## Design principles

1. **Closed menu, not open questions.** The model picks from a fixed list of topics and
   request types instead of composing free-form queries. Small models are good at choosing
   among a few options and bad at inventing valid arguments.
2. **The server writes the answer; the model only chooses and fills in.** Legal text
   (constitutional articles, statutes, deadlines) is fixed text written by people. The model
   never generates it.
3. **Short responses.** Every tool answer fits well inside a small model's context window
   (a sheet is ≈300 words; the petition tool returns only a file path and a few lines).
4. **Closed choices with helpful errors.** Topics and request types are enumerated values in the
   tool schema, so a wrong value is rejected with an error that lists the valid ones and the
   model can recover on its own.
5. **Personal data stays on the user's device.** The petition comes back with placeholders
   (`[NOMBRE COMPLETO]`, `[NÚMERO DE CÉDULA]`, …) that the person fills in locally. The server
   neither receives nor stores them.
6. **Every answer shows its source.** Each topic sheet lists the law it is based on.

## Tools

| Tool | What it does |
|---|---|
| `ficha(tema)` | Returns one sheet. The closed list of topics (with a one-line summary each) is part of the tool's own description and schema, so a small model *chooses* among valid options instead of searching |
| `generar_peticion(tipo, entidad, solicitud, formato?)` | Writes a *derecho de petición* with fixed legal text to a Word file on the user's computer and returns only the file path and the legal deadline |

The petition is saved to a file (default `Documents/Peticiones`, or the folder in `KIT_VEEDURIA_SALIDA`)
instead of being returned as text because, in early tests, small models summarized or rewrote
a letter returned in the tool response and the person never got the real document.
The server is meant to run on the user's own machine (stdio), so the path is usable.

Current sheets (Spanish): the right of petition; access to public information; what to do if
the State does not answer; basics of the *tutela* action; how the Colombian State is organized;
which entity handles which problem; citizen oversight (*veedurías*); where to find public
contracts and projects.

## Run it

Requires Python 3.10+ and the `mcp` package.

```bash
pip install -r requirements.txt
python -m unittest discover -s tests
PYTHONPATH=src python -m kit_veeduria.server      # stdio server
```

To use it with a local model in LM Studio (or any MCP client that supports stdio), see
[`examples/mcp.json`](examples/mcp.json).

## What is *not* here yet

- **Live queries** to public procurement (SECOP) and company registry (RUES) data. These exist
  in a separate, non-public service and are not part of this repository yet.
- **A systematic evaluation.** Informal tests with Qwen3 8B and 14B (LM Studio, with and without
  reasoning, one run per question, no repetitions) changed the design three times:
  (1) returning the letter as text failed, because the model summarized it (0 of 10 delivered) — the letter is now
  saved to a file; (2) a keyword search over the sheets looked good on the questions it was tuned on
  (8 of 8) but failed on new ones (2–3 of 8) — it was replaced by a closed topic list inside the tool schema;
  (3) on 15 fresh questions never used for tuning, the 14B (both modes) got all 5 petitions (right type, file path
  delivered) and 8 of 8 sheet lookups right and refused the 2 out-of-scope questions; the 8B with reasoning got 7 of 8 sheets and
  4 of 5 petitions with a path; the 8B without reasoning got 4 of 8 sheets (it often named the topic or said "not covered"
  without calling the tool). These are small samples; a larger, independent test set and repeated runs are still needed.
- **Legal review** of the sheets and the petition template by a lawyer.
- **Community pilots.** The kit is designed for citizens and local oversight groups; no field
  pilot has been run yet.

## Structure

```
src/kit_veeduria/
  fichas/            topic sheets (Markdown, one per topic)
  fichas.py          loads and serves the sheets
  peticion.py        fixed-text petition generator
  server.py          MCP server (stdio)
tests/               unit tests (no model required)
examples/            client configuration
```

## License

- **Code** (`src/`, `tests/`, `examples/`): [Apache License 2.0](LICENSE).
- **Topic sheets** (`src/kit_veeduria/fichas/`): [CC BY 4.0](LICENSE-fichas.md) — reuse them freely, with credit to Cuestión Pública.

## Maintainers

Cuestión Pública (Colombia), investigative journalism on public contracting and political finance.
