"""PyLab — Python de cero a funciones, para estudiantes de posgrado.

Lanzar con:
    streamlit run app.py
"""

from __future__ import annotations

import random

import streamlit as st

import ui
from lessons import LESSONS, all_challenges
from sandbox import ALLOWED_MODULES, run_user_code
from ui import (
    PAGE_CHULETA, PAGE_PROGRESO, PAGE_RETOS, PAGE_SANDBOX, award, badge,
    cards, challenge, hero, level_from_xp, md_inline, progress_bar, quiz,
    render_blocks, render_result, section, table,
)

st.set_page_config(
    page_title="PyLab · Python hasta funciones",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()
ui.init_state()

ss = st.session_state
# Ojo: la etiqueta NO puede empezar por "1." o Streamlit la interpreta como
# lista numerada de markdown y se come el número.
LESSON_LABELS = [f"{les['icon']}  {les['num']}. {les['title']}" for les in LESSONS]
BY_LABEL = dict(zip(LESSON_LABELS, LESSONS))
TOOLS = [PAGE_SANDBOX, PAGE_RETOS, PAGE_CHULETA, PAGE_PROGRESO]

TIPS = [
    "Lee **la última línea** del error primero: ahí está el tipo y el mensaje.",
    "`print(f\"{variable=}\")` te muestra nombre y valor de un solo golpe.",
    "Si copias y pegas un bloque por segunda vez, eso pide ser una función.",
    "Nombra las variables como si otra persona fuera a leer tu código mañana. Esa persona eres tú.",
    "`sorted()` devuelve una lista nueva; `.sort()` modifica la original y devuelve `None`.",
    "Usa `.get(clave, valor)` en diccionarios con datos externos y te ahorras los `KeyError`.",
    "Cuando un `if` no entra, imprime la condición: casi siempre es un espacio o una mayúscula.",
    "Escribe primero el caso más simple, hazlo funcionar, y solo entonces generalízalo.",
    "20 minutos diarios rinden más que 4 horas el domingo: el cerebro consolida entre sesiones.",
    "`for i, x in enumerate(xs, start=1)` es más limpio que `range(len(xs))`.",
]

# --------------------------------------------------------------------------- #
# Navegación pendiente (se aplica ANTES de crear los widgets del menú)
# --------------------------------------------------------------------------- #

ss.setdefault("page", LESSON_LABELS[0])
ss.setdefault("nav_lesson", LESSON_LABELS[0])
ss.setdefault("tip_idx", random.randrange(len(TIPS)))

if "_goto" in ss:
    ss.page = ss.pop("_goto")
if "_goto_lesson" in ss:
    etiqueta = ss.pop("_goto_lesson")
    ss.nav_lesson = etiqueta
    ss.page = etiqueta


def _on_lesson_change() -> None:
    ss.page = ss.nav_lesson


def _go(destino: str) -> None:
    ss.page = destino


# --------------------------------------------------------------------------- #
# Barra lateral  (se dibuja al final del script, para que el XP salga fresco)
# --------------------------------------------------------------------------- #

RETOS = all_challenges()
TOTAL_QUIZ = sum(len(les.get("quiz", [])) for les in LESSONS)
TOTAL_RETOS = len(RETOS)


def stats() -> tuple[int, int, float]:
    """(quizzes acertados, retos superados, % de avance total)."""
    quiz_ok = sum(1 for k in ss.done if k.startswith("quiz_"))
    retos_ok = sum(1 for k in ss.done if k.startswith("reto_"))
    avance = 100 * (quiz_ok + retos_ok) / max(1, TOTAL_QUIZ + TOTAL_RETOS)
    return quiz_ok, retos_ok, avance


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            "<div class='sf-brand'><div class='sf-brand-logo'>🐍</div>"
            "<div><div class='sf-brand-name'>PyLab</div>"
            "<div class='sf-brand-sub'>de cero a funciones</div></div></div>",
            unsafe_allow_html=True,
        )

        nivel, nombre_nivel, en_nivel, paso = level_from_xp(ss.xp)
        st.markdown(
            f"<div class='sf-mini'>Nivel {nivel} · <b style='color:#fff'>{nombre_nivel}</b>"
            f" · {ss.xp} XP</div>", unsafe_allow_html=True,
        )
        progress_bar(100 * en_nivel / paso, f"{en_nivel}/{paso} XP para el siguiente nivel")

        st.markdown("<div class='sf-mini' style='margin:.9rem 0 .2rem;letter-spacing:.12em'>"
                    "LECCIONES</div>", unsafe_allow_html=True)
        st.radio(
            "Lecciones", LESSON_LABELS, key="nav_lesson",
            label_visibility="collapsed", on_change=_on_lesson_change,
        )

        st.markdown("<div class='sf-mini' style='margin:.9rem 0 .35rem;letter-spacing:.12em'>"
                    "PRACTICAR</div>", unsafe_allow_html=True)
        for fila in (TOOLS[:2], TOOLS[2:]):
            cols = st.columns(2)
            for col, destino in zip(cols, fila):
                col.button(
                    destino, key=f"tool_{destino}", use_container_width=True,
                    type="primary" if ss.page == destino else "secondary",
                    on_click=_go, args=(destino,),
                )

        st.divider()
        st.markdown("<div class='sf-mini' style='letter-spacing:.12em'>MINI TIP</div>",
                    unsafe_allow_html=True)
        st.markdown(
            "<div class='sf-call sf-tip' style='margin-top:.35rem'>"
            f"<div class='sf-call-ico'>💡</div><div>{md_inline(TIPS[ss.tip_idx])}</div></div>",
            unsafe_allow_html=True,
        )
        if st.button("🔀 Otro tip", use_container_width=True):
            ss.tip_idx = (ss.tip_idx + 1) % len(TIPS)
            st.rerun()

        _, _, avance = stats()
        st.markdown(f"<div class='sf-mini' style='margin-top:.8rem'>Progreso total: "
                    f"<b style='color:#fff'>{avance:.0f}%</b></div>", unsafe_allow_html=True)
        progress_bar(avance)


# --------------------------------------------------------------------------- #
# Página: lección
# --------------------------------------------------------------------------- #


def page_lesson(lesson: dict) -> None:
    ss.visited.add(lesson["id"])
    hero(
        lesson["icon"],
        f"{lesson['num']}. {lesson['title']}",
        lesson["subtitle"],
        [f"⏱ {lesson['minutes']} min", f"🏷 {lesson['tag']}", *lesson.get("chips", [])],
    )

    render_blocks(lesson["blocks"], prefix=lesson["id"])

    if lesson.get("quiz"):
        quiz(lesson["id"], lesson["quiz"])

    for ch in lesson.get("challenges", []):
        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        challenge(ch)

    # Navegación inferior
    st.divider()
    idx = LESSONS.index(lesson)
    c1, c2, c3 = st.columns([1.6, 3, 1.6])
    if idx > 0:
        c1.button(f"← {LESSONS[idx-1]['title']}", use_container_width=True,
                  key="prev_lesson",
                  on_click=lambda: ss.__setitem__("_goto_lesson", LESSON_LABELS[idx - 1]))
    if idx < len(LESSONS) - 1:
        c3.button(f"{LESSONS[idx+1]['title']} →", use_container_width=True,
                  key="next_lesson", type="primary",
                  on_click=lambda: ss.__setitem__("_goto_lesson", LESSON_LABELS[idx + 1]))
    else:
        c3.button("Ir a los retos 🏆", use_container_width=True, key="next_retos",
                  type="primary", on_click=_go, args=(PAGE_RETOS,))


# --------------------------------------------------------------------------- #
# Página: sandbox
# --------------------------------------------------------------------------- #

PLANTILLAS: dict[str, tuple[str, str]] = {
    "— Empezar en blanco —": ("# Escribe tu código aquí\nprint(\"Hola\")\n", ""),
    "Hola, mundo con variables": (
        'nombre = "Ana"\n'
        'creditos = 3\n'
        'print(f"Hola {nombre}, llevas {creditos} créditos")\n', ""),
    "Pedir datos con input()": (
        'nombre = input("Nombre: ")\n'
        'nota = float(input("Nota: "))\n\n'
        'if nota >= 3.0:\n'
        '    print(f"{nombre} aprobó con {nota:.1f}")\n'
        'else:\n'
        '    print(f"{nombre} debe repetir")\n', "Ana\n4.2"),
    "Tabla de multiplicar (bucles)": (
        "numero = 7\n"
        "for i in range(1, 11):\n"
        '    print(f"{numero} x {i:>2} = {numero * i:>3}")\n', ""),
    "Promedio de una lista": (
        "notas = [4.5, 3.8, 4.9, 2.7, 3.3]\n\n"
        "promedio = sum(notas) / len(notas)\n"
        "aprobadas = [n for n in notas if n >= 3.0]\n\n"
        'print(f"Promedio: {promedio:.2f}")\n'
        'print(f"Aprobadas: {len(aprobadas)} de {len(notas)}")\n'
        'print(f"Mejor: {max(notas)} | Peor: {min(notas)}")\n', ""),
    "Contar palabras (diccionarios)": (
        'texto = "el dato el dato y el resultado"\n'
        "conteo = {}\n\n"
        "for palabra in texto.split():\n"
        "    conteo[palabra] = conteo.get(palabra, 0) + 1\n\n"
        "for palabra, veces in sorted(conteo.items(), key=lambda p: p[1], reverse=True):\n"
        '    print(f"{palabra:<12} {veces}")\n', ""),
    "Mini reporte con funciones": (
        "def promedio(notas):\n"
        "    if not notas:\n"
        "        return 0.0\n"
        "    return round(sum(notas) / len(notas), 2)\n\n\n"
        "def clasificar(nota):\n"
        "    if nota >= 4.5:\n"
        '        return "Excelente"\n'
        "    if nota >= 3.0:\n"
        '        return "Aprobado"\n'
        '    return "Reprobado"\n\n\n'
        "grupo = [\n"
        '    {"nombre": "Ana", "notas": [4.5, 3.8, 4.9]},\n'
        '    {"nombre": "Luis", "notas": [3.0, 2.8, 3.4]},\n'
        "]\n\n"
        "for est in grupo:\n"
        '    media = promedio(est["notas"])\n'
        '    print(f\'{est["nombre"]:<6}{media:>6.2f}  {clasificar(media)}\')\n', ""),
    "Módulos permitidos (math, random)": (
        "import math\n"
        "import random\n\n"
        'print("Raíz de 2:", round(math.sqrt(2), 4))\n'
        'print("Pi:", round(math.pi, 4))\n'
        'print("Dado:", random.randint(1, 6))\n'
        'print("Muestra:", random.sample(range(1, 50), 6))\n', ""),
}


def page_sandbox() -> None:
    if "_load_code" in ss:
        ss.sandbox_code = ss.pop("_load_code")
    if "_load_stdin" in ss:
        ss.sandbox_stdin = ss.pop("_load_stdin")
    ss.setdefault("sandbox_code", PLANTILLAS["— Empezar en blanco —"][0])
    ss.setdefault("sandbox_stdin", "")

    hero("🧪", "Sandbox libre",
         "Tu laboratorio: escribe, ejecuta, rómpelo y vuelve a empezar. Los errores salen traducidos y con pista.",
         ["Ejecución real de Python", "input() simulado", "Corta bucles infinitos"])

    izq, der = st.columns([3, 2], gap="medium")

    with izq:
        st.markdown("<div class='sf-h2'>✍️ Editor</div>", unsafe_allow_html=True)
        st.text_area("Código", key="sandbox_code", height=380, label_visibility="collapsed")

        b1, b2, b3 = st.columns([1.1, 1.1, 2.2])
        ejecutar = b1.button("▶ Ejecutar", type="primary", use_container_width=True)
        if b2.button("🧹 Limpiar", use_container_width=True):
            ss["_load_code"] = "# Escribe tu código aquí\n"
            st.rerun()
        if b3.button("💾 Guardar este código", use_container_width=True):
            ss.snippets.append(ss.sandbox_code)
            st.toast("Código guardado abajo", icon="💾")

    with der:
        st.markdown("<div class='sf-h2'>📥 Entrada (input)</div>", unsafe_allow_html=True)
        st.text_area(
            "Entrada", key="sandbox_stdin", height=110, label_visibility="collapsed",
            placeholder="Una línea por cada input() de tu programa",
        )
        st.markdown("<div class='sf-h2'>📦 Plantillas</div>", unsafe_allow_html=True)
        eleccion = st.selectbox("Plantillas", list(PLANTILLAS), label_visibility="collapsed")
        if st.button("Cargar plantilla", use_container_width=True):
            codigo, entrada = PLANTILLAS[eleccion]
            ss["_load_code"] = codigo
            ss["_load_stdin"] = entrada
            st.rerun()

    if ejecutar:
        ss["sandbox_result"] = run_user_code(ss.sandbox_code, ss.sandbox_stdin)
        award("primera_ejecucion", 5)

    section("📤 Resultado")
    resultado = ss.get("sandbox_result")
    if resultado is None:
        st.markdown(
            "<div class='sf-out'><div class='sf-out-h'>Esperando</div>"
            "<pre>Dale a ▶ Ejecutar para ver la salida aquí.</pre></div>",
            unsafe_allow_html=True,
        )
    else:
        render_result(resultado)
        if resultado.ok and resultado.namespace:
            interesantes = {
                k: v for k, v in resultado.namespace.items()
                if not k.startswith("__") and not callable(v)
            }
            if interesantes:
                with st.expander(f"🔍 Variables al terminar ({len(interesantes)})"):
                    table(["Variable", "Tipo", "Valor"],
                          [[f"`{k}`", f"`{type(v).__name__}`", "`" + repr(v)[:180] + "`"]
                           for k, v in list(interesantes.items())[:40]])

    if ss.snippets:
        section("💾 Tus códigos guardados")
        for i, snippet in enumerate(reversed(ss.snippets[-8:])):
            with st.expander(f"Guardado #{len(ss.snippets) - i} · {snippet.strip().splitlines()[0][:50]}"):
                st.code(snippet, language="python")
                if st.button("Cargar en el editor", key=f"load_snip_{i}"):
                    ss["_load_code"] = snippet
                    st.rerun()

    section("ℹ️ Qué se puede hacer aquí")
    cards([
        ("✅", "Todo lo del curso", "Variables, condicionales, bucles, listas, diccionarios, funciones, clases..."),
        ("📦", "Módulos permitidos",
         f"`math`, `random`, `statistics`, `datetime`, `json`, `re`, `collections`, "
         f"`itertools`... ({len(ALLOWED_MODULES)} en total)"),
        ("⏱", "Tope de 8 segundos", "Si tu programa se cuelga, la sandbox lo corta y te avisa."),
        ("🚫", "Sin archivos ni red", "`open`, `os` y similares están desactivados para que nada se dañe."),
    ])


# --------------------------------------------------------------------------- #
# Página: retos
# --------------------------------------------------------------------------- #


def page_retos() -> None:
    hechos = sum(1 for r in RETOS if f"reto_{r['id']}" in ss.done)
    hero("🏆", "Retos autoevaluados",
         "Ejercicios que se corrigen solos: te dicen exactamente qué caso falló y por qué. Aquí es donde se aprende de verdad.",
         [f"{hechos}/{len(RETOS)} superados", "Pistas y solución incluidas"])

    progress_bar(100 * hechos / max(1, len(RETOS)), f"{hechos} de {len(RETOS)} retos superados")

    nivel = st.radio("Dificultad", ["Todos", "Fácil", "Medio", "Reto"],
                     horizontal=True, label_visibility="collapsed")
    filtrados = [r for r in RETOS if nivel == "Todos" or r.get("level") == nivel]

    if not filtrados:
        st.info("No hay retos con ese filtro.")
        return

    def etiqueta(i: int) -> str:
        r = filtrados[i]
        marca = "✅" if f"reto_{r['id']}" in ss.done else "⬜"
        return f"{marca}  {r['title']}  ·  {r.get('level', '')}"

    indice = st.selectbox("Elige un reto", range(len(filtrados)), format_func=etiqueta,
                          label_visibility="collapsed")
    elegido = filtrados[indice]

    color, bg = ui.LEVEL_COLORS.get(elegido.get("level", "Fácil"), ui.LEVEL_COLORS["Fácil"])
    st.markdown(
        f"<div style='margin:.6rem 0 .2rem'>{badge(elegido.get('level', 'Fácil'), color, bg)} "
        f"&nbsp;<span class='sf-mini'>{elegido.get('topic', '')} · "
        f"{elegido.get('points', 25)} XP</span></div>",
        unsafe_allow_html=True,
    )
    challenge(elegido)

    section("📋 Todos los retos")
    table(
        ["", "Reto", "Nivel", "Tema", "XP"],
        [["✅" if f"reto_{r['id']}" in ss.done else "⬜", r["title"],
          r.get("level", ""), r.get("topic", ""), r.get("points", 25)] for r in RETOS],
    )


# --------------------------------------------------------------------------- #
# Página: chuleta
# --------------------------------------------------------------------------- #

CHULETA: dict[str, list[tuple[str, str]]] = {
    "Básicos": [
        ("Variables y tipos",
         'nombre = "Ana"        # str\n'
         "edad = 29             # int\n"
         "promedio = 4.35       # float\n"
         "activo = True         # bool\n"
         "vacio = None          # NoneType\n\n"
         "print(type(edad))\n"
         'numero = int("42")\n'
         "texto = str(42)"),
        ("Operadores",
         "7 / 2    # 3.5   división real\n"
         "7 // 2   # 3     división entera\n"
         "7 % 2    # 1     residuo\n"
         "2 ** 10  # 1024  potencia\n\n"
         "x += 1   # x = x + 1\n"
         "3 <= x <= 9\n"
         "a and b   /   a or b   /   not a"),
        ("f-strings",
         'f"{nombre} sacó {nota:.2f}"\n'
         'f"{1250000:,}"        # separador de miles\n'
         'f"|{nombre:>10}|"     # derecha\n'
         'f"|{nombre:<10}|"     # izquierda\n'
         'f"|{nombre:^10}|"     # centrado\n'
         'f"{0.853:.1%}"        # porcentaje\n'
         'f"{nota=}"            # depuración'),
    ],
    "Control": [
        ("Condicionales",
         "if nota >= 4.5:\n"
         '    print("Excelente")\n'
         "elif nota >= 3.0:\n"
         '    print("Aprobado")\n'
         "else:\n"
         '    print("Reprobado")\n\n'
         'estado = "OK" if nota >= 3 else "NO"'),
        ("Bucles",
         "for i in range(1, 6):\n"
         "    print(i)\n\n"
         "for i, x in enumerate(xs, start=1):\n"
         "    print(i, x)\n\n"
         "for a, b in zip(xs, ys):\n"
         "    print(a, b)\n\n"
         "while saldo > 0:\n"
         "    saldo -= 100\n\n"
         "# break -> sale | continue -> siguiente"),
        ("Try / except",
         "try:\n"
         "    numero = float(dato)\n"
         "except ValueError:\n"
         '    print("No es un número")'),
    ],
    "Colecciones": [
        ("Listas",
         "xs = [3, 1, 2]\n"
         "xs.append(4)\n"
         "xs.insert(0, 9)\n"
         "xs.remove(1)\n"
         "ultimo = xs.pop()\n"
         "xs.sort()              # modifica\n"
         "nueva = sorted(xs)     # copia ordenada\n"
         "copia = xs.copy()      # ¡no uses ys = xs!\n"
         "xs[1:3], xs[::-1], len(xs), 3 in xs"),
        ("Diccionarios",
         'd = {"nombre": "Ana", "edad": 29}\n'
         'd["edad"] = 30\n'
         'd["nuevo"] = True\n'
         'd.get("tel", "sin dato")\n'
         "for k, v in d.items():\n"
         "    print(k, v)\n\n"
         "conteo[p] = conteo.get(p, 0) + 1"),
        ("Tuplas y conjuntos",
         "punto = (4.5, 3.8)      # inmutable\n"
         "x, y = punto            # desempaquetado\n\n"
         "unicos = set([1, 1, 2])\n"
         "a & b   # intersección\n"
         "a | b   # unión\n"
         "a - b   # diferencia"),
        ("Comprensiones",
         "[n for n in notas if n >= 3.0]\n"
         "[n * 2 for n in numeros]\n"
         '{k: v for k, v in pares}\n'
         "sum(xs), max(xs), min(xs), len(xs)"),
    ],
    "Funciones": [
        ("Definir y llamar",
         "def promedio(notas):\n"
         '    """Promedio de una lista."""\n'
         "    if not notas:\n"
         "        return 0.0\n"
         "    return round(sum(notas) / len(notas), 2)\n\n\n"
         "media = promedio([4.5, 3.8])"),
        ("Parámetros",
         "def saludar(nombre, saludo=\"Hola\"):\n"
         '    return f"{saludo}, {nombre}"\n\n'
         'saludar("Ana")\n'
         'saludar("Ana", saludo="Buenas")\n\n'
         "def promedio(*notas): ...      # varios posicionales\n"
         "def registrar(**datos): ...    # varios con nombre\n\n"
         "# ¡Nunca def f(xs=[]) ! usa xs=None"),
        ("Varios retornos y lambda",
         "def stats(xs):\n"
         "    return min(xs), max(xs), sum(xs) / len(xs)\n\n"
         "menor, mayor, media = stats(xs)\n\n"
         "sorted(gente, key=lambda p: p[\"edad\"])\n"
         "max(d, key=d.get)"),
    ],
    "Errores frecuentes": [
        ("Los que más se ven",
         "NameError          -> nombre mal escrito o sin definir\n"
         "TypeError          -> mezclaste texto y número\n"
         "ValueError         -> int(\"hola\") / float(\"\")\n"
         "IndexError         -> índice fuera de la lista\n"
         "KeyError           -> clave que no existe\n"
         "IndentationError   -> falta o sobra sangría\n"
         "ZeroDivisionError  -> dividiste entre 0\n"
         "AttributeError     -> método que ese tipo no tiene"),
        ("Antídotos",
         '"5" + 5            ->  int("5") + 5   o   f"5{5}"\n'
         "d[\"x\"]             ->  d.get(\"x\", valor_defecto)\n"
         "xs = xs.sort()     ->  xs.sort()  o  ys = sorted(xs)\n"
         "ys = xs            ->  ys = xs.copy()\n"
         "def f(xs=[])       ->  def f(xs=None)\n"
         "if x = 3           ->  if x == 3"),
    ],
}


def page_chuleta() -> None:
    hero("📋", "Chuleta de Python",
         "Todo lo del curso en una sola página. Tenla abierta mientras resuelves los retos: consultar no es hacer trampa.",
         ["Lista para imprimir", "Descargable en .md"])

    tabs = st.tabs(list(CHULETA))
    for tab, (titulo, bloques) in zip(tabs, CHULETA.items()):
        with tab:
            for subtitulo, codigo in bloques:
                st.markdown(f"<div class='sf-h2'>{subtitulo}</div>", unsafe_allow_html=True)
                st.code(codigo, language="python")

    partes = ["# Chuleta de Python — PyLab\n"]
    for titulo, bloques in CHULETA.items():
        partes.append(f"\n## {titulo}\n")
        for subtitulo, codigo in bloques:
            partes.append(f"\n### {subtitulo}\n\n```python\n{codigo}\n```\n")
    st.download_button("⬇️ Descargar la chuleta (.md)", "".join(partes),
                       file_name="chuleta_python.md", mime="text/markdown")


# --------------------------------------------------------------------------- #
# Página: progreso
# --------------------------------------------------------------------------- #


def page_progreso() -> None:
    nivel, nombre_nivel, en_nivel, paso = level_from_xp(ss.xp)
    hero("📈", "Mi progreso",
         f"Vas en el nivel **{nivel} · {nombre_nivel}**. El progreso se guarda mientras la pestaña siga abierta.",
         [f"{ss.xp} XP", f"{len(ss.visited)}/{len(LESSONS)} lecciones abiertas"])

    quiz_ok, retos_ok, avance = stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("XP", ss.xp)
    c2.metric("Quizzes", f"{quiz_ok}/{TOTAL_QUIZ}")
    c3.metric("Retos", f"{retos_ok}/{TOTAL_RETOS}")
    c4.metric("Lecciones", f"{len(ss.visited)}/{len(LESSONS)}")
    progress_bar(avance, f"{avance:.0f}% del curso completado")

    section("📚 Lección por lección")
    filas = []
    for les in LESSONS:
        n_quiz = len(les.get("quiz", []))
        hechos_quiz = sum(1 for i in range(n_quiz)
                          if f"quiz_{les['id']}_q{i}" in ss.done)
        n_ret = len(les.get("challenges", []))
        hechos_ret = sum(1 for ch in les.get("challenges", [])
                         if f"reto_{ch['id']}" in ss.done)
        completa = hechos_quiz == n_quiz and hechos_ret == n_ret
        filas.append([
            "✅" if completa else ("🔵" if les["id"] in ss.visited else "⬜"),
            f"{les['num']}. {les['icon']} {les['title']}",
            f"{hechos_quiz}/{n_quiz}" if n_quiz else "—",
            f"{hechos_ret}/{n_ret}" if n_ret else "—",
        ])
    table(["", "Lección", "Quiz", "Retos"], filas)

    section("🏆 Retos")
    table(["", "Reto", "Nivel", "XP"],
          [["✅" if f"reto_{r['id']}" in ss.done else "⬜", r["title"],
            r.get("level", ""), r.get("points", 25)] for r in RETOS])

    section("🔄 Empezar de cero")
    st.caption("Borra XP, quizzes y retos resueltos. El código que escribiste en la sandbox no se toca.")
    seguro = st.checkbox("Sí, quiero reiniciar mi progreso")
    if st.button("Reiniciar progreso", disabled=not seguro):
        ss.xp = 0
        ss.done = set()
        ss.visited = set()
        st.rerun()


# --------------------------------------------------------------------------- #
# Router
# --------------------------------------------------------------------------- #

if ss.page == PAGE_SANDBOX:
    page_sandbox()
elif ss.page == PAGE_RETOS:
    page_retos()
elif ss.page == PAGE_CHULETA:
    page_chuleta()
elif ss.page == PAGE_PROGRESO:
    page_progreso()
else:
    page_lesson(BY_LABEL.get(ss.page, LESSONS[0]))

render_sidebar()

st.markdown(
    "<div style='margin-top:3rem;text-align:center' class='sf-mini'>"
    "PyLab · hecho con Streamlit para estudiantes de posgrado · "
    "la sandbox ejecuta Python real en tu máquina</div>",
    unsafe_allow_html=True,
)
