"""Motor de ejecución de la sandbox educativa.

Ejecuta el código del estudiante dentro del mismo proceso de Streamlit, pero con
varias barreras pensadas para que nadie se haga daño sin querer:

* lista blanca de módulos importables (``math``, ``random``, ``json``, ...)
* bloqueo de llamadas peligrosas (``open``, ``eval``, ``exec``, ``__import__``...)
* ``print`` capturado e ``input`` simulado desde un cuadro de texto
* límite de tiempo (bucles infinitos) y de tamaño de salida
* traducción de los errores de Python a español, con pista incluida

AVISO IMPORTANTE: esto es una barrera *pedagógica*, no una caja de seguridad
real. El código corre con los permisos de quien lanza Streamlit, así que usa la
app solo con código tuyo o de tus estudiantes, en tu propia máquina o en un
entorno controlado.
"""

from __future__ import annotations

import ast
import builtins as _bi
import re
import threading
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

DEFAULT_TIMEOUT = 8.0
MAX_OUTPUT_CHARS = 20_000
SANDBOX_FILENAME = "<sandbox>"

# --------------------------------------------------------------------------- #
# Políticas
# --------------------------------------------------------------------------- #

ALLOWED_MODULES = {
    "math", "random", "statistics", "datetime", "json", "string", "re", "time",
    "collections", "itertools", "functools", "operator", "decimal", "fractions",
    "textwrap", "unicodedata", "calendar", "copy", "typing", "dataclasses",
    "enum", "heapq", "bisect", "pprint", "numbers", "abc", "csv", "uuid",
}

# Nombres que ni siquiera se pueden mencionar dentro del código del estudiante.
BLOCKED_NAMES = {
    "open", "eval", "exec", "compile", "__import__", "breakpoint",
    "exit", "quit", "input_raw", "setattr", "delattr", "vars", "memoryview",
}

# Atributos que sirven para escaparse del entorno restringido.
BLOCKED_ATTRS = {
    "__class__", "__bases__", "__subclasses__", "__mro__", "__globals__",
    "__code__", "__closure__", "__builtins__", "__getattribute__",
    "__reduce__", "__reduce_ex__", "__import__", "__loader__", "__spec__",
    "__dict__", "__self__", "__func__",
}

# Builtins que sí quedan disponibles dentro de la sandbox.
_SAFE_BUILTIN_NAMES = [
    "abs", "all", "any", "ascii", "bin", "bool", "bytes", "callable", "chr",
    "complex", "dict", "divmod", "enumerate", "filter", "float", "format",
    "frozenset", "getattr", "hasattr", "hash", "hex", "id", "int",
    "isinstance", "issubclass", "iter", "len", "list", "map", "max", "min",
    "next", "object", "oct", "ord", "pow", "property", "range", "repr",
    "reversed", "round", "set", "slice", "sorted", "staticmethod", "str",
    "sum", "super", "tuple", "type", "zip", "classmethod",
    # excepciones y constantes
    "ArithmeticError", "AssertionError", "AttributeError", "BaseException",
    "EOFError", "Exception", "FloatingPointError", "IndentationError",
    "IndexError", "KeyError", "LookupError", "NameError", "NotImplementedError",
    "OverflowError", "RecursionError", "RuntimeError", "StopIteration",
    "SyntaxError", "TypeError", "UnboundLocalError", "ValueError",
    "ZeroDivisionError", "True", "False", "None", "NotImplemented", "Ellipsis",
]


class OutputLimit(Exception):
    """Se lanza cuando el programa imprime demasiado (normalmente, bucle loco)."""


# --------------------------------------------------------------------------- #
# Captura de salida y entrada simulada
# --------------------------------------------------------------------------- #


class _Buffer:
    """Acumula texto con tope, para que un ``while True: print()`` no tumbe la app."""

    def __init__(self, limit: int = MAX_OUTPUT_CHARS) -> None:
        self._parts: list[str] = []
        self._n = 0
        self._limit = limit
        self.truncated = False

    def write(self, text: str) -> None:
        if self._n >= self._limit:
            self.truncated = True
            raise OutputLimit()
        self._parts.append(text)
        self._n += len(text)
        if self._n >= self._limit:
            self.truncated = True
            raise OutputLimit()

    def value(self) -> str:
        return "".join(self._parts)


def _make_print(buf: _Buffer) -> Callable[..., None]:
    def _print(*values: Any, sep: str = " ", end: str = "\n", file: Any = None,
               flush: bool = False) -> None:
        buf.write(sep.join(str(v) for v in values) + end)

    return _print


def _make_input(buf: _Buffer, stdin_text: str) -> Callable[..., str]:
    pending = iter(stdin_text.splitlines() if stdin_text else [])

    def _input(prompt: str = "") -> str:
        if prompt:
            buf.write(str(prompt))
        try:
            value = next(pending)
        except StopIteration:
            raise EOFError(
                "input() pidió un dato pero la caja «Entrada (input)» está vacía "
                "o ya se acabaron las líneas."
            ) from None
        buf.write(value + "\n")  # eco, como en una terminal de verdad
        return value

    return _input


def _guarded_import(name: str, globals_=None, locals_=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root not in ALLOWED_MODULES:
        raise ImportError(
            f"El módulo «{name}» no está disponible en la sandbox. "
            f"Permitidos: {', '.join(sorted(ALLOWED_MODULES))}."
        )
    return _bi.__import__(name, globals_, locals_, fromlist, level)


def _make_globals(buf: _Buffer, stdin_text: str) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for name in _SAFE_BUILTIN_NAMES:
        if hasattr(_bi, name):
            safe[name] = getattr(_bi, name)
    safe["print"] = _make_print(buf)
    safe["input"] = _make_input(buf, stdin_text)
    safe["__import__"] = _guarded_import
    safe["__build_class__"] = _bi.__build_class__  # permite definir clases
    return {"__builtins__": safe, "__name__": "__main__", "__doc__": None}


# --------------------------------------------------------------------------- #
# Revisión estática (antes de ejecutar)
# --------------------------------------------------------------------------- #


def _static_check(tree: ast.AST) -> list[str]:
    problems: list[str] = []

    def add(lineno: int, msg: str) -> None:
        problems.append(f"Línea {lineno}: {msg}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_MODULES:
                    add(node.lineno, f"el módulo «{alias.name}» no está permitido en la sandbox.")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level or root not in ALLOWED_MODULES:
                add(node.lineno, f"el módulo «{node.module or '.'}» no está permitido en la sandbox.")
        elif isinstance(node, ast.Name) and node.id in BLOCKED_NAMES:
            add(node.lineno, f"«{node.id}» está desactivado aquí (toca disco o ejecuta código arbitrario).")
        elif isinstance(node, ast.Attribute) and node.attr in BLOCKED_ATTRS:
            add(node.lineno, f"el atributo «{node.attr}» está desactivado en la sandbox.")

    return problems


# --------------------------------------------------------------------------- #
# Errores en español
# --------------------------------------------------------------------------- #

_HINTS: dict[str, str] = {
    "SyntaxError": "Revisa comillas o paréntesis sin cerrar y los dos puntos «:» al final de if / for / while / def.",
    "IndentationError": "Python usa la sangría para saber qué va dentro de qué. Usa siempre 4 espacios y sé consistente.",
    "TabError": "Mezclaste tabulaciones y espacios. Usa solo espacios (4 por nivel).",
    "NameError": "Estás usando un nombre que Python no conoce: quizá lo escribiste distinto, o es un texto al que le faltan comillas.",
    "UnboundLocalError": "Dentro de una función usaste una variable antes de asignarla. Pásala como parámetro o asígnala primero.",
    "ZeroDivisionError": "No se puede dividir entre cero. Valida el divisor con un if antes de dividir.",
    "IndexError": "El índice se salió del rango. Recuerda: el primero es 0 y el último es len(coleccion) - 1.",
    "KeyError": "Esa clave no existe en el diccionario. Usa mi_dict.get(clave, valor_por_defecto) para evitarlo.",
    "AttributeError": "Ese método no existe para ese tipo de dato. Comprueba con type(x) qué tienes realmente entre manos.",
    "EOFError": "Tu programa pidió un input() pero no había datos. Escribe una línea por cada input() en la caja «Entrada».",
    "RecursionError": "Una función se llama a sí misma sin caso de parada. Añade la condición que corta la recursión.",
    "ImportError": "En la sandbox solo se pueden importar módulos de la lista blanca (math, random, json, datetime...).",
    "ModuleNotFoundError": "Ese módulo no está disponible aquí. Prueba con math, random, statistics, datetime o json.",
    "StopIteration": "Se acabaron los elementos del iterador antes de lo esperado.",
    "AssertionError": "Falló un assert: la condición que diste por cierta no lo era.",
}

_MESSAGE_HINTS: list[tuple[str, str]] = [
    (r"can only concatenate str",
     "No puedes sumar texto y número con «+». Usa una f-string: f\"total: {n}\" o convierte con str(n)."),
    (r"unsupported operand type\(s\)",
     "Los tipos no combinan con ese operador. Revisa con type(x) y convierte con int(), float() o str()."),
    (r"invalid literal for int\(\)",
     "int() solo convierte textos que sean números enteros: \"12\" sí, \"12.5\" o \"hola\" no."),
    (r"could not convert string to float",
     "float() necesita un texto numérico. Ojo con los espacios: usa texto.strip() antes de convertir."),
    (r"object is not callable",
     "Estás poniendo paréntesis a algo que no es una función. ¿Le diste a una variable el nombre de una función?"),
    (r"takes .* positional argument.* but .* were given",
     "Llamaste a la función con más (o menos) argumentos de los que declaraste en su def."),
    (r"missing \d+ required positional argument",
     "Falta pasar argumentos obligatorios. Míralos en la línea del def o dales un valor por defecto."),
    (r"object is not subscriptable",
     "Estás usando corchetes [ ] sobre algo que no es lista, texto ni diccionario."),
    (r"object is not iterable",
     "Solo se puede recorrer con for aquello que tiene elementos (listas, textos, diccionarios, range...)."),
    (r"'str' object does not support item assignment",
     "Los textos son inmutables: no puedes hacer texto[0] = \"A\". Crea un texto nuevo con replace() o slicing."),
    (r"list indices must be integers",
     "Los índices de una lista son enteros. Si querías buscar por nombre, lo que necesitas es un diccionario."),
]


def _hint_for(error_type: str, message: str) -> str:
    for pattern, hint in _MESSAGE_HINTS:
        if re.search(pattern, message):
            return hint
    return _HINTS.get(error_type, "Lee la última línea del error: casi siempre dice exactamente qué pasó y dónde.")


@dataclass
class RunResult:
    """Resultado de ejecutar código del estudiante."""

    code: str = ""
    ok: bool = False
    stdout: str = ""
    error: str = ""
    error_type: str = ""
    hint: str = ""
    lineno: int | None = None
    namespace: dict[str, Any] = field(default_factory=dict)
    timed_out: bool = False
    truncated: bool = False
    seconds: float = 0.0
    blocked: list[str] = field(default_factory=list)

    @property
    def has_error(self) -> bool:
        return bool(self.error) or self.timed_out


def _extract_lineno(exc: BaseException) -> int | None:
    lineno = None
    for frame, line in traceback.walk_tb(exc.__traceback__):
        if frame.f_code.co_filename == SANDBOX_FILENAME:
            lineno = line
    return lineno


def run_user_code(
    code: str,
    stdin: str = "",
    timeout: float = DEFAULT_TIMEOUT,
    extra_globals: dict[str, Any] | None = None,
) -> RunResult:
    """Ejecuta ``code`` y devuelve un :class:`RunResult` listo para pintar."""

    result = RunResult(code=code)

    if not code.strip():
        result.error_type = "Sin código"
        result.error = "No hay nada que ejecutar."
        result.hint = "Escribe algo en el editor y vuelve a darle a Ejecutar."
        return result

    # 1) ¿Compila?
    try:
        tree = ast.parse(code, filename=SANDBOX_FILENAME)
    except SyntaxError as exc:
        result.error_type = type(exc).__name__
        result.error = exc.msg or str(exc)
        result.lineno = exc.lineno
        result.hint = _hint_for(result.error_type, result.error)
        return result

    # 2) ¿Usa algo prohibido?
    problems = _static_check(tree)
    if problems:
        result.blocked = problems
        result.error_type = "Bloqueado por la sandbox"
        result.error = "\n".join(problems)
        result.hint = ("Esta sandbox es para practicar lógica de Python: no permite tocar archivos, "
                       "la red ni el sistema. Todo lo demás está disponible.")
        return result

    # 3) A ejecutar, en un hilo aparte para poder cortar bucles infinitos.
    buf = _Buffer()
    g = _make_globals(buf, stdin)
    if extra_globals:
        g.update(extra_globals)

    box: dict[str, Any] = {}

    def worker() -> None:
        start = time.perf_counter()
        try:
            exec(compile(tree, SANDBOX_FILENAME, "exec"), g)
            box["ok"] = True
        except OutputLimit:
            box["ok"] = True
        except SystemExit:
            box["ok"] = True
        except BaseException as exc:  # noqa: BLE001 - queremos mostrarlo todo
            box["exc"] = exc
        finally:
            box["seconds"] = time.perf_counter() - start

    thread = threading.Thread(target=worker, daemon=True, name="sandbox-run")
    thread.start()
    thread.join(timeout)

    result.stdout = buf.value()
    result.truncated = buf.truncated
    result.namespace = g
    result.seconds = float(box.get("seconds", timeout))

    if thread.is_alive():
        result.timed_out = True
        result.error_type = "Tiempo agotado"
        result.error = f"El programa lleva más de {timeout:.0f} segundos ejecutándose y se detuvo."
        result.hint = ("Casi siempre es un bucle infinito: revisa que la condición del while "
                       "cambie dentro del bucle (por ejemplo, un contador que suma).")
        return result

    exc = box.get("exc")
    if exc is not None:
        result.error_type = type(exc).__name__
        result.error = str(exc) or result.error_type
        result.lineno = _extract_lineno(exc)
        result.hint = _hint_for(result.error_type, result.error)
        return result

    result.ok = True
    return result


# --------------------------------------------------------------------------- #
# Utilidades para los retos autoevaluados
# --------------------------------------------------------------------------- #


def call_safely(func: Callable[..., Any], args: Sequence[Any] = (),
                kwargs: dict[str, Any] | None = None,
                timeout: float = 4.0) -> tuple[bool, Any, str]:
    """Llama a una función del estudiante sin arriesgar un cuelgue de la app.

    Devuelve ``(ok, valor, mensaje_de_error)``.
    """
    kwargs = kwargs or {}
    box: dict[str, Any] = {}

    def worker() -> None:
        try:
            box["value"] = func(*args, **kwargs)
        except BaseException as exc:  # noqa: BLE001
            box["exc"] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return False, None, "la función se quedó colgada (¿bucle infinito?)"
    if "exc" in box:
        exc = box["exc"]
        return False, None, f"{type(exc).__name__}: {exc}"
    return True, box.get("value"), ""


def pretty(value: Any) -> str:
    """Representación corta y legible para los mensajes de los retos."""
    text = repr(value)
    return text if len(text) <= 120 else text[:117] + "..."
