"""Contenido del curso: lecciones, mini tips, quizzes y retos autoevaluados.

La ruta va desde `print("Hola")` hasta funciones, que es donde el estudiante
deja de escribir *scripts* y empieza a escribir *programas*.

Cada lección es un diccionario con:
    id, num, icon, title, tag, minutes, subtitle, chips, blocks, quiz, challenges

Los `blocks` son tuplas que `ui.render_blocks` sabe pintar:
    ("h", titulo) ("md", texto) ("code", codigo[, stdin[, pie]]) ("show", codigo)
    ("tip"/"warn"/"key"/"bad", texto[, titulo]) ("cards", items)
    ("table", cabeceras, filas) ("cmp", mal, bien[, nota])
"""

from __future__ import annotations

from ui import (
    t_custom, t_defined, t_func, t_num, t_rerun_contains, t_stdout_contains,
    t_var,
)

# --------------------------------------------------------------------------- #
# Comprobadores a medida
# --------------------------------------------------------------------------- #


def _check_tarjeta(res):
    ns = res.namespace
    for var in ("nombre", "programa"):
        if var not in ns:
            return False, f"falta la variable `{var}`"
        if not isinstance(ns[var], str) or not ns[var].strip():
            return False, f"`{var}` tiene que ser un texto con algo dentro"
        if ns[var] not in res.stdout:
            return False, f"el valor de `{var}` no aparece en lo que imprimiste"
    return True, ""


def _check_siete_lineas(res):
    ventas = [120, 340, 90, 500, 275, 60, 410]
    lineas = [ln for ln in res.stdout.splitlines() if ln.strip()]
    if len(lineas) < len(ventas):
        return False, f"esperaba al menos 7 líneas (una por venta) y conté {len(lineas)}"
    for i, venta in enumerate(ventas, start=1):
        if not any(str(venta) in ln for ln in lineas):
            return False, f"la venta del día {i} ({venta}) no aparece impresa"
    return True, "una línea por venta"


def _check_promedios(res):
    prom = res.namespace.get("promedios")
    if not isinstance(prom, dict):
        return False, "`promedios` tiene que ser un diccionario"
    esperado = {"Ana": 4.4, "Luis": 3.07, "Sara": 4.87}
    if set(prom) != set(esperado):
        return False, f"las claves deberían ser {sorted(esperado)} y son {sorted(prom)}"
    for nombre, valor in esperado.items():
        try:
            actual = float(prom[nombre])
        except (TypeError, ValueError):
            return False, f"el promedio de {nombre} no es un número"
        if abs(actual - valor) > 0.005:
            return False, f"para {nombre} esperaba ~{valor} y tengo {prom[nombre]}"
    return True, "3 promedios correctos"


def _fizzbuzz_esperado(n: int) -> list[str]:
    salida = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            salida.append("FizzBuzz")
        elif i % 3 == 0:
            salida.append("Fizz")
        elif i % 5 == 0:
            salida.append("Buzz")
        else:
            salida.append(str(i))
    return salida


_ESTUDIANTES_DEMO = [
    {"nombre": "Ana", "notas": [4.5, 4.0]},
    {"nombre": "Luis", "notas": [2.0, 2.5]},
]


# --------------------------------------------------------------------------- #
# 1. Empieza aquí
# --------------------------------------------------------------------------- #

L_INICIO = {
    "id": "inicio",
    "num": 1,
    "icon": "🚀",
    "title": "Empieza aquí",
    "tag": "Inicio",
    "minutes": 4,
    "subtitle": "Cómo sacarle el jugo a esta app en 20 minutos diarios (y por qué eso funciona mejor que 4 horas el domingo).",
    "chips": ["Sin instalar nada", "Aprende ejecutando", "Ruta hasta funciones"],
    "blocks": [
        ("md",
         "Esta app es un **laboratorio**: cada concepto viene con código que puedes ejecutar, "
         "romper y volver a ejecutar sin salir de la página. Aprender a programar no es "
         "*entender* código ajeno, es **escribir** código propio y equivocarse rápido."),
        ("cards", [
            ("📖", "Lecciones", "Teoría mínima + ejemplos ejecutables. Todo bloque de código tiene botón `▶ Ejecutar`."),
            ("🧪", "Sandbox", "Un editor libre donde escribes lo que quieras, con `input()` simulado y errores traducidos."),
            ("🏆", "Retos", "Ejercicios que se **corrigen solos**: te dicen qué pasó y qué falta."),
            ("📈", "Progreso", "Ganas XP con cada quiz y reto. Sirve para ver si de verdad avanzaste."),
        ]),
        ("h", "Tu primer programa"),
        ("code",
         'print("Hola, mundo")\n'
         'print("Soy estudiante de posgrado y hoy empiezo con Python 🐍")\n'
         'print("2 + 2 =", 2 + 2)',
         "", "Dale a **▶ Ejecutar** y mira el panel de salida."),
        ("tip",
         "`print()` es tu microscopio. Cuando algo no funcione, imprime las variables "
         "*antes* de la línea que falla: el 80 % de los errores se ven a simple vista."),
        ("h", "El método: 20 minutos que sí rinden"),
        ("cards", [
            ("⌨️", "Escribe, no copies", "Copiar y pegar produce la ilusión de saber. Teclea el ejemplo aunque lo veas obvio."),
            ("🔧", "Rompe el ejemplo", "Cambia un número, borra una comilla, mira el error. Los errores son el temario real."),
            ("🗣️", "Explícalo en voz alta", "Si no puedes explicar qué hace una línea, todavía no la sabes."),
            ("🔁", "Repaso espaciado", "Vuelve mañana a la lección de hoy durante 5 minutos. Ahí se fija."),
        ]),
        ("warn",
         "El enemigo número uno del posgrado es el *tutorial infinito*: ver 6 horas de video y no escribir "
         "una línea. Regla práctica: por cada 10 minutos de lectura, 20 de teclado."),
        ("h", "La ruta que vas a recorrer"),
        ("table",
         ["#", "Lección", "Con esto podrás"],
         [
             ["2", "Variables y tipos", "Guardar datos y saber qué tienes entre manos"],
             ["3", "Operadores", "Calcular, comparar y decidir"],
             ["4", "Cadenas de texto", "Limpiar y formatear datos reales"],
             ["5", "Entrada y salida", "Programas que conversan con el usuario"],
             ["6", "Condicionales", "Que el programa tome decisiones"],
             ["7", "Bucles", "Repetir sin repetirte"],
             ["8", "Listas y tuplas", "Manejar colecciones ordenadas"],
             ["9", "Diccionarios y conjuntos", "Datos con nombre (como una fila de una tabla)"],
             ["10", "Funciones", "Empaquetar lógica y dejar de copiar y pegar"],
         ]),
        ("key",
         "Meta del curso: llegar a **funciones**. Ahí es donde tu código pasa de ser una lista de "
         "instrucciones a ser una herramienta reutilizable."),
    ],
    "quiz": [
        {
            "q": "¿Cuál es la mejor forma de estudiar con esta app?",
            "options": [
                "Leer todas las lecciones seguidas y luego practicar",
                "Ejecutar, modificar y romper cada ejemplo mientras leo",
                "Ver la solución de los retos primero para ahorrar tiempo",
            ],
            "answer": 1,
            "why": "La práctica intercalada con la teoría es lo que fija el aprendizaje.",
            "hint": "Programar es una habilidad motriz, como tocar un instrumento.",
        },
        {
            "q": "¿Qué imprime `print(\"2 + 2 =\", 2 + 2)`?",
            "options": ["2 + 2 = 2 + 2", "2 + 2 = 4", "4 4"],
            "answer": 1,
            "why": "Lo que va entre comillas es texto literal; lo que va fuera, Python lo calcula.",
            "hint": "Fíjate en qué parte está entre comillas.",
        },
    ],
    "challenges": [{
        "id": "tarjeta",
        "title": "Tu tarjeta de presentación",
        "level": "Fácil",
        "points": 20,
        "prompt": ("Crea las variables `nombre` y `programa` (textos) e imprime al menos una línea "
                   "que contenga **ambos** valores."),
        "starter": 'nombre = ""\nprograma = ""\n\nprint()',
        "tests": [t_custom("Defines `nombre` y `programa` y los imprimes", _check_tarjeta)],
        "hint": "Puedes unir texto y variables con una f-string: `print(f\"Soy {nombre} de {programa}\")`.",
        "solution": ('nombre = "Camilo"\n'
                     'programa = "Especialización en Bases de Datos"\n\n'
                     'print(f"Soy {nombre} y estudio {programa}")'),
    }],
}

# --------------------------------------------------------------------------- #
# 2. Variables y tipos
# --------------------------------------------------------------------------- #

L_VARIABLES = {
    "id": "variables",
    "num": 2,
    "icon": "📦",
    "title": "Variables y tipos",
    "tag": "Fundamentos",
    "minutes": 9,
    "subtitle": "Una variable no es una caja: es una **etiqueta** que le pegas a un dato para poder llamarlo por su nombre.",
    "chips": ["int · float · str · bool", "type()", "snake_case"],
    "blocks": [
        ("md",
         "En Python no declaras el tipo: asignas y listo. El tipo lo pone el **dato**, no tú.\n\n"
         "```python\nnombre = \"Ana\"   # la etiqueta 'nombre' apunta al texto \"Ana\"\n```"),
        ("code",
         'nombre = "Ana"\n'
         'edad = 29\n'
         'promedio = 4.35\n'
         'activo = True\n'
         'pendiente = None\n\n'
         'print(nombre, edad, promedio, activo, pendiente)\n'
         'print(type(nombre), type(edad), type(promedio), type(activo))'),
        ("h", "Los cinco tipos que necesitas hoy"),
        ("table",
         ["Tipo", "Qué guarda", "Ejemplo", "Ojo con..."],
         [
             ["`int`", "Enteros", "`42`, `-7`, `0`", "División `/` siempre da `float`"],
             ["`float`", "Decimales", "`4.35`, `1e-3`", "`0.1 + 0.2` no da exacto `0.3`"],
             ["`str`", "Texto", '`"Ana"`, `\'BD\'`', "`\"5\" + 5` es error"],
             ["`bool`", "Verdadero/falso", "`True`, `False`", "Van con mayúscula inicial"],
             ["`None`", "Ausencia de valor", "`None`", "No es `0` ni `\"\"`"],
         ]),
        ("code",
         'print(7 / 2)      # 3.5  -> siempre float\n'
         'print(7 // 2)     # 3    -> división entera\n'
         'print(0.1 + 0.2)  # el clásico susto de los decimales\n'
         'print(round(0.1 + 0.2, 2))',
         "", "Ejecuta y observa la tercera línea: no es un bug de Python, es cómo funcionan los decimales binarios."),
        ("tip",
         "Para dinero y notas, redondea al final con `round(valor, 2)` o formatea con `f\"{valor:.2f}\"`. "
         "Nunca compares floats con `==`; compara con una tolerancia."),
        ("h", "Convertir entre tipos (casting)"),
        ("code",
         'texto = "42"\n'
         'numero = int(texto)        # str -> int\n'
         'print(numero + 8)\n\n'
         'print(float("3.5") * 2)    # str -> float\n'
         'print(str(2026) + " es el año")   # int -> str\n'
         'print(int(4.99))           # trunca, NO redondea\n'
         'print(bool(0), bool(""), bool("hola"))'),
        ("warn",
         "`int(\"4.5\")` explota con `ValueError`. Si el texto trae decimales, primero `float()` y luego `int()`."),
        ("h", "Cómo nombrar variables (esto sí se califica en la vida real)"),
        ("cmp",
         'x = 250000\ny = 0.19\nz = x * y',
         'precio_base = 250000\ntasa_iva = 0.19\nvalor_iva = precio_base * tasa_iva',
         "El código se lee muchas más veces de las que se escribe. Usa `snake_case` y nombres que digan qué guardan."),
        ("md",
         "**Reglas duras:** empiezan por letra o `_`, no llevan espacios ni tildes, distinguen mayúsculas "
         "(`nota` ≠ `Nota`) y no pueden ser palabras reservadas (`if`, `for`, `class`, `def`, `list`...)."),
        ("tip",
         "Nunca le pongas a una variable el nombre de algo de Python: si escribes `list = [1, 2]`, "
         "pierdes la función `list()` en el resto del programa."),
        ("h", "Trucos de asignación"),
        ("code",
         'a, b, c = 1, 2, 3          # asignación múltiple\n'
         'print(a, b, c)\n\n'
         'a, b = b, a                # intercambio sin variable temporal\n'
         'print(a, b)\n\n'
         'contador = 0\n'
         'contador += 5              # equivale a contador = contador + 5\n'
         'print(contador)\n\n'
         'IVA_COLOMBIA = 0.19        # "constante": MAYÚSCULAS por convención\n'
         'print(IVA_COLOMBIA)'),
        ("key",
         "`=` **asigna**, `==` **compara**. Es el error de dedo más común del primer mes."),
    ],
    "quiz": [
        {
            "q": "¿Qué tipo tiene `resultado` tras `resultado = 10 / 2`?",
            "options": ["int", "float", "str"],
            "answer": 1,
            "why": "El operador `/` devuelve siempre float, aunque la división sea exacta (5.0).",
            "hint": "Prueba `print(type(10 / 2))` en la sandbox.",
        },
        {
            "q": "¿Cuál de estos nombres de variable es válido y recomendable?",
            "options": ["2do_promedio", "promedio final", "promedio_final"],
            "answer": 2,
            "why": "No puede empezar por número ni llevar espacios; `snake_case` es el estándar (PEP 8).",
            "hint": "Piensa qué caracteres NO se permiten.",
        },
        {
            "q": "¿Qué pasa al ejecutar `int(\"7.9\")`?",
            "options": ["Devuelve 7", "Devuelve 8", "Lanza ValueError"],
            "answer": 2,
            "why": "`int()` solo acepta textos de enteros. Con decimales: `int(float(\"7.9\"))` → 7.",
            "hint": "Pruébalo en la sandbox y lee el error.",
        },
    ],
    "challenges": [{
        "id": "iva",
        "title": "Calcula el IVA",
        "level": "Fácil",
        "points": 25,
        "prompt": ("Con `precio_base = 250000` y `tasa_iva = 0.19`:\n\n"
                   "1. Crea `valor_iva` con el IVA del precio.\n"
                   "2. Crea `total` con el precio más el IVA.\n"
                   "3. Imprime el total con **dos decimales** (debe verse `297500.00`)."),
        "starter": ("precio_base = 250000\n"
                    "tasa_iva = 0.19\n\n"
                    "valor_iva = \n"
                    "total = \n\n"
                    "print()"),
        "tests": [
            t_num("valor_iva", 47500.0),
            t_num("total", 297500.0),
            t_stdout_contains("297500.00", "Imprimes el total con dos decimales"),
        ],
        "hint": "Para el formato: `print(f\"Total: {total:.2f}\")`.",
        "solution": ("precio_base = 250000\n"
                     "tasa_iva = 0.19\n\n"
                     "valor_iva = precio_base * tasa_iva\n"
                     "total = precio_base + valor_iva\n\n"
                     'print(f"Total a pagar: {total:.2f}")'),
    }],
}

# --------------------------------------------------------------------------- #
# 3. Operadores
# --------------------------------------------------------------------------- #

L_OPERADORES = {
    "id": "operadores",
    "num": 3,
    "icon": "➗",
    "title": "Operadores",
    "tag": "Fundamentos",
    "minutes": 8,
    "subtitle": "Calcular, comparar y combinar condiciones. Con `//` y `%` se resuelven la mitad de los ejercicios de un parcial.",
    "chips": ["// y %", "and · or · not", "Precedencia"],
    "blocks": [
        ("h", "Aritméticos"),
        ("table",
         ["Operador", "Qué hace", "Ejemplo", "Resultado"],
         [
             ["`+ - *`", "Suma, resta, multiplica", "`3 * 4`", "`12`"],
             ["`/`", "División real", "`7 / 2`", "`3.5`"],
             ["`//`", "División entera (cociente)", "`7 // 2`", "`3`"],
             ["`%`", "Módulo (residuo)", "`7 % 2`", "`1`"],
             ["`**`", "Potencia", "`2 ** 10`", "`1024`"],
         ]),
        ("code",
         'total_minutos = 145\n'
         'horas = total_minutos // 60\n'
         'minutos = total_minutos % 60\n'
         'print(f"{horas}h {minutos}min")\n\n'
         'numero = 17\n'
         'print("par" if numero % 2 == 0 else "impar")'),
        ("tip",
         "`//` y `%` son la pareja para **repartir**: cuántos grupos completos salen (`//`) y qué sobra (`%`). "
         "Sirven para horas/minutos, páginas de resultados, turnos, días de la semana..."),
        ("h", "Comparación: siempre devuelven True o False"),
        ("code",
         'nota = 3.8\n'
         'print(nota > 3.0)\n'
         'print(nota == 3.8)\n'
         'print(nota != 5.0)\n'
         'print(3.0 <= nota <= 5.0)   # comparación encadenada, muy pythónica\n'
         'print("ana" == "Ana")       # el texto distingue mayúsculas'),
        ("h", "Lógicos: and, or, not"),
        ("code",
         'asistencia = 0.85\n'
         'nota = 3.4\n\n'
         'aprueba = nota >= 3.0 and asistencia >= 0.80\n'
         'print("Aprueba:", aprueba)\n\n'
         'print(not aprueba)\n'
         'print(nota >= 4.5 or asistencia == 1.0)'),
        ("key",
         "Cortocircuito: en `A and B`, si `A` es falso, `B` **ni se evalúa**. Por eso se escribe "
         "`if cantidad != 0 and total / cantidad > 5:` — así nunca divides entre cero."),
        ("h", "Pertenencia y valores de verdad"),
        ("code",
         'carrera = "Especialización en Bases de Datos"\n'
         'print("Datos" in carrera)\n'
         'print("Redes" not in carrera)\n\n'
         '# Todo esto es "falso" para Python:\n'
         'print(bool(0), bool(0.0), bool(""), bool([]), bool({}), bool(None))\n'
         '# y todo lo demás es "verdadero":\n'
         'print(bool(-1), bool("0"), bool([0]))'),
        ("warn",
         "`bool(\"False\")` es `True`: cualquier texto no vacío es verdadero. Ojo cuando leas datos con `input()`."),
        ("h", "Precedencia (quién va primero)"),
        ("code",
         'print(2 + 3 * 4)        # 14, no 20\n'
         'print((2 + 3) * 4)      # 20\n'
         'print(10 - 2 ** 3)      # la potencia primero -> 2\n'
         'print(True or False and False)   # "and" va antes que "or" -> True'),
        ("tip",
         "No memorices la tabla de precedencia: **pon paréntesis**. Cuestan cero y evitan discusiones."),
    ],
    "quiz": [
        {
            "q": "¿Cuánto vale `17 % 5`?",
            "options": ["3", "2", "3.4"],
            "answer": 1,
            "why": "17 = 5*3 + 2. El módulo devuelve el residuo: 2.",
            "hint": "`%` no divide: devuelve lo que sobra.",
        },
        {
            "q": "Con `x = 0`, ¿qué imprime `print(x != 0 and 10 / x > 1)`?",
            "options": ["ZeroDivisionError", "False", "True"],
            "answer": 1,
            "why": "Por el cortocircuito: `x != 0` es False, así que la división nunca se ejecuta.",
            "hint": "Piensa qué hace `and` cuando la primera parte ya es falsa.",
        },
    ],
    "challenges": [{
        "id": "segundos",
        "title": "De segundos a h:mm:ss",
        "level": "Fácil",
        "points": 25,
        "prompt": ("Con `total_segundos = 7325`, calcula las variables `horas`, `minutos` y `segundos` "
                   "usando solo `//` y `%`. Luego imprime el resultado en formato `2:02:05`."),
        "starter": ("total_segundos = 7325\n\n"
                    "horas = \n"
                    "minutos = \n"
                    "segundos = \n\n"
                    "print()"),
        "tests": [
            t_var("horas", 2), t_var("minutos", 2), t_var("segundos", 5),
            t_stdout_contains("2:02:05", "Imprimes `2:02:05` (con ceros a la izquierda)"),
        ],
        "hint": ("Primero saca las horas con `// 3600`. Lo que sobra (`% 3600`) son los segundos "
                 "restantes: de ahí salen minutos y segundos. Para los ceros: `f\"{minutos:02d}\"`."),
        "solution": ("total_segundos = 7325\n\n"
                     "horas = total_segundos // 3600\n"
                     "resto = total_segundos % 3600\n"
                     "minutos = resto // 60\n"
                     "segundos = resto % 60\n\n"
                     'print(f"{horas}:{minutos:02d}:{segundos:02d}")'),
    }],
}

# --------------------------------------------------------------------------- #
# 4. Cadenas
# --------------------------------------------------------------------------- #

L_CADENAS = {
    "id": "cadenas",
    "num": 4,
    "icon": "🔤",
    "title": "Cadenas de texto",
    "tag": "Datos",
    "minutes": 11,
    "subtitle": "El 90 % de los datos del mundo real llega como texto sucio. Aquí aprendes a limpiarlo y presentarlo.",
    "chips": ["f-strings", "slicing", ".strip() .split() .join()"],
    "blocks": [
        ("h", "Crear texto"),
        ("code",
         "simple = 'comillas simples'\n"
         'doble = "comillas dobles: da igual"\n'
         'con_comillas = "Ella dijo \'listo\'"\n'
         'largo = """Un texto\n'
         'de varias\n'
         'líneas"""\n\n'
         'print(simple)\n'
         'print(con_comillas)\n'
         'print(largo)\n'
         'print(len(largo))'),
        ("h", "f-strings: la única forma que debes usar para formatear"),
        ("code",
         'nombre = "Ana"\n'
         'nota = 4.3567\n'
         'creditos = 3\n\n'
         'print(f"{nombre} sacó {nota:.2f} en {creditos} créditos")\n'
         'print(f"Redondeado a entero: {nota:.0f}")\n'
         'print(f"Con separador de miles: {1250000:,}")\n'
         'print(f"Alineado a la derecha: |{nombre:>10}|")\n'
         'print(f"Alineado a la izquierda: |{nombre:<10}|")\n'
         'print(f"Centrado: |{nombre:^10}|")\n'
         'print(f"Porcentaje: {0.8532:.1%}")\n'
         'print(f"Se puede calcular adentro: {nota * creditos:.2f}")'),
        ("tip",
         "`f\"{variable=}\"` imprime *nombre y valor*: `print(f\"{nota=}\")` muestra `nota=4.3567`. "
         "Es el atajo de depuración más rápido que existe."),
        ("h", "Índices y rebanadas (slicing)"),
        ("md",
         "```\n texto:   P  y  t  h  o  n\n índice:  0  1  2  3  4  5\n negativo:-6 -5 -4 -3 -2 -1\n```"),
        ("code",
         'palabra = "Python"\n'
         'print(palabra[0])       # primer carácter\n'
         'print(palabra[-1])      # último\n'
         'print(palabra[0:3])     # desde 0 hasta 3 (sin incluir el 3)\n'
         'print(palabra[:3])      # lo mismo\n'
         'print(palabra[3:])      # desde el 3 hasta el final\n'
         'print(palabra[::2])     # de dos en dos\n'
         'print(palabra[::-1])    # al revés'),
        ("warn",
         "El texto es **inmutable**: `palabra[0] = \"J\"` lanza `TypeError`. "
         "Para cambiarlo, creas uno nuevo: `\"J\" + palabra[1:]`."),
        ("h", "Los métodos que vas a usar siempre"),
        ("code",
         'dato = "   ana MARÍA gómez  \\n"\n\n'
         'print(repr(dato.strip()))     # quita espacios y saltos de los extremos\n'
         'print(dato.strip().title())   # Cada Palabra En Mayúscula\n'
         'print(dato.strip().upper())\n'
         'print(dato.strip().lower())\n'
         'print(dato.strip().replace(" ", "_"))\n'
         'print(dato.strip().split())   # divide por espacios -> lista\n'
         'print("-".join(["2026", "08", "13"]))\n'
         'print("bases de datos".startswith("bases"))\n'
         'print("informe.pdf".endswith(".pdf"))\n'
         'print("abracadabra".count("a"))\n'
         'print("abracadabra".find("cad"))'),
        ("key",
         "Cadena de métodos: `texto.strip().lower().replace(\",\", \".\")`. Cada método devuelve un texto "
         "nuevo, así que se pueden encadenar. El original **nunca** cambia."),
        ("h", "Un caso real: normalizar datos de un formulario"),
        ("code",
         'entrada = "  JUAN carlos PÉREZ ;  juan.perez@UNI.EDU.CO  "\n\n'
         'partes = entrada.split(";")\n'
         'nombre = partes[0].strip().title()\n'
         'correo = partes[1].strip().lower()\n\n'
         'print(f"Nombre: {nombre}")\n'
         'print(f"Correo: {correo}")\n'
         'print(f"Usuario: {correo.split(\'@\')[0]}")\n'
         'print(f"Dominio: {correo.split(\'@\')[1]}")'),
        ("tip",
         "Regla de oro con datos de usuario: **siempre** `.strip()` a la entrada. Un espacio invisible "
         "al final es la causa favorita de los `if` que no entran."),
    ],
    "quiz": [
        {
            "q": "¿Qué imprime `print(\"Python\"[1:4])`?",
            "options": ["Pyt", "yth", "ytho"],
            "answer": 1,
            "why": "Empieza en el índice 1 y llega hasta el 4 sin incluirlo: y, t, h.",
            "hint": "El límite derecho nunca se incluye.",
        },
        {
            "q": "`texto = \"  Hola  \"`. ¿Cuál deja `\"hola\"`?",
            "options": ["texto.lower()", "texto.strip().lower()", "texto.replace(\" \", \"\").upper()"],
            "answer": 1,
            "why": "`strip()` quita los espacios de los extremos y `lower()` pasa a minúsculas.",
            "hint": "Hay que hacer dos cosas: quitar espacios y bajar a minúsculas.",
        },
        {
            "q": "¿Qué devuelve `\"a,b,c\".split(\",\")`?",
            "options": ["\"abc\"", "[\"a\", \"b\", \"c\"]", "(\"a\", \"b\", \"c\")"],
            "answer": 1,
            "why": "`split()` siempre devuelve una **lista** de textos.",
            "hint": "El opuesto de `join()`.",
        },
    ],
    "challenges": [{
        "id": "normalizar",
        "title": "Normaliza un nombre",
        "level": "Fácil",
        "points": 25,
        "prompt": ("Partiendo de `entrada = \"  ana MARÍA gómez  \"`:\n\n"
                   "1. `limpio` → sin espacios sobrantes y con cada palabra en mayúscula inicial "
                   "(`Ana María Gómez`).\n"
                   "2. `saludo` → exactamente `Hola, Ana María Gómez`.\n"
                   "3. `palabras` → cuántas palabras tiene el nombre (un número)."),
        "starter": ('entrada = "  ana MARÍA gómez  "\n\n'
                    "limpio = \n"
                    "saludo = \n"
                    "palabras = \n\n"
                    "print(saludo, palabras)"),
        "tests": [
            t_var("limpio", "Ana María Gómez"),
            t_var("saludo", "Hola, Ana María Gómez"),
            t_var("palabras", 3),
        ],
        "hint": "`.strip()` + `.title()` resuelven el punto 1. Para contar: `len(limpio.split())`.",
        "solution": ('entrada = "  ana MARÍA gómez  "\n\n'
                     "limpio = entrada.strip().title()\n"
                     'saludo = f"Hola, {limpio}"\n'
                     "palabras = len(limpio.split())\n\n"
                     "print(saludo, palabras)"),
    }],
}

# --------------------------------------------------------------------------- #
# 5. Entrada y salida
# --------------------------------------------------------------------------- #

L_IO = {
    "id": "entrada_salida",
    "num": 5,
    "icon": "⌨️",
    "title": "Entrada y salida",
    "tag": "Interacción",
    "minutes": 7,
    "subtitle": "Programas que conversan: `input()` para preguntar, `print()` para responder. Y la trampa clásica del texto que parece número.",
    "chips": ["input() simulado", "print(sep, end)", "try / except"],
    "blocks": [
        ("key",
         "En esta app `input()` **sí funciona**: escribe una línea por cada `input()` en la caja "
         "**Entrada** de la sandbox (o usa los ejemplos de abajo, que ya la traen puesta)."),
        ("h", "input() siempre devuelve texto"),
        ("code",
         'nombre = input("¿Cómo te llamas? ")\n'
         'edad_texto = input("¿Qué edad tienes? ")\n\n'
         'print(type(edad_texto))          # ¡str, aunque hayas escrito 30!\n'
         'edad = int(edad_texto)           # hay que convertir\n\n'
         'print(f"Hola {nombre}, el otro año cumples {edad + 1}")',
         "Ana\n29",
         "Este ejemplo ya trae la entrada `Ana` y `29` cargada."),
        ("warn",
         "Sin conversión, `edad_texto + 1` lanza `TypeError`. Y `\"29\" * 3` no da 87: da `292929`."),
        ("h", "Convertir en la misma línea"),
        ("code",
         'nota1 = float(input("Nota 1: "))\n'
         'nota2 = float(input("Nota 2: "))\n\n'
         'promedio = (nota1 + nota2) / 2\n'
         'print(f"Promedio: {promedio:.2f}")',
         "4.5\n3.8"),
        ("h", "print() con más control"),
        ("code",
         'print("a", "b", "c")                 # separador por defecto: espacio\n'
         'print("a", "b", "c", sep=" | ")\n'
         'print("cargando", end="...")\n'
         'print("listo")\n'
         'print("-" * 30)                       # separador visual\n'
         'print(f"{\'Materia\':<20}{\'Nota\':>6}")\n'
         'print(f"{\'Bases de datos\':<20}{4.5:>6.2f}")\n'
         'print(f"{\'Estadística\':<20}{3.9:>6.2f}")',
         "", "Con `<`, `>` y `^` puedes armar tablas de texto decentes sin librerías."),
        ("h", "Validar lo que entra (primer vistazo a try/except)"),
        ("code",
         'dato = input("Escribe un número: ")\n\n'
         'try:\n'
         '    numero = float(dato)\n'
         '    print(f"El doble es {numero * 2}")\n'
         'except ValueError:\n'
         '    print(f"«{dato}» no es un número válido")',
         "cuarenta",
         "Cambia la entrada a `40` en la sandbox y compara el resultado."),
        ("tip",
         "Nunca confíes en la entrada del usuario. `float(input())` directo se cae con el primer "
         "dedazo; envolverlo en `try/except` convierte un crash en un mensaje amable."),
    ],
    "quiz": [
        {
            "q": "Si el usuario escribe `10`, ¿qué tipo tiene `x = input()`?",
            "options": ["int", "str", "float"],
            "answer": 1,
            "why": "`input()` devuelve SIEMPRE `str`. Si necesitas número, conviértelo.",
            "hint": "Pruébalo con `type(x)`.",
        },
        {
            "q": "¿Qué imprime `print(\"A\", \"B\", sep=\"\")`?",
            "options": ["A B", "AB", "A,B"],
            "answer": 1,
            "why": "`sep` define qué va entre los valores; vacío los pega.",
            "hint": "Por defecto `sep` es un espacio.",
        },
    ],
    "challenges": [{
        "id": "promedio_io",
        "title": "Boletín express",
        "level": "Fácil",
        "points": 25,
        "stdin": "Camilo\n4.5\n3.8\n4.0",
        "prompt": ("Lee **cuatro** líneas con `input()`: un nombre y tres notas. Imprime una línea que "
                   "contenga el nombre y el promedio con **dos decimales**.\n\n"
                   "Con la entrada de prueba (`Camilo`, `4.5`, `3.8`, `4.0`) debe aparecer `Camilo` y `4.10`."),
        "starter": ("nombre = input()\n"
                    "n1 = float(input())\n"
                    "n2 = \n"
                    "n3 = \n\n"
                    "promedio = \n"
                    "print()"),
        "tests": [
            t_stdout_contains("Camilo", "Imprimes el nombre"),
            t_stdout_contains("4.10", "El promedio sale con dos decimales"),
            t_rerun_contains("Ana\n3.0\n3.0\n3.0", "3.00",
                             "Funciona también con otras notas (Ana, 3.0 x3 → 3.00)"),
        ],
        "hint": "El promedio es `(n1 + n2 + n3) / 3` y el formato `f\"{promedio:.2f}\"`.",
        "solution": ("nombre = input()\n"
                     "n1 = float(input())\n"
                     "n2 = float(input())\n"
                     "n3 = float(input())\n\n"
                     "promedio = (n1 + n2 + n3) / 3\n"
                     'print(f"{nombre}: promedio {promedio:.2f}")'),
    }],
}

# --------------------------------------------------------------------------- #
# 6. Condicionales
# --------------------------------------------------------------------------- #

L_CONDICIONALES = {
    "id": "condicionales",
    "num": 6,
    "icon": "🔀",
    "title": "Condicionales",
    "tag": "Control",
    "minutes": 10,
    "subtitle": "Que el programa decida. Aquí entra la indentación, que en Python no es estética: es sintaxis.",
    "chips": ["if / elif / else", "Indentación", "Ternario"],
    "blocks": [
        ("h", "La estructura"),
        ("show",
         "if condicion:\n"
         "    # bloque que se ejecuta si es True (4 espacios)\n"
         "elif otra_condicion:\n"
         "    # se evalúa solo si la anterior fue False\n"
         "else:\n"
         "    # si ninguna se cumplió\n"),
        ("code",
         'nota = 3.4\n\n'
         'if nota >= 4.5:\n'
         '    print("Excelente")\n'
         'elif nota >= 3.0:\n'
         '    print("Aprobado")\n'
         'else:\n'
         '    print("Reprobado")\n\n'
         'print("Esta línea siempre se ejecuta (no está indentada)")',
         "", "Cambia el valor de `nota` y vuelve a ejecutar. Prueba 4.9, 3.0 y 2.9."),
        ("key",
         "El orden importa: `elif` solo se evalúa si lo anterior fue falso. Por eso basta con "
         "`nota >= 3.0` en el segundo caso: si llegó ahí, ya sabemos que es menor a 4.5."),
        ("h", "La indentación es sintaxis"),
        ("cmp",
         'if nota >= 3.0:\nprint("Aprobado")',
         'if nota >= 3.0:\n    print("Aprobado")',
         "Sin sangría, Python lanza `IndentationError`. Usa siempre 4 espacios y no mezcles tabuladores."),
        ("h", "Condiciones compuestas y validación"),
        ("code",
         'edad = 26\n'
         'promedio = 4.1\n'
         'tiene_pregrado = True\n\n'
         'if tiene_pregrado and promedio >= 3.8 and edad >= 21:\n'
         '    print("Cumple para la beca")\n'
         'else:\n'
         '    print("No cumple todavía")\n\n'
         'nota = 6.2\n'
         'if not (0 <= nota <= 5):\n'
         '    print("Fuera de rango")'),
        ("h", "Guard clauses: adiós a las escaleras de ifs"),
        ("cmp",
         'if usuario != "":\n'
         '    if clave != "":\n'
         '        if len(clave) >= 8:\n'
         '            print("Acceso concedido")\n'
         '        else:\n'
         '            print("Clave corta")\n'
         '    else:\n'
         '        print("Falta clave")\n'
         'else:\n'
         '    print("Falta usuario")',
         'if usuario == "":\n'
         '    print("Falta usuario")\n'
         'elif clave == "":\n'
         '    print("Falta clave")\n'
         'elif len(clave) < 8:\n'
         '    print("Clave corta")\n'
         'else:\n'
         '    print("Acceso concedido")',
         "Descarta primero los casos malos y deja el caso bueno al final, sin anidar. Se lee de arriba a abajo."),
        ("h", "El ternario (una línea)"),
        ("code",
         'nota = 3.2\n'
         'estado = "Aprobado" if nota >= 3.0 else "Reprobado"\n'
         'print(estado)\n\n'
         'cantidad = 1\n'
         'print(f"{cantidad} estudiante" + ("s" if cantidad != 1 else ""))'),
        ("tip",
         "Usa el ternario solo cuando quepa cómodo en una línea. Si necesitas un `elif`, vuelve al `if` normal."),
        ("warn",
         "Comparar con `==` textos que vienen de `input()` falla por espacios y mayúsculas. "
         "Normaliza primero: `respuesta = input().strip().lower()` y luego `if respuesta == \"si\":`."),
    ],
    "quiz": [
        {
            "q": "Con `nota = 4.6`, ¿qué imprime el ejemplo de `if nota >= 4.5 / elif nota >= 3.0 / else`?",
            "options": ["Excelente", "Excelente y Aprobado", "Aprobado"],
            "answer": 0,
            "why": "En cuanto una rama se cumple, las demás se saltan.",
            "hint": "`elif` no se evalúa si el `if` ya fue verdadero.",
        },
        {
            "q": "¿Qué error da un bloque `if` sin sangría en la línea siguiente?",
            "options": ["SyntaxError", "IndentationError", "Ninguno, Python lo tolera"],
            "answer": 1,
            "why": "Python usa la sangría para delimitar bloques; sin ella no sabe qué va dentro.",
            "hint": "Pruébalo en la sandbox: el mensaje lo dice literalmente.",
        },
        {
            "q": "¿Cuál es la forma correcta de validar que `x` esté entre 0 y 5?",
            "options": ["if 0 <= x <= 5:", "if x >= 0 or x <= 5:", "if x between 0 and 5:"],
            "answer": 0,
            "why": "Python permite encadenar comparaciones. Con `or` sería verdadero para cualquier número.",
            "hint": "Piensa qué pasa con x = 100 en la opción del `or`.",
        },
    ],
    "challenges": [{
        "id": "clasificar_nota",
        "title": "Clasificador de notas",
        "level": "Medio",
        "points": 30,
        "stdin": "4.8",
        "prompt": ("Lee una nota con `input()` y imprime **exactamente** una de estas palabras:\n\n"
                   "- `Excelente` si la nota es 4.5 o más\n"
                   "- `Aprobado` si es 3.0 o más (pero menor a 4.5)\n"
                   "- `Reprobado` si es menor a 3.0\n"
                   "- `Fuera de rango` si no está entre 0 y 5\n\n"
                   "Se probará con varias entradas distintas, así que la lógica debe servir para todas."),
        "starter": ("nota = float(input())\n\n"
                    "if \n"
                    "    print()\n"),
        "tests": [
            t_stdout_contains("Excelente", "Con 4.8 dice «Excelente»"),
            t_rerun_contains("3.2", "Aprobado"),
            t_rerun_contains("2.0", "Reprobado"),
            t_rerun_contains("7", "Fuera de rango"),
            t_rerun_contains("-1", "Fuera de rango"),
        ],
        "hint": "Valida primero el rango (`if nota < 0 or nota > 5:`) y después clasifica con `elif`.",
        "solution": ("nota = float(input())\n\n"
                     "if nota < 0 or nota > 5:\n"
                     '    print("Fuera de rango")\n'
                     "elif nota >= 4.5:\n"
                     '    print("Excelente")\n'
                     "elif nota >= 3.0:\n"
                     '    print("Aprobado")\n'
                     "else:\n"
                     '    print("Reprobado")'),
    }],
}

# --------------------------------------------------------------------------- #
# 7. Bucles
# --------------------------------------------------------------------------- #

L_BUCLES = {
    "id": "bucles",
    "num": 7,
    "icon": "🔁",
    "title": "Bucles",
    "tag": "Control",
    "minutes": 12,
    "subtitle": "Repetir sin repetirte. `for` cuando sabes cuántas veces; `while` cuando dependes de una condición.",
    "chips": ["for / range", "while", "enumerate · zip"],
    "blocks": [
        ("h", "for + range"),
        ("code",
         'for i in range(5):          # 0, 1, 2, 3, 4\n'
         '    print("Vuelta", i)\n\n'
         'print("---")\n'
         'for i in range(1, 6):       # desde 1 hasta 5\n'
         '    print(i, "al cuadrado es", i ** 2)\n\n'
         'print("---")\n'
         'for i in range(10, 0, -2):  # inicio, fin, paso\n'
         '    print(i, end=" ")'),
        ("key",
         "`range(a, b)` **no incluye** `b`. `range(5)` va de 0 a 4: son 5 elementos, que es lo que suele importar."),
        ("h", "for sobre cualquier colección"),
        ("code",
         'materias = ["Bases de datos", "Estadística", "Ética"]\n\n'
         'for materia in materias:\n'
         '    print("-", materia)\n\n'
         'print("---")\n'
         'for letra in "Python":\n'
         '    print(letra, end="·")'),
        ("h", "enumerate y zip: los dos que separan al novato del que sabe"),
        ("cmp",
         'for i in range(len(materias)):\n'
         '    print(i + 1, materias[i])',
         'for i, materia in enumerate(materias, start=1):\n'
         '    print(i, materia)',
         "`enumerate` te da posición y valor al tiempo. `start=1` evita el `i + 1` por todas partes."),
        ("code",
         'materias = ["Bases de datos", "Estadística", "Ética"]\n'
         'notas = [4.5, 3.8, 4.9]\n\n'
         'for materia, nota in zip(materias, notas):\n'
         '    print(f"{materia:<18} {nota:>5.2f}")'),
        ("h", "Acumuladores: el patrón que más se repite"),
        ("code",
         'notas = [4.5, 3.8, 4.9, 2.7, 3.3]\n\n'
         'suma = 0\n'
         'aprobadas = 0\n'
         'mayor = notas[0]\n\n'
         'for nota in notas:\n'
         '    suma += nota\n'
         '    if nota >= 3.0:\n'
         '        aprobadas += 1\n'
         '    if nota > mayor:\n'
         '        mayor = nota\n\n'
         'print(f"Promedio: {suma / len(notas):.2f}")\n'
         'print(f"Aprobadas: {aprobadas} de {len(notas)}")\n'
         'print(f"Mejor nota: {mayor}")\n\n'
         '# Python ya trae atajos para lo mismo:\n'
         'print(sum(notas) / len(notas), max(notas), min(notas))'),
        ("h", "while: repetir mientras se cumpla algo"),
        ("code",
         'saldo = 100000\n'
         'retiro = 30000\n'
         'operaciones = 0\n\n'
         'while saldo >= retiro:\n'
         '    saldo -= retiro\n'
         '    operaciones += 1\n'
         '    print(f"Retiro {operaciones}: queda {saldo}")\n\n'
         'print("Saldo final:", saldo)'),
        ("warn",
         "Si dentro del `while` no cambias nada de la condición, el bucle es infinito. "
         "La sandbox lo corta a los 8 segundos, pero en tu máquina toca `Ctrl+C`."),
        ("h", "break y continue"),
        ("code",
         'for numero in [4, 8, 15, 16, 23, 42]:\n'
         '    if numero % 2 != 0:\n'
         '        continue           # salta al siguiente\n'
         '    if numero > 20:\n'
         '        print("Encontrado uno grande:", numero)\n'
         '        break              # sale del bucle\n'
         '    print("Par pequeño:", numero)'),
        ("h", "Comprensiones de lista (el atajo elegante)"),
        ("code",
         'notas = [4.5, 3.8, 4.9, 2.7, 3.3]\n\n'
         'sobre_tres = [n for n in notas if n >= 3.0]\n'
         'en_porcentaje = [round(n / 5 * 100) for n in notas]\n\n'
         'print(sobre_tres)\n'
         'print(en_porcentaje)'),
        ("tip",
         "Una comprensión se lee así: **qué guardo** · **de dónde** · **con qué filtro**. "
         "Si no cabe cómoda en una línea, usa un `for` normal: la claridad gana."),
        ("bad",
         "No modifiques una lista mientras la recorres (`for x in lista: lista.remove(x)`): se salta elementos. "
         "Construye una lista nueva con una comprensión."),
    ],
    "quiz": [
        {
            "q": "¿Cuántas veces se ejecuta `for i in range(3, 8):`?",
            "options": ["4", "5", "8"],
            "answer": 1,
            "why": "Va 3, 4, 5, 6, 7 → 5 iteraciones (el 8 no entra).",
            "hint": "Resta el inicio del fin: 8 - 3.",
        },
        {
            "q": "¿Cuál es la forma pythónica de recorrer con índice y valor?",
            "options": ["for i in range(len(xs)):", "for i, x in enumerate(xs):", "for x in xs.index():"],
            "answer": 1,
            "why": "`enumerate` entrega la pareja (posición, valor) sin indexar a mano.",
            "hint": "Una de las tres ni siquiera existe.",
        },
        {
            "q": "¿Qué hace `continue` dentro de un bucle?",
            "options": ["Termina el bucle", "Salta a la siguiente iteración", "Reinicia el bucle desde cero"],
            "answer": 1,
            "why": "`continue` salta el resto del cuerpo; `break` es el que termina el bucle.",
            "hint": "El que termina es el otro.",
        },
    ],
    "challenges": [{
        "id": "ventas",
        "title": "Reporte de ventas",
        "level": "Medio",
        "points": 30,
        "prompt": ("Con la lista `ventas` del editor:\n\n"
                   "1. `total` → suma de todas las ventas.\n"
                   "2. `mayor` → la venta más alta.\n"
                   "3. `sobre_200` → cuántas ventas superan 200.\n"
                   "4. Imprime **una línea por venta** con su número de día (usa `enumerate`)."),
        "starter": ("ventas = [120, 340, 90, 500, 275, 60, 410]\n\n"
                    "total = 0\n"
                    "mayor = ventas[0]\n"
                    "sobre_200 = 0\n\n"
                    "for i, venta in enumerate(ventas, start=1):\n"
                    "    pass\n\n"
                    "print(total, mayor, sobre_200)"),
        "height": 260,
        "tests": [
            t_var("total", 1795),
            t_var("mayor", 500),
            t_var("sobre_200", 4),
            t_custom("Imprimes una línea por cada venta", _check_siete_lineas),
        ],
        "hint": ("Dentro del `for`: acumula con `total += venta`, actualiza `mayor` con un `if` "
                 "y cuenta con otro `if venta > 200`. Imprime con `print(f\"Día {i}: {venta}\")`."),
        "solution": ("ventas = [120, 340, 90, 500, 275, 60, 410]\n\n"
                     "total = 0\n"
                     "mayor = ventas[0]\n"
                     "sobre_200 = 0\n\n"
                     "for i, venta in enumerate(ventas, start=1):\n"
                     "    total += venta\n"
                     "    if venta > mayor:\n"
                     "        mayor = venta\n"
                     "    if venta > 200:\n"
                     "        sobre_200 += 1\n"
                     '    print(f"Dia {i}: {venta}")\n\n'
                     'print(f"Total {total} | Mayor {mayor} | Sobre 200: {sobre_200}")'),
    }],
}

# --------------------------------------------------------------------------- #
# 8. Listas y tuplas
# --------------------------------------------------------------------------- #

L_LISTAS = {
    "id": "listas",
    "num": 8,
    "icon": "📚",
    "title": "Listas y tuplas",
    "tag": "Colecciones",
    "minutes": 12,
    "subtitle": "La lista es la colección que más vas a usar. La tupla es su versión inmutable, y hay una trampa de copias que confunde a todo el mundo.",
    "chips": ["append · sort · slicing", "copia vs referencia", "tuplas"],
    "blocks": [
        ("h", "Lo básico"),
        ("code",
         'materias = ["Bases de datos", "Estadística", "Ética"]\n\n'
         'print(materias[0], materias[-1])\n'
         'print(len(materias))\n'
         'print(materias[0:2])\n'
         'print("Ética" in materias)\n\n'
         'materias[1] = "Estadística aplicada"   # las listas SÍ se modifican\n'
         'print(materias)'),
        ("h", "Métodos que debes tener en los dedos"),
        ("table",
         ["Método", "Qué hace", "¿Modifica la lista?"],
         [
             ["`.append(x)`", "Agrega al final", "Sí"],
             ["`.insert(i, x)`", "Inserta en la posición i", "Sí"],
             ["`.extend(otra)`", "Agrega todos los de otra lista", "Sí"],
             ["`.remove(x)`", "Quita la **primera** aparición de x", "Sí"],
             ["`.pop(i)`", "Saca y devuelve el elemento i (último si no indicas)", "Sí"],
             ["`.sort()`", "Ordena en el sitio", "Sí → devuelve `None`"],
             ["`sorted(lista)`", "Devuelve una lista **nueva** ordenada", "No"],
             ["`.reverse()`", "Invierte en el sitio", "Sí"],
             ["`.count(x)` / `.index(x)`", "Cuenta / busca posición", "No"],
         ]),
        ("code",
         'notas = [4.5, 3.8, 4.9, 2.7]\n\n'
         'notas.append(3.3)\n'
         'notas.insert(0, 5.0)\n'
         'notas.remove(2.7)\n'
         'ultima = notas.pop()\n\n'
         'print(notas, "| saqué:", ultima)\n'
         'print("ordenada nueva:", sorted(notas, reverse=True))\n'
         'print("la original sigue igual:", notas)\n\n'
         'notas.sort()\n'
         'print("ahora sí ordenada:", notas)'),
        ("warn",
         "`lista = lista.sort()` es un error clásico: `sort()` devuelve `None`, así que te quedas sin lista. "
         "O usas `lista.sort()` solo, o `nueva = sorted(lista)`."),
        ("h", "La trampa de las copias"),
        ("code",
         'original = [1, 2, 3]\n'
         'alias = original          # NO es una copia: es otro nombre para lo mismo\n'
         'copia = original.copy()   # esto sí es una copia (o original[:])\n\n'
         'alias.append(99)\n'
         'copia.append(-1)\n\n'
         'print("original:", original)\n'
         'print("alias   :", alias)\n'
         'print("copia   :", copia)',
         "", "Mira cómo el 99 aparece también en `original`."),
        ("key",
         "Las listas se pasan **por referencia**. Si una función recibe una lista y le hace `append`, "
         "la lista de afuera también cambia. A veces lo quieres; cuando no, pasa `lista.copy()`."),
        ("h", "Tuplas: como listas, pero inmutables"),
        ("code",
         'punto = (4.5, 3.8)\n'
         'print(punto[0], len(punto))\n\n'
         'nota, asistencia = punto        # desempaquetado\n'
         'print(nota, asistencia)\n\n'
         'estudiante = ("Ana", 29, "Especialización")\n'
         'nombre, edad, programa = estudiante\n'
         'print(f"{nombre} ({edad}) - {programa}")\n\n'
         '# punto[0] = 9  ->  TypeError: no se puede modificar una tupla'),
        ("tip",
         "Usa **tupla** cuando el conjunto de valores no debe cambiar (una coordenada, una fila leída de la "
         "base de datos) y **lista** cuando vas a agregar o quitar elementos."),
        ("h", "Listas de listas (una tabla, básicamente)"),
        ("code",
         'tabla = [\n'
         '    ["Ana", 4.5, 4.0],\n'
         '    ["Luis", 3.0, 2.8],\n'
         '    ["Sara", 4.9, 5.0],\n'
         ']\n\n'
         'print(tabla[0])       # una fila\n'
         'print(tabla[0][1])    # una celda\n\n'
         'for fila in tabla:\n'
         '    nombre = fila[0]\n'
         '    promedio = (fila[1] + fila[2]) / 2\n'
         '    print(f"{nombre:<6} {promedio:.2f}")'),
        ("tip",
         "Si te encuentras escribiendo `fila[0]`, `fila[1]`, `fila[2]` por todas partes, es señal de que "
         "necesitas un **diccionario** (siguiente lección): `fila[\"nombre\"]` se entiende sin contar posiciones."),
    ],
    "quiz": [
        {
            "q": "`xs = [3, 1, 2]`. ¿Qué vale `ys` tras `ys = xs.sort()`?",
            "options": ["[1, 2, 3]", "None", "[3, 1, 2]"],
            "answer": 1,
            "why": "`sort()` ordena en el sitio y devuelve `None`. Para obtener una lista nueva usa `sorted()`.",
            "hint": "Ojo con lo que *devuelve*, no con lo que hace.",
        },
        {
            "q": "`a = [1, 2]`, `b = a`, `b.append(3)`. ¿Qué vale `a`?",
            "options": ["[1, 2]", "[1, 2, 3]", "Error"],
            "answer": 1,
            "why": "`b = a` no copia: ambos nombres apuntan a la misma lista.",
            "hint": "Recuerda el ejemplo del alias.",
        },
        {
            "q": "¿Cuál de estas operaciones NO se puede hacer con una tupla?",
            "options": ["Recorrerla con for", "Leer `t[0]`", "Hacer `t[0] = 5`"],
            "answer": 2,
            "why": "Las tuplas son inmutables: se leen y se recorren, pero no se modifican.",
            "hint": "Inmutable = no se puede cambiar.",
        },
    ],
    "challenges": [{
        "id": "inventario",
        "title": "Inventario de laboratorio",
        "level": "Medio",
        "points": 30,
        "prompt": ("Partiendo de `inventario = [\"teclado\", \"mouse\", \"monitor\"]`:\n\n"
                   "1. Agrega `\"webcam\"` al final y quita `\"mouse\"`.\n"
                   "2. Crea `ordenado` con la lista **ordenada alfabéticamente**, sin alterar `inventario`.\n"
                   "3. Crea `total` con la cantidad de equipos."),
        "starter": ('inventario = ["teclado", "mouse", "monitor"]\n\n'
                    "# 1)\n\n"
                    "ordenado = \n"
                    "total = \n\n"
                    "print(inventario, ordenado, total)"),
        "tests": [
            t_var("inventario", ["teclado", "monitor", "webcam"]),
            t_var("ordenado", ["monitor", "teclado", "webcam"]),
            t_var("total", 3),
        ],
        "hint": "`append()` agrega, `remove()` quita y `sorted()` devuelve una copia ordenada.",
        "solution": ('inventario = ["teclado", "mouse", "monitor"]\n\n'
                     'inventario.append("webcam")\n'
                     'inventario.remove("mouse")\n\n'
                     "ordenado = sorted(inventario)\n"
                     "total = len(inventario)\n\n"
                     "print(inventario, ordenado, total)"),
    }],
}

# --------------------------------------------------------------------------- #
# 9. Diccionarios y conjuntos
# --------------------------------------------------------------------------- #

L_DICCIONARIOS = {
    "id": "diccionarios",
    "num": 9,
    "icon": "🗂️",
    "title": "Diccionarios y conjuntos",
    "tag": "Colecciones",
    "minutes": 12,
    "subtitle": "Un diccionario es una **fila de una tabla**: cada dato tiene nombre. Y un conjunto elimina duplicados sin que hagas nada.",
    "chips": ["clave: valor", ".get()", "set()"],
    "blocks": [
        ("h", "Crear y leer"),
        ("code",
         'estudiante = {\n'
         '    "nombre": "Ana Gómez",\n'
         '    "edad": 29,\n'
         '    "programa": "Especialización en BD",\n'
         '    "notas": [4.5, 3.8, 4.9],\n'
         '}\n\n'
         'print(estudiante["nombre"])\n'
         'print(estudiante["notas"][0])\n'
         'print(len(estudiante))\n'
         'print("edad" in estudiante)'),
        ("code",
         'estudiante = {"nombre": "Ana", "edad": 29}\n\n'
         'print(estudiante.get("telefono"))                  # None, no explota\n'
         'print(estudiante.get("telefono", "sin registrar")) # con valor por defecto\n'
         '# print(estudiante["telefono"])  ->  KeyError'),
        ("key",
         "`dic[clave]` explota si la clave no existe; `dic.get(clave, valor_por_defecto)` no. "
         "Con datos que vienen de afuera (formularios, APIs, bases de datos), usa siempre `.get()`."),
        ("h", "Modificar"),
        ("code",
         'estudiante = {"nombre": "Ana", "edad": 29}\n\n'
         'estudiante["semestre"] = 2          # agrega\n'
         'estudiante["edad"] = 30             # actualiza\n'
         'estudiante.update({"activo": True, "edad": 31})\n'
         'quitado = estudiante.pop("semestre")\n\n'
         'print(estudiante)\n'
         'print("quité:", quitado)'),
        ("h", "Recorrer"),
        ("code",
         'notas = {"Bases de datos": 4.5, "Estadística": 3.8, "Ética": 4.9}\n\n'
         'for materia in notas:                 # recorre las CLAVES\n'
         '    print(materia)\n\n'
         'print("---")\n'
         'for materia, nota in notas.items():   # clave y valor\n'
         '    print(f"{materia:<18} {nota:>5.2f}")\n\n'
         'print("---")\n'
         'print(list(notas.keys()))\n'
         'print(list(notas.values()))\n'
         'print(f"Promedio: {sum(notas.values()) / len(notas):.2f}")'),
        ("h", "Lista de diccionarios: el formato de datos más común del mundo"),
        ("code",
         'estudiantes = [\n'
         '    {"nombre": "Ana", "notas": [4.5, 3.8, 4.9]},\n'
         '    {"nombre": "Luis", "notas": [3.0, 2.8, 3.4]},\n'
         '    {"nombre": "Sara", "notas": [4.9, 4.7, 5.0]},\n'
         ']\n\n'
         'for est in estudiantes:\n'
         '    promedio = sum(est["notas"]) / len(est["notas"])\n'
         '    estado = "Aprobado" if promedio >= 3.0 else "Reprobado"\n'
         '    print(f\'{est["nombre"]:<6} {promedio:.2f}  {estado}\')',
         "", "Así se ve un resultado de consulta SQL cuando llega a Python: una lista de filas con nombre."),
        ("tip",
         "Contar cosas con diccionario es un patrón que vale oro:\n"
         "`conteo[palabra] = conteo.get(palabra, 0) + 1`"),
        ("code",
         'texto = "el dato el dato y el resultado"\n'
         'conteo = {}\n\n'
         'for palabra in texto.split():\n'
         '    conteo[palabra] = conteo.get(palabra, 0) + 1\n\n'
         'print(conteo)\n\n'
         '# ordenar por frecuencia (de mayor a menor)\n'
         'ranking = sorted(conteo.items(), key=lambda par: par[1], reverse=True)\n'
         'print(ranking)'),
        ("h", "Conjuntos (set): únicos y operaciones de conjuntos"),
        ("code",
         'inscritos = ["Ana", "Luis", "Ana", "Sara", "Luis", "Ana"]\n'
         'unicos = set(inscritos)\n'
         'print(unicos, len(unicos))\n\n'
         'grupo_a = {"Ana", "Luis", "Sara"}\n'
         'grupo_b = {"Sara", "Pedro"}\n\n'
         'print("En ambos:", grupo_a & grupo_b)\n'
         'print("En alguno:", grupo_a | grupo_b)\n'
         'print("Solo en A:", grupo_a - grupo_b)\n'
         'print("¿Sara está?", "Sara" in grupo_a)'),
        ("tip",
         "Para preguntar «¿está este dato en la colección?» miles de veces, un `set` es muchísimo más "
         "rápido que una lista. Y `list(set(datos))` quita duplicados en una línea (aunque pierde el orden)."),
        ("warn",
         "Las claves de un diccionario y los elementos de un set deben ser **inmutables**: sirven textos, "
         "números y tuplas; **no** listas ni diccionarios."),
    ],
    "quiz": [
        {
            "q": "¿Qué pasa con `d = {\"a\": 1}` al ejecutar `d[\"b\"]`?",
            "options": ["Devuelve None", "Lanza KeyError", "Crea la clave con valor None"],
            "answer": 1,
            "why": "Leer una clave inexistente lanza `KeyError`. Para evitarlo: `d.get(\"b\")`.",
            "hint": "Hay un método que sí devuelve None.",
        },
        {
            "q": "¿Cuál recorre clave y valor al tiempo?",
            "options": ["for k in d:", "for k, v in d.items():", "for v in d.values():"],
            "answer": 1,
            "why": "`.items()` entrega las parejas (clave, valor).",
            "hint": "Necesitas dos variables en el for.",
        },
        {
            "q": "¿Qué imprime `len(set([1, 2, 2, 3, 3, 3]))`?",
            "options": ["6", "3", "1"],
            "answer": 1,
            "why": "El conjunto elimina duplicados: quedan 1, 2 y 3.",
            "hint": "Cuenta cuántos valores distintos hay.",
        },
    ],
    "challenges": [{
        "id": "promedios",
        "title": "Promedios por estudiante",
        "level": "Medio",
        "points": 35,
        "prompt": ("Con la lista `estudiantes` del editor:\n\n"
                   "1. Construye el diccionario `promedios` con la forma `{\"Ana\": 4.4, ...}`, "
                   "**redondeado a 2 decimales**.\n"
                   "2. Guarda en `mejor` el nombre de quien tiene el promedio más alto."),
        "starter": ("estudiantes = [\n"
                    '    {"nombre": "Ana", "notas": [4.5, 3.8, 4.9]},\n'
                    '    {"nombre": "Luis", "notas": [3.0, 2.8, 3.4]},\n'
                    '    {"nombre": "Sara", "notas": [4.9, 4.7, 5.0]},\n'
                    "]\n\n"
                    "promedios = {}\n"
                    "for est in estudiantes:\n"
                    "    pass\n\n"
                    "mejor = \n\n"
                    "print(promedios, mejor)"),
        "height": 280,
        "tests": [
            t_custom("`promedios` tiene los 3 promedios correctos", _check_promedios),
            t_var("mejor", "Sara"),
        ],
        "hint": ("Dentro del for: `promedios[est[\"nombre\"]] = round(sum(est[\"notas\"]) / len(est[\"notas\"]), 2)`.\n\n"
                 "Para el mejor: `max(promedios, key=promedios.get)`  (o un bucle con una variable `mejor`)."),
        "solution": ("estudiantes = [\n"
                     '    {"nombre": "Ana", "notas": [4.5, 3.8, 4.9]},\n'
                     '    {"nombre": "Luis", "notas": [3.0, 2.8, 3.4]},\n'
                     '    {"nombre": "Sara", "notas": [4.9, 4.7, 5.0]},\n'
                     "]\n\n"
                     "promedios = {}\n"
                     "for est in estudiantes:\n"
                     '    notas = est["notas"]\n'
                     '    promedios[est["nombre"]] = round(sum(notas) / len(notas), 2)\n\n'
                     "mejor = max(promedios, key=promedios.get)\n\n"
                     "print(promedios, mejor)"),
    }],
}

# --------------------------------------------------------------------------- #
# 10. Funciones
# --------------------------------------------------------------------------- #

L_FUNCIONES = {
    "id": "funciones",
    "num": 10,
    "icon": "🧩",
    "title": "Funciones",
    "tag": "Meta del curso",
    "minutes": 15,
    "subtitle": "El salto de calidad: dejas de repetir código y empiezas a construir piezas con nombre, probables y reutilizables.",
    "chips": ["def · return", "Parámetros por defecto", "Ámbito", "lambda"],
    "blocks": [
        ("md",
         "Una función es un bloque con **nombre**, que recibe **entradas** (parámetros) y devuelve una "
         "**salida** (`return`). Cuando copies y pegues código por segunda vez, eso es una función esperando a nacer."),
        ("h", "Anatomía"),
        ("show",
         "def nombre_de_la_funcion(parametro1, parametro2):\n"
         '    """Qué hace (docstring, opcional pero recomendado)."""\n'
         "    resultado = parametro1 + parametro2\n"
         "    return resultado\n"),
        ("code",
         'def area_rectangulo(base, altura):\n'
         '    """Devuelve el área de un rectángulo."""\n'
         '    return base * altura\n\n\n'
         'print(area_rectangulo(3, 4))\n'
         'print(area_rectangulo(2.5, 4))\n'
         'print(area_rectangulo(altura=10, base=2))   # argumentos con nombre\n'
         'print(area_rectangulo.__doc__)'),
        ("key",
         "`return` **devuelve** un valor para poder seguir usándolo; `print` solo **muestra**. "
         "Si tu función solo imprime, no puedes reutilizar su resultado en otro cálculo."),
        ("cmp",
         'def promedio(notas):\n'
         '    print(sum(notas) / len(notas))\n\n'
         '# no sirve para nada más:\n'
         '# total = promedio(xs) * 2  ->  TypeError',
         'def promedio(notas):\n'
         '    return sum(notas) / len(notas)\n\n'
         'print(promedio([4.0, 5.0]))\n'
         'total = promedio([4.0, 5.0]) * 2',
         "Calcular y mostrar son responsabilidades distintas. La función calcula; quien la llama decide si imprime, guarda o suma."),
        ("h", "Parámetros por defecto"),
        ("code",
         'def clasificar(nota, minimo_aprobatorio=3.0):\n'
         '    if nota >= minimo_aprobatorio:\n'
         '        return "Aprobado"\n'
         '    return "Reprobado"\n\n\n'
         'print(clasificar(3.2))                          # usa el 3.0 por defecto\n'
         'print(clasificar(3.2, minimo_aprobatorio=3.5))  # posgrado exigente\n'
         'print(clasificar(3.2, 4.0))'),
        ("warn",
         "Nunca uses una lista o un diccionario como valor por defecto (`def f(xs=[])`): ese objeto se "
         "crea **una sola vez** y se comparte entre llamadas. Usa `def f(xs=None):` y dentro "
         "`if xs is None: xs = []`."),
        ("code",
         '# El clásico bug del argumento mutable\n'
         'def agregar_mal(item, bolsa=[]):\n'
         '    bolsa.append(item)\n'
         '    return bolsa\n\n'
         'print(agregar_mal("a"))\n'
         'print(agregar_mal("b"))   # ¡aparece la "a" otra vez!\n\n\n'
         'def agregar_bien(item, bolsa=None):\n'
         '    if bolsa is None:\n'
         '        bolsa = []\n'
         '    bolsa.append(item)\n'
         '    return bolsa\n\n'
         'print(agregar_bien("a"))\n'
         'print(agregar_bien("b"))'),
        ("h", "Devolver varios valores"),
        ("code",
         'def estadisticas(notas):\n'
         '    return min(notas), max(notas), sum(notas) / len(notas)\n\n\n'
         'menor, mayor, media = estadisticas([4.5, 3.8, 4.9, 2.7])\n'
         'print(f"min={menor} max={mayor} media={media:.2f}")\n\n'
         'print(estadisticas([1, 2, 3]))   # en realidad devuelve una tupla'),
        ("h", "Ámbito: qué ve cada quien"),
        ("code",
         'contador = 0            # variable global\n\n'
         'def sumar_uno(valor):\n'
         '    contador = valor + 1    # esta "contador" es LOCAL, otra distinta\n'
         '    return contador\n\n\n'
         'print(sumar_uno(10))\n'
         'print("la global no cambió:", contador)'),
        ("tip",
         "Regla práctica: una función debería depender solo de sus **parámetros** y comunicarse solo por "
         "su **return**. Si necesitas un dato de afuera, pásalo como argumento; evita `global`."),
        ("h", "*args y **kwargs (cuando no sabes cuántos argumentos vienen)"),
        ("code",
         'def promedio(*notas):\n'
         '    if not notas:\n'
         '        return 0.0\n'
         '    return sum(notas) / len(notas)\n\n\n'
         'print(promedio(4.5, 3.8))\n'
         'print(promedio(4.5, 3.8, 4.9, 5.0))\n'
         'print(promedio())\n\n\n'
         'def registrar(nombre, **datos):\n'
         '    print(f"Estudiante: {nombre}")\n'
         '    for clave, valor in datos.items():\n'
         '        print(f"  - {clave}: {valor}")\n\n\n'
         'registrar("Ana", edad=29, programa="BD", activo=True)'),
        ("h", "lambda: funciones de una línea, sin nombre"),
        ("code",
         'estudiantes = [\n'
         '    {"nombre": "Ana", "promedio": 4.4},\n'
         '    {"nombre": "Luis", "promedio": 3.1},\n'
         '    {"nombre": "Sara", "promedio": 4.9},\n'
         ']\n\n'
         '# ordenar por promedio, de mayor a menor\n'
         'ranking = sorted(estudiantes, key=lambda e: e["promedio"], reverse=True)\n'
         'for i, e in enumerate(ranking, start=1):\n'
         '    print(i, e["nombre"], e["promedio"])\n\n'
         'aprobados = list(filter(lambda e: e["promedio"] >= 3.0, estudiantes))\n'
         'nombres = list(map(lambda e: e["nombre"], estudiantes))\n'
         'print(len(aprobados), nombres)'),
        ("tip",
         "`lambda` se usa casi siempre como argumento `key=` de `sorted()`, `max()` o `min()`. "
         "Si la necesitas para algo más largo, escribe un `def` normal: se lee mejor."),
        ("h", "Descomponer un problema: el verdadero superpoder"),
        ("code",
         'def promedio(notas):\n'
         '    """Promedio de una lista de notas (0.0 si está vacía)."""\n'
         '    if not notas:\n'
         '        return 0.0\n'
         '    return round(sum(notas) / len(notas), 2)\n\n\n'
         'def clasificar(nota):\n'
         '    """Convierte una nota numérica en su categoría."""\n'
         '    if nota >= 4.5:\n'
         '        return "Excelente"\n'
         '    if nota >= 3.0:\n'
         '        return "Aprobado"\n'
         '    return "Reprobado"\n\n\n'
         'def linea_reporte(estudiante):\n'
         '    """Arma la línea de texto de un estudiante."""\n'
         '    media = promedio(estudiante["notas"])\n'
         '    return f\'{estudiante["nombre"]:<8}{media:>6.2f}  {clasificar(media)}\'\n\n\n'
         'grupo = [\n'
         '    {"nombre": "Ana", "notas": [4.5, 3.8, 4.9]},\n'
         '    {"nombre": "Luis", "notas": [3.0, 2.8, 3.4]},\n'
         '    {"nombre": "Sara", "notas": [4.9, 4.7, 5.0]},\n'
         ']\n\n'
         'for estudiante in grupo:\n'
         '    print(linea_reporte(estudiante))',
         "", "Tres funciones pequeñas y probables en vez de un bloque gigante. Así se escribe código de verdad."),
        ("cards", [
            ("🎯", "Una tarea", "Si al describir la función dices «y además...», son dos funciones."),
            ("🔤", "Nombre en verbo", "`calcular_promedio`, `validar_correo`, `cargar_datos`."),
            ("📏", "Corta", "Si no cabe en la pantalla, probablemente esconde otra función adentro."),
            ("🧪", "Probable", "Con `return` puedes verificarla; con solo `print` te toca leer a ojo."),
        ]),
        ("key",
         "Llegaste a la meta del curso. Con variables, condicionales, bucles, colecciones y funciones "
         "ya puedes escribir el 90 % de los scripts que necesitarás en el posgrado."),
    ],
    "quiz": [
        {
            "q": "¿Qué devuelve una función que no tiene `return`?",
            "options": ["0", "None", "Lanza un error"],
            "answer": 1,
            "why": "Toda función sin `return` explícito devuelve `None`.",
            "hint": "Pruébalo: `def f(): pass` y luego `print(f())`.",
        },
        {
            "q": "`def saludar(nombre, saludo=\"Hola\")`. ¿Cuál llamada es inválida?",
            "options": ["saludar(\"Ana\")", "saludar(\"Ana\", \"Buenas\")", "saludar(saludo=\"Buenas\")"],
            "answer": 2,
            "why": "`nombre` no tiene valor por defecto: es obligatorio.",
            "hint": "¿Cuál deja un parámetro obligatorio sin valor?",
        },
        {
            "q": "¿Por qué `def f(items=[])` es peligroso?",
            "options": [
                "Porque Python no permite listas como parámetro",
                "Porque la lista se crea una sola vez y se comparte entre llamadas",
                "Porque hace la función más lenta",
            ],
            "answer": 1,
            "why": "El valor por defecto se evalúa al definir la función, no en cada llamada. Usa `None`.",
            "hint": "Recuerda el ejemplo donde reaparecía la «a».",
        },
        {
            "q": "¿Cuál es la diferencia entre `return` y `print`?",
            "options": [
                "Ninguna, son sinónimos",
                "`return` entrega el valor a quien llamó; `print` solo lo muestra en pantalla",
                "`print` es más rápido",
            ],
            "answer": 1,
            "why": "Con `return` puedes seguir operando con el resultado; con `print` el valor se pierde.",
            "hint": "Piensa si puedes hacer `total = mi_funcion() * 2`.",
        },
    ],
    "challenges": [
        {
            "id": "area",
            "title": "Tu primera función",
            "level": "Fácil",
            "points": 25,
            "prompt": ("Escribe la función `area_rectangulo(base, altura)` que **devuelva** (no imprima) "
                       "el área."),
            "starter": "def area_rectangulo(base, altura):\n    pass\n",
            "height": 140,
            "tests": [t_func("area_rectangulo", [((3, 4), 12), ((2.5, 4), 10.0), ((0, 7), 0)])],
            "hint": "El cuerpo es una sola línea: `return base * altura`.",
            "solution": "def area_rectangulo(base, altura):\n    return base * altura",
        },
        {
            "id": "notas_funciones",
            "title": "Dos funciones que trabajan juntas",
            "level": "Medio",
            "points": 40,
            "prompt": ("Escribe **dos** funciones:\n\n"
                       "1. `promedio(notas)` → devuelve el promedio **redondeado a 2 decimales**. "
                       "Si la lista está vacía, devuelve `0.0`.\n"
                       "2. `clasificar(nota)` → devuelve `\"Excelente\"` (≥ 4.5), `\"Aprobado\"` (≥ 3.0) "
                       "o `\"Reprobado\"`."),
            "starter": ("def promedio(notas):\n"
                        "    pass\n\n\n"
                        "def clasificar(nota):\n"
                        "    pass\n\n\n"
                        "print(promedio([4.5, 3.8, 4.9]), clasificar(4.4))"),
            "height": 260,
            "tests": [
                t_func("promedio", [
                    (([4.5, 3.8, 4.9],), 4.4),
                    (([3.0, 2.8, 3.4],), 3.07),
                    (([],), 0.0),
                ]),
                t_func("clasificar", [
                    ((4.9,), "Excelente"), ((4.5,), "Excelente"),
                    ((3.0,), "Aprobado"), ((4.4,), "Aprobado"),
                    ((2.9,), "Reprobado"), ((0,), "Reprobado"),
                ]),
            ],
            "hint": ("En `promedio`, primero el caso vacío: `if not notas: return 0.0`. "
                     "En `clasificar`, recuerda que cada `return` termina la función: no necesitas `else`."),
            "solution": ("def promedio(notas):\n"
                         '    """Promedio redondeado a 2 decimales."""\n'
                         "    if not notas:\n"
                         "        return 0.0\n"
                         "    return round(sum(notas) / len(notas), 2)\n\n\n"
                         "def clasificar(nota):\n"
                         '    """Categoría de una nota de 0 a 5."""\n'
                         "    if nota >= 4.5:\n"
                         '        return "Excelente"\n'
                         "    if nota >= 3.0:\n"
                         '        return "Aprobado"\n'
                         '    return "Reprobado"\n\n\n'
                         "print(promedio([4.5, 3.8, 4.9]), clasificar(4.4))"),
        },
    ],
}

LESSONS = [
    L_INICIO, L_VARIABLES, L_OPERADORES, L_CADENAS, L_IO,
    L_CONDICIONALES, L_BUCLES, L_LISTAS, L_DICCIONARIOS, L_FUNCIONES,
]

# --------------------------------------------------------------------------- #
# Retos extra (solo aparecen en la página de Retos)
# --------------------------------------------------------------------------- #

EXTRA_CHALLENGES = [
    {
        "id": "descuentos",
        "title": "Descuentos por categoría",
        "level": "Fácil",
        "points": 25,
        "topic": "Funciones + condicionales",
        "prompt": ("Escribe `precio_final(precio, categoria)` que aplique **20 %** de descuento a "
                   "`\"estudiante\"`, **15 %** a `\"docente\"` y **0 %** a cualquier otra cosa. "
                   "Devuelve el valor redondeado a 2 decimales."),
        "starter": "def precio_final(precio, categoria):\n    pass\n",
        "height": 160,
        "tests": [t_func("precio_final", [
            ((100000, "estudiante"), 80000.0),
            ((100000, "docente"), 85000.0),
            ((100000, "externo"), 100000.0),
            ((59900, "estudiante"), 47920.0),
        ])],
        "hint": "Guarda el descuento en una variable con `if/elif/else` y al final `return round(precio * (1 - descuento), 2)`.",
        "solution": ("def precio_final(precio, categoria):\n"
                     '    if categoria == "estudiante":\n'
                     "        descuento = 0.20\n"
                     '    elif categoria == "docente":\n'
                     "        descuento = 0.15\n"
                     "    else:\n"
                     "        descuento = 0.0\n"
                     "    return round(precio * (1 - descuento), 2)"),
    },
    {
        "id": "fizzbuzz",
        "title": "FizzBuzz (el clásico de las entrevistas)",
        "level": "Medio",
        "points": 30,
        "topic": "Bucles + módulo",
        "prompt": ("Escribe `fizzbuzz(n)` que devuelva una **lista** con los números de 1 a `n`, pero:\n\n"
                   "- múltiplos de 3 → `\"Fizz\"`\n"
                   "- múltiplos de 5 → `\"Buzz\"`\n"
                   "- múltiplos de ambos → `\"FizzBuzz\"`\n"
                   "- los demás → el número **como texto** (`\"1\"`, `\"2\"`, ...)"),
        "starter": "def fizzbuzz(n):\n    resultado = []\n    for i in range(1, n + 1):\n        pass\n    return resultado\n",
        "height": 200,
        "tests": [t_func("fizzbuzz", [
            ((15,), _fizzbuzz_esperado(15)),
            ((5,), _fizzbuzz_esperado(5)),
            ((1,), ["1"]),
        ])],
        "hint": "Pregunta **primero** por el múltiplo de 15 (o de 3 y 5 a la vez); si no, nunca sale `FizzBuzz`.",
        "solution": ("def fizzbuzz(n):\n"
                     "    resultado = []\n"
                     "    for i in range(1, n + 1):\n"
                     "        if i % 15 == 0:\n"
                     '            resultado.append("FizzBuzz")\n'
                     "        elif i % 3 == 0:\n"
                     '            resultado.append("Fizz")\n'
                     "        elif i % 5 == 0:\n"
                     '            resultado.append("Buzz")\n'
                     "        else:\n"
                     "            resultado.append(str(i))\n"
                     "    return resultado"),
    },
    {
        "id": "palindromo",
        "title": "¿Es palíndromo?",
        "level": "Medio",
        "points": 30,
        "topic": "Cadenas + funciones",
        "prompt": ("Escribe `es_palindromo(texto)` que devuelva `True` si el texto se lee igual al derecho "
                   "y al revés, **ignorando espacios y mayúsculas**.\n\n"
                   "Ejemplo: `\"Anita lava la tina\"` → `True`."),
        "starter": "def es_palindromo(texto):\n    pass\n",
        "height": 160,
        "tests": [t_func("es_palindromo", [
            (("Anita lava la tina",), True),
            (("reconocer",), True),
            (("Bases de datos",), False),
            (("A",), True),
        ])],
        "hint": "Primero limpia: `limpio = texto.lower().replace(\" \", \"\")`. Luego compara con `limpio[::-1]`.",
        "solution": ("def es_palindromo(texto):\n"
                     '    limpio = texto.lower().replace(" ", "")\n'
                     "    return limpio == limpio[::-1]"),
    },
    {
        "id": "contar_palabras",
        "title": "Contador de palabras",
        "level": "Medio",
        "points": 35,
        "topic": "Diccionarios + cadenas",
        "prompt": ("Escribe `contar_palabras(texto)` que devuelva un diccionario `{palabra: veces}`.\n\n"
                   "Reglas: pasa todo a minúsculas y elimina los signos `. , ; ! ?` antes de contar.\n\n"
                   "`\"El dato, el dato; y el DATO!\"` → `{\"el\": 3, \"dato\": 3, \"y\": 1}`"),
        "starter": "def contar_palabras(texto):\n    pass\n",
        "height": 200,
        "tests": [t_func("contar_palabras", [
            (("El dato, el dato; y el DATO!",), {"el": 3, "dato": 3, "y": 1}),
            (("uno uno uno",), {"uno": 3}),
            (("",), {}),
        ])],
        "hint": ("Quita los signos con varios `.replace(signo, \"\")` (o un bucle sobre `\".,;!?\"`), "
                 "separa con `.split()` y cuenta con `conteo[p] = conteo.get(p, 0) + 1`."),
        "solution": ("def contar_palabras(texto):\n"
                     "    limpio = texto.lower()\n"
                     '    for signo in ".,;!?":\n'
                     '        limpio = limpio.replace(signo, "")\n'
                     "    conteo = {}\n"
                     "    for palabra in limpio.split():\n"
                     "        conteo[palabra] = conteo.get(palabra, 0) + 1\n"
                     "    return conteo"),
    },
    {
        "id": "proyecto_final",
        "title": "Proyecto final: mini sistema de notas",
        "level": "Reto",
        "points": 60,
        "topic": "Todo el curso junto",
        "prompt": ("Junta todo lo aprendido. Escribe **tres** funciones:\n\n"
                   "1. `promedio(notas)` → promedio redondeado a 2 decimales (`0.0` si está vacía).\n"
                   "2. `clasificar(nota)` → `\"Excelente\"` (≥ 4.5), `\"Aprobado\"` (≥ 3.0), `\"Reprobado\"`.\n"
                   "3. `resumen(estudiantes)` → recibe una lista de diccionarios "
                   "`{\"nombre\": str, \"notas\": [float]}` y devuelve:\n\n"
                   "```python\n"
                   "{\"aprobados\": [nombres con promedio >= 3.0],\n"
                   " \"reprobados\": [los demás],\n"
                   " \"mejor\": nombre del promedio más alto}\n"
                   "```\n"
                   "Los nombres deben ir en el mismo orden en que llegan."),
        "starter": ("def promedio(notas):\n"
                    "    pass\n\n\n"
                    "def clasificar(nota):\n"
                    "    pass\n\n\n"
                    "def resumen(estudiantes):\n"
                    "    pass\n\n\n"
                    "grupo = [\n"
                    '    {"nombre": "Ana", "notas": [4.5, 4.0]},\n'
                    '    {"nombre": "Luis", "notas": [2.0, 2.5]},\n'
                    "]\n"
                    "print(resumen(grupo))"),
        "height": 340,
        "tests": [
            t_func("promedio", [(([4.5, 4.0],), 4.25), (([],), 0.0)]),
            t_func("clasificar", [((4.6,), "Excelente"), ((3.5,), "Aprobado"), ((1.0,), "Reprobado")]),
            t_func("resumen", [((_ESTUDIANTES_DEMO,), {
                "aprobados": ["Ana"], "reprobados": ["Luis"], "mejor": "Ana",
            })]),
        ],
        "hint": ("`resumen` puede apoyarse en `promedio`: recorre la lista, calcula el promedio de cada uno, "
                 "guárdalo para comparar y ve llenando las dos listas. El mejor es el del promedio más alto."),
        "solution": ("def promedio(notas):\n"
                     "    if not notas:\n"
                     "        return 0.0\n"
                     "    return round(sum(notas) / len(notas), 2)\n\n\n"
                     "def clasificar(nota):\n"
                     "    if nota >= 4.5:\n"
                     '        return "Excelente"\n'
                     "    if nota >= 3.0:\n"
                     '        return "Aprobado"\n'
                     '    return "Reprobado"\n\n\n'
                     "def resumen(estudiantes):\n"
                     "    aprobados = []\n"
                     "    reprobados = []\n"
                     "    mejor = None\n"
                     "    mejor_promedio = -1\n\n"
                     "    for est in estudiantes:\n"
                     '        media = promedio(est["notas"])\n'
                     "        if media >= 3.0:\n"
                     '            aprobados.append(est["nombre"])\n'
                     "        else:\n"
                     '            reprobados.append(est["nombre"])\n'
                     "        if media > mejor_promedio:\n"
                     "            mejor_promedio = media\n"
                     '            mejor = est["nombre"]\n\n'
                     '    return {"aprobados": aprobados, "reprobados": reprobados, "mejor": mejor}\n\n\n'
                     "grupo = [\n"
                     '    {"nombre": "Ana", "notas": [4.5, 4.0]},\n'
                     '    {"nombre": "Luis", "notas": [2.0, 2.5]},\n'
                     "]\n"
                     "print(resumen(grupo))"),
        "solution_note": "Fíjate cómo `resumen` reutiliza `promedio`: ese es el objetivo de escribir funciones.",
    },
]


def all_challenges() -> list[dict]:
    """Todos los retos: los de cada lección + los extra."""
    retos = []
    for lesson in LESSONS:
        for ch in lesson.get("challenges", []):
            item = dict(ch)
            item.setdefault("topic", f"{lesson['icon']} {lesson['title']}")
            retos.append(item)
    retos.extend(EXTRA_CHALLENGES)
    return retos


def find_lesson(lesson_id: str) -> dict | None:
    for lesson in LESSONS:
        if lesson["id"] == lesson_id:
            return lesson
    return None
