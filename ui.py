"""Componentes visuales y estilos de PyLab.

Todo lo que pinta la interfaz vive aquí: la hoja de estilos, las tarjetas, los
callouts de tips, el bloque de código ejecutable, el quiz y el reto autoevaluado.
Así ``lessons.py`` solo tiene contenido y ``app.py`` solo tiene navegación.
"""

from __future__ import annotations

import html as _html
import re as _re
from typing import Any, Callable, Iterable, Sequence

import streamlit as st

from sandbox import RunResult, run_user_code

# Nombres de página (los usa el menú y los botones "abrir en sandbox").
PAGE_SANDBOX = "🧪 Sandbox libre"
PAGE_RETOS = "🏆 Retos"
PAGE_CHULETA = "📋 Chuleta"
PAGE_PROGRESO = "📈 Mi progreso"

LEVEL_COLORS = {
    "Fácil": ("#34D399", "rgba(52,211,153,.14)"),
    "Medio": ("#FBBF24", "rgba(251,191,36,.14)"),
    "Reto": ("#FB7185", "rgba(251,113,133,.14)"),
}


# --------------------------------------------------------------------------- #
# Estado
# --------------------------------------------------------------------------- #


def init_state() -> None:
    ss = st.session_state
    ss.setdefault("xp", 0)
    ss.setdefault("done", set())        # logros ya conseguidos (quiz + retos)
    ss.setdefault("visited", set())     # lecciones abiertas
    ss.setdefault("runs", {})           # resultados de los ejemplos ejecutados
    ss.setdefault("snippets", [])       # código guardado desde la sandbox


def award(achievement_id: str, points: int) -> bool:
    """Suma XP una sola vez por logro. Devuelve True si es la primera vez."""
    ss = st.session_state
    if achievement_id in ss.done:
        return False
    ss.done.add(achievement_id)
    ss.xp += points
    return True


def level_from_xp(xp: int) -> tuple[int, str, int, int]:
    """(nivel, nombre, xp_en_nivel, xp_para_el_siguiente)"""
    names = ["Aprendiz", "Explorador", "Practicante", "Artesano", "Pythonista"]
    step = 120
    lvl = min(len(names), xp // step + 1)
    return lvl, names[lvl - 1], xp % step, step


# --------------------------------------------------------------------------- #
# Estilos
# --------------------------------------------------------------------------- #

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root{
  --sf-brand:#7C5CFF;
  --sf-brand-2:#22D3EE;
  --sf-ok:#34D399;
  --sf-warn:#FBBF24;
  --sf-bad:#FB7185;
  --sf-text:#E9ECF8;
  --sf-muted:#98A2C0;
  --sf-card:rgba(255,255,255,.045);
  --sf-card-2:rgba(255,255,255,.075);
  --sf-border:rgba(255,255,255,.10);
  --sf-radius:16px;
}

html, body, [data-testid="stAppViewContainer"], .stApp{
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
}

.stApp{
  background:
    radial-gradient(1100px 620px at 12% -8%, rgba(124,92,255,.20), transparent 60%),
    radial-gradient(900px 520px at 92% 4%, rgba(34,211,238,.14), transparent 58%),
    radial-gradient(800px 800px at 50% 120%, rgba(124,92,255,.10), transparent 60%),
    #0B0F1A;
}

.block-container{padding-top:2.2rem;padding-bottom:4rem;max-width:1180px;}
footer{visibility:hidden;}

code, pre, kbd, .stTextArea textarea, [data-testid="stCodeBlock"]{
  font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Consolas,monospace !important;
}
[data-testid="stCodeBlock"] pre, pre{
  border-radius:14px !important;
  border:1px solid var(--sf-border) !important;
  background:rgba(4,7,16,.72) !important;
}
.stTextArea textarea{
  background:rgba(4,7,16,.72) !important;
  border:1px solid var(--sf-border) !important;
  border-radius:14px !important;
  font-size:.92rem !important;
  line-height:1.55 !important;
  color:#E9ECF8 !important;
}
.stTextArea textarea:focus{
  border-color:rgba(124,92,255,.75) !important;
  box-shadow:0 0 0 3px rgba(124,92,255,.18) !important;
}

/* ---------- Botones ---------- */
.stButton > button, .stDownloadButton > button{
  border-radius:12px;
  border:1px solid var(--sf-border);
  background:var(--sf-card-2);
  color:var(--sf-text);
  font-weight:600;
  padding:.42rem .95rem;
  transition:transform .12s ease, box-shadow .18s ease, border-color .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  transform:translateY(-1px);
  border-color:rgba(124,92,255,.65);
  color:#fff;
  box-shadow:0 8px 22px -10px rgba(124,92,255,.75);
}
.stButton > button[kind="primary"]{
  background:linear-gradient(135deg,var(--sf-brand),#5B8CFF 55%,var(--sf-brand-2));
  border:none;color:#0A0D18;font-weight:700;
}
.stButton > button[kind="primary"]:hover{color:#0A0D18;}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,rgba(16,21,38,.96),rgba(9,12,22,.98));
  border-right:1px solid var(--sf-border);
}
[data-testid="stSidebar"] .block-container{padding-top:1.2rem;}
[data-testid="stSidebar"] label[data-baseweb="radio"]{
  display:flex;align-items:center;gap:.4rem;
  width:100%;padding:.42rem .6rem;margin:.12rem 0;
  border-radius:11px;border:1px solid transparent;
  font-size:.93rem;cursor:pointer;
  transition:background .15s ease,border-color .15s ease,transform .12s ease;
}
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child{display:none;}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{
  background:rgba(255,255,255,.055);transform:translateX(2px);
}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){
  background:linear-gradient(90deg,rgba(124,92,255,.28),rgba(34,211,238,.10));
  border-color:rgba(124,92,255,.55);
}
[data-testid="stSidebar"] label[data-baseweb="radio"] p{
  font-size:.93rem !important;margin:0 !important;
}

/* ---------- Marca ---------- */
.sf-brand{display:flex;align-items:center;gap:.7rem;margin:.2rem 0 1.1rem;}
.sf-brand-logo{
  width:42px;height:42px;border-radius:13px;display:grid;place-items:center;
  font-size:1.35rem;
  background:linear-gradient(135deg,var(--sf-brand),var(--sf-brand-2));
  box-shadow:0 10px 26px -12px rgba(124,92,255,.9);
}
.sf-brand-name{font-weight:800;font-size:1.18rem;letter-spacing:-.02em;line-height:1;}
.sf-brand-sub{font-size:.72rem;color:var(--sf-muted);letter-spacing:.13em;text-transform:uppercase;}

/* ---------- Hero ---------- */
.sf-hero{
  position:relative;overflow:hidden;
  display:flex;gap:1.1rem;align-items:center;
  padding:1.5rem 1.6rem;margin:0 0 1.4rem;
  border-radius:22px;border:1px solid var(--sf-border);
  background:linear-gradient(120deg,rgba(124,92,255,.20),rgba(34,211,238,.07) 55%,rgba(255,255,255,.03));
}
.sf-hero::after{
  content:"";position:absolute;inset:-60% -20% auto auto;width:340px;height:340px;
  background:radial-gradient(circle,rgba(34,211,238,.25),transparent 65%);
  filter:blur(6px);
}
.sf-hero-icon{
  flex:0 0 auto;width:62px;height:62px;border-radius:19px;display:grid;place-items:center;
  font-size:2rem;background:rgba(255,255,255,.08);border:1px solid var(--sf-border);
  backdrop-filter:blur(6px);
}
.sf-hero h1{
  margin:0;font-size:1.85rem;font-weight:800;letter-spacing:-.03em;line-height:1.15;
  background:linear-gradient(90deg,#fff,#C9D2FF 60%,#8FE9FF);
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.sf-hero p{margin:.32rem 0 0;color:var(--sf-muted);font-size:.98rem;max-width:70ch;}
.sf-chips{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.7rem;}
.sf-chip{
  font-size:.75rem;padding:.2rem .6rem;border-radius:999px;
  background:rgba(255,255,255,.07);border:1px solid var(--sf-border);color:#CBD3F0;
}

/* ---------- Secciones ---------- */
.sf-h2{
  display:flex;align-items:center;gap:.55rem;
  margin:1.9rem 0 .7rem;font-size:1.22rem;font-weight:700;letter-spacing:-.015em;color:#F1F3FF;
}
.sf-h2::before{
  content:"";width:5px;height:1.15em;border-radius:99px;
  background:linear-gradient(180deg,var(--sf-brand),var(--sf-brand-2));
}

/* ---------- Tarjetas ---------- */
.sf-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:.75rem;margin:.5rem 0 .2rem;}
.sf-card{
  padding:.95rem 1rem;border-radius:var(--sf-radius);
  border:1px solid var(--sf-border);background:var(--sf-card);
  transition:transform .15s ease,border-color .15s ease,background .15s ease;
}
.sf-card:hover{transform:translateY(-2px);border-color:rgba(124,92,255,.45);background:var(--sf-card-2);}
.sf-card-ico{font-size:1.3rem;}
.sf-card-t{font-weight:700;margin:.35rem 0 .2rem;font-size:.98rem;color:#EFF1FF;}
.sf-card-b{font-size:.87rem;color:var(--sf-muted);line-height:1.5;}
.sf-card-b code{background:rgba(255,255,255,.09);padding:.05rem .3rem;border-radius:6px;font-size:.85em;color:#B9C4FF;}

/* ---------- Callouts ---------- */
.sf-call{
  display:flex;gap:.7rem;align-items:flex-start;
  padding:.8rem .95rem;margin:.7rem 0;border-radius:14px;
  border:1px solid var(--sf-border);border-left-width:3px;
  background:var(--sf-card);font-size:.92rem;line-height:1.55;color:#DDE2F6;
}
.sf-call b{color:#fff;}
.sf-call code{background:rgba(255,255,255,.10);padding:.05rem .32rem;border-radius:6px;font-size:.86em;color:#B9C4FF;}
.sf-call-ico{font-size:1.05rem;line-height:1.4;}
.sf-tip{border-left-color:var(--sf-brand-2);background:linear-gradient(90deg,rgba(34,211,238,.10),rgba(255,255,255,.03));}
.sf-warn{border-left-color:var(--sf-warn);background:linear-gradient(90deg,rgba(251,191,36,.10),rgba(255,255,255,.03));}
.sf-key{border-left-color:var(--sf-brand);background:linear-gradient(90deg,rgba(124,92,255,.14),rgba(255,255,255,.03));}
.sf-bad{border-left-color:var(--sf-bad);background:linear-gradient(90deg,rgba(251,113,133,.10),rgba(255,255,255,.03));}

/* ---------- Salida de la sandbox ---------- */
.sf-out{
  border-radius:14px;border:1px solid var(--sf-border);
  background:rgba(3,6,14,.75);padding:.75rem .9rem;margin:.15rem 0 .3rem;
}
.sf-out-h{
  font-size:.71rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--sf-muted);margin-bottom:.4rem;display:flex;gap:.5rem;align-items:center;
}
.sf-out pre{
  margin:0 !important;background:transparent !important;border:none !important;padding:0 !important;
  white-space:pre-wrap;word-break:break-word;font-size:.88rem;color:#D7F7E8;line-height:1.55;
}
.sf-out.err pre{color:#FFD3DA;}
.sf-dot{width:8px;height:8px;border-radius:99px;display:inline-block;}
.sf-dot.ok{background:var(--sf-ok);box-shadow:0 0 10px var(--sf-ok);}
.sf-dot.no{background:var(--sf-bad);box-shadow:0 0 10px var(--sf-bad);}

/* ---------- Insignias ---------- */
.sf-badge{
  display:inline-block;font-size:.72rem;font-weight:700;
  padding:.16rem .55rem;border-radius:999px;border:1px solid transparent;
}
.sf-num{
  display:inline-grid;place-items:center;width:26px;height:26px;border-radius:9px;
  background:linear-gradient(135deg,var(--sf-brand),var(--sf-brand-2));
  color:#0A0D18;font-weight:800;font-size:.85rem;margin-right:.5rem;
}

/* ---------- Progreso ---------- */
.sf-bar{height:9px;border-radius:99px;background:rgba(255,255,255,.09);overflow:hidden;margin:.45rem 0 .3rem;}
.sf-bar span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--sf-brand),var(--sf-brand-2));}
.sf-mini{font-size:.78rem;color:var(--sf-muted);}

/* ---------- Tablas ---------- */
.sf-table table{width:100%;border-collapse:collapse;font-size:.9rem;}
.sf-table th{
  text-align:left;padding:.5rem .7rem;color:#C6CEF0;font-weight:600;
  border-bottom:1px solid var(--sf-border);background:rgba(255,255,255,.04);
}
.sf-table td{padding:.45rem .7rem;border-bottom:1px solid rgba(255,255,255,.06);color:#DDE2F6;}
.sf-table tr:last-child td{border-bottom:none;}
.sf-table code{background:rgba(255,255,255,.09);padding:.05rem .32rem;border-radius:6px;color:#B9C4FF;}

/* ---------- Expander / tabs ---------- */
[data-testid="stExpander"]{border:1px solid var(--sf-border);border-radius:14px;background:var(--sf-card);}
.stTabs [data-baseweb="tab-list"]{gap:.3rem;}
.stTabs [data-baseweb="tab"]{
  border-radius:11px 11px 0 0;padding:.4rem .85rem;font-weight:600;font-size:.9rem;
}
hr{border-color:var(--sf-border) !important;}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Piezas de UI
# --------------------------------------------------------------------------- #


def _md(text: str) -> str:
    """Markdown mínimo (**negrita**, *cursiva* y `código`) para usarlo en HTML."""
    text = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = _re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)", r"<i>\1</i>", text)
    parts = text.split("`")
    out = []
    for i, part in enumerate(parts):
        out.append(part if i % 2 == 0 else f"<code>{part}</code>")
    return "".join(out)


#: Alias público (lo usa app.py para pintar tips en la barra lateral).
md_inline = _md


def hero(icon: str, title: str, subtitle: str, chips: Sequence[str] = ()) -> None:
    chip_html = "".join(f"<span class='sf-chip'>{c}</span>" for c in chips)
    st.markdown(
        f"<div class='sf-hero'><div class='sf-hero-icon'>{icon}</div>"
        f"<div><h1>{title}</h1><p>{_md(subtitle)}</p>"
        f"<div class='sf-chips'>{chip_html}</div></div></div>",
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f"<div class='sf-h2'>{title}</div>", unsafe_allow_html=True)


def callout(kind: str, text: str, title: str | None = None) -> None:
    icons = {"tip": "💡", "warn": "⚠️", "key": "🔑", "bad": "🚫"}
    titles = {"tip": "Mini tip", "warn": "Trampa frecuente", "key": "Idea clave", "bad": "Evita esto"}
    ico = icons.get(kind, "💡")
    head = title if title is not None else titles.get(kind, "")
    body = f"<b>{head}:</b> {_md(text)}" if head else _md(text)
    st.markdown(
        f"<div class='sf-call sf-{kind}'><div class='sf-call-ico'>{ico}</div><div>{body}</div></div>",
        unsafe_allow_html=True,
    )


def cards(items: Iterable[tuple[str, str, str]]) -> None:
    body = "".join(
        f"<div class='sf-card'><div class='sf-card-ico'>{ico}</div>"
        f"<div class='sf-card-t'>{t}</div><div class='sf-card-b'>{_md(b)}</div></div>"
        for ico, t, b in items
    )
    st.markdown(f"<div class='sf-grid'>{body}</div>", unsafe_allow_html=True)


def table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    head = "".join(f"<th>{_html.escape(str(h), quote=False)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_md(_html.escape(str(c), quote=False))}</td>" for c in row)
        + "</tr>"
        for row in rows
    )
    st.markdown(
        f"<div class='sf-table'><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def badge(text: str, color: str = "#7C5CFF", bg: str = "rgba(124,92,255,.16)") -> str:
    return f"<span class='sf-badge' style='color:{color};background:{bg};border-color:{color}55'>{text}</span>"


def progress_bar(pct: float, label: str = "") -> None:
    pct = max(0.0, min(100.0, pct))
    extra = f"<div class='sf-mini'>{label}</div>" if label else ""
    st.markdown(
        f"<div class='sf-bar'><span style='width:{pct:.0f}%'></span></div>{extra}",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Resultado de ejecución
# --------------------------------------------------------------------------- #


def render_result(res: RunResult) -> None:
    if res.has_error:
        if res.stdout:
            st.markdown(
                "<div class='sf-out'><div class='sf-out-h'><span class='sf-dot ok'></span>"
                "Salida antes del error</div><pre>"
                f"{_html.escape(res.stdout)}</pre></div>",
                unsafe_allow_html=True,
            )
        where = f" · línea {res.lineno}" if res.lineno else ""
        st.markdown(
            "<div class='sf-out err'><div class='sf-out-h'><span class='sf-dot no'></span>"
            f"{_html.escape(res.error_type)}{where}</div><pre>"
            f"{_html.escape(res.error)}</pre></div>",
            unsafe_allow_html=True,
        )
        if res.hint:
            callout("tip", res.hint, title="Cómo arreglarlo")
        return

    salida = res.stdout if res.stdout else "(el programa terminó sin imprimir nada)"
    st.markdown(
        "<div class='sf-out'><div class='sf-out-h'><span class='sf-dot ok'></span>"
        f"Salida · {res.seconds*1000:.0f} ms</div><pre>{_html.escape(salida)}</pre></div>",
        unsafe_allow_html=True,
    )
    if res.truncated:
        st.caption("✂️ La salida es muy larga y se cortó. ¿Seguro que el bucle termina?")


# --------------------------------------------------------------------------- #
# Bloque de código ejecutable
# --------------------------------------------------------------------------- #


def demo(code: str, key: str, stdin: str = "", caption: str | None = None) -> None:
    """Muestra un ejemplo con botones para ejecutarlo o llevarlo a la sandbox."""
    code = code.strip("\n")
    if caption:
        st.markdown(f"<div class='sf-mini' style='margin-bottom:.3rem'>{_md(caption)}</div>",
                    unsafe_allow_html=True)
    st.code(code, language="python")

    c1, c2, _ = st.columns([1.05, 1.45, 3.5])
    if c1.button("▶ Ejecutar", key=f"run_{key}"):
        st.session_state.runs[key] = run_user_code(code, stdin)
    if c2.button("🧪 Llevar a la sandbox", key=f"snd_{key}"):
        st.session_state["_load_code"] = code
        st.session_state["_load_stdin"] = stdin
        st.session_state["_goto"] = PAGE_SANDBOX
        st.rerun()

    res = st.session_state.runs.get(key)
    if res is not None:
        render_result(res)


def compare(bad: str, good: str, note: str = "") -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='sf-mini'>🚫 <b>Así no</b></div>", unsafe_allow_html=True)
        st.code(bad.strip("\n"), language="python")
    with c2:
        st.markdown("<div class='sf-mini'>✅ <b>Así sí</b></div>", unsafe_allow_html=True)
        st.code(good.strip("\n"), language="python")
    if note:
        callout("key", note, title="Por qué")


# --------------------------------------------------------------------------- #
# Bloques declarativos de una lección
# --------------------------------------------------------------------------- #


def render_blocks(blocks: Sequence[tuple], prefix: str) -> None:
    for i, block in enumerate(blocks):
        kind, rest = block[0], block[1:]
        key = f"{prefix}_{i}"
        if kind == "h":
            section(rest[0])
        elif kind == "md":
            st.markdown(rest[0])
        elif kind == "code":
            demo(rest[0], key, stdin=rest[1] if len(rest) > 1 else "",
                 caption=rest[2] if len(rest) > 2 else None)
        elif kind == "show":
            st.code(rest[0].strip("\n"), language="python")
        elif kind in ("tip", "warn", "key", "bad"):
            callout(kind, rest[0], title=rest[1] if len(rest) > 1 else None)
        elif kind == "cards":
            cards(rest[0])
        elif kind == "table":
            table(rest[0], rest[1])
        elif kind == "cmp":
            compare(rest[0], rest[1], rest[2] if len(rest) > 2 else "")
        else:  # pragma: no cover - error de contenido, no del usuario
            st.warning(f"Bloque desconocido: {kind}")


# --------------------------------------------------------------------------- #
# Quiz
# --------------------------------------------------------------------------- #


def quiz(lesson_id: str, questions: Sequence[dict]) -> None:
    section("🧠 Comprueba que quedó claro")
    for i, q in enumerate(questions):
        qid = f"{lesson_id}_q{i}"
        st.markdown(
            f"<div style='margin:.9rem 0 .1rem'><span class='sf-num'>{i+1}</span>"
            f"<b>{_md(q['q'])}</b></div>",
            unsafe_allow_html=True,
        )
        choice = st.radio(
            "opciones", q["options"], index=None, key=f"radio_{qid}",
            label_visibility="collapsed",
        )
        if choice is None:
            continue
        if q["options"].index(choice) == q["answer"]:
            if award(f"quiz_{qid}", 10):
                st.toast("¡Correcto! +10 XP", icon="🎯")
            st.success(f"✅ Correcto. {q.get('why', '')}")
        else:
            st.error(f"❌ Casi. {q.get('hint', 'Vuelve a leer el ejemplo de arriba.')}")


# --------------------------------------------------------------------------- #
# Retos autoevaluados
# --------------------------------------------------------------------------- #


def _run_tests(ch: dict, code: str) -> tuple[RunResult, list[tuple[str, bool, str]]]:
    res = run_user_code(code, ch.get("stdin", ""), timeout=ch.get("timeout", 8.0))
    rows: list[tuple[str, bool, str]] = []
    if res.has_error:
        return res, rows
    for test in ch["tests"]:
        try:
            ok, detail = test["check"](res)
        except Exception as exc:  # noqa: BLE001 - un checker no debe tumbar la app
            ok, detail = False, f"no se pudo comprobar ({type(exc).__name__}: {exc})"
        rows.append((test["label"], bool(ok), detail))
    return res, rows


def challenge(ch: dict, show_header: bool = True) -> None:
    cid = ch["id"]
    code_key = f"code_{cid}"
    res_key = f"res_{cid}"

    # Reinicio pedido en la ejecución anterior (se aplica ANTES de crear el widget).
    if st.session_state.get("_reset_challenge") == cid:
        st.session_state[code_key] = ch["starter"].strip("\n")
        st.session_state.pop("_reset_challenge")
        st.session_state.pop(res_key, None)

    if show_header:
        color, bg = LEVEL_COLORS.get(ch.get("level", "Fácil"), LEVEL_COLORS["Fácil"])
        check = " ✅" if f"reto_{cid}" in st.session_state.done else ""
        st.markdown(
            f"<div class='sf-h2'>🏁 {ch['title']}{check} &nbsp;"
            f"{badge(ch.get('level', 'Fácil'), color, bg)}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(ch["prompt"])

    st.session_state.setdefault(code_key, ch["starter"].strip("\n"))
    st.text_area(
        "Tu código", key=code_key,
        height=ch.get("height", 220), label_visibility="collapsed",
    )
    if ch.get("stdin"):
        st.caption(f"📥 Entrada simulada para tu `input()`: `{ch['stdin'].replace(chr(10), ' ⏎ ')}`")

    c1, c2, c3 = st.columns([1.2, 1.1, 3.4])
    if c1.button("✅ Comprobar", key=f"btn_check_{cid}", type="primary"):
        st.session_state[res_key] = _run_tests(ch, st.session_state[code_key])
    if c2.button("↺ Reiniciar", key=f"btn_reset_{cid}"):
        st.session_state["_reset_challenge"] = cid
        st.rerun()

    stored = st.session_state.get(res_key)
    if stored:
        res, rows = stored
        if res.has_error:
            st.markdown("<div class='sf-mini'>Tu código no llegó a terminar:</div>",
                        unsafe_allow_html=True)
            render_result(res)
        else:
            if res.stdout:
                render_result(res)
            passed = sum(1 for _, ok, _ in rows if ok)
            for label, ok, detail in rows:
                icon = "✅" if ok else "❌"
                extra = f" — {detail}" if detail else ""
                st.markdown(f"{icon} **{label}**{extra}")
            if rows and passed == len(rows):
                if award(f"reto_{cid}", ch.get("points", 25)):
                    st.balloons()
                    st.success(f"🎉 ¡Reto superado! +{ch.get('points', 25)} XP")
                else:
                    st.success("🎉 ¡Sigue correcto!")
            elif rows:
                st.info(f"Vas {passed} de {len(rows)}. Ajusta y vuelve a comprobar.")

    with st.expander("💡 Pista"):
        st.markdown(ch.get("hint", "Descompón el problema en pasos y prueba cada uno por separado."))
    with st.expander("🔓 Ver una solución posible (intenta primero, de verdad)"):
        st.code(ch["solution"].strip("\n"), language="python")
        if ch.get("solution_note"):
            st.caption(ch["solution_note"])


# --------------------------------------------------------------------------- #
# Helpers para escribir tests de retos en lessons.py
# --------------------------------------------------------------------------- #


def t_stdout_contains(fragment: str, label: str | None = None,
                      ci: bool = True) -> dict:
    def check(res: RunResult) -> tuple[bool, str]:
        got = res.stdout.lower() if ci else res.stdout
        want = fragment.lower() if ci else fragment
        if want in got:
            return True, ""
        return False, f"no encontré «{fragment}» en la salida"

    return {"label": label or f"La salida contiene «{fragment}»", "check": check}


def t_stdout_equals(expected: str, label: str = "La salida es exactamente la esperada") -> dict:
    def check(res: RunResult) -> tuple[bool, str]:
        got = res.stdout.strip().replace("\r\n", "\n")
        want = expected.strip().replace("\r\n", "\n")
        if got == want:
            return True, ""
        return False, f"esperaba `{want!r}` y obtuve `{got!r}`"

    return {"label": label, "check": check}


def t_var(name: str, expected: Any, label: str | None = None) -> dict:
    def check(res: RunResult) -> tuple[bool, str]:
        if name not in res.namespace:
            return False, f"no existe la variable `{name}`"
        got = res.namespace[name]
        if got == expected and type(got) is type(expected):
            return True, ""
        return False, f"`{name}` vale {got!r} y esperaba {expected!r}"

    return {"label": label or f"La variable `{name}` es correcta", "check": check}


def t_func(name: str, cases: Sequence[tuple[tuple, Any]],
           label: str | None = None) -> dict:
    """Comprueba que existe la función ``name`` y que devuelve lo esperado."""
    from sandbox import call_safely, pretty

    def check(res: RunResult) -> tuple[bool, str]:
        fn = res.namespace.get(name)
        if fn is None:
            return False, f"no encontré la función `{name}`"
        if not callable(fn):
            return False, f"`{name}` existe pero no es una función"
        for args, expected in cases:
            ok, value, err = call_safely(fn, args)
            if not ok:
                return False, f"{name}{args!r} falló: {err}"
            if value != expected:
                return False, (f"{name}{args!r} devolvió {pretty(value)} "
                               f"y esperaba {pretty(expected)}")
        return True, f"{len(cases)} casos probados"

    return {"label": label or f"`{name}()` devuelve los valores correctos", "check": check}


def t_num(name: str, expected: float, tol: float = 1e-6,
          label: str | None = None) -> dict:
    """Como :func:`t_var` pero para números (tolera los decimales de float)."""

    def check(res: RunResult) -> tuple[bool, str]:
        if name not in res.namespace:
            return False, f"no existe la variable `{name}`"
        got = res.namespace[name]
        if isinstance(got, bool) or not isinstance(got, (int, float)):
            return False, f"`{name}` debería ser un número y es {type(got).__name__}"
        if abs(got - expected) <= tol:
            return True, ""
        return False, f"`{name}` vale {got!r} y esperaba {expected!r}"

    return {"label": label or f"La variable `{name}` es correcta", "check": check}


def t_rerun_contains(stdin: str, fragment: str, label: str | None = None,
                     ci: bool = True) -> dict:
    """Vuelve a ejecutar el mismo código con otra entrada y revisa la salida."""

    def check(res: RunResult) -> tuple[bool, str]:
        again = run_user_code(res.code, stdin)
        if again.has_error:
            return False, f"con esa entrada falló: {again.error_type} — {again.error}"
        got = again.stdout.lower() if ci else again.stdout
        want = fragment.lower() if ci else fragment
        if want in got:
            return True, ""
        return False, (f"esperaba ver «{fragment}» y la salida fue "
                       f"«{again.stdout.strip()}»")

    entrada = stdin.strip().replace("\n", " / ")
    return {"label": label or f"Con la entrada «{entrada}» responde bien", "check": check}


def t_defined(name: str, label: str | None = None) -> dict:
    def check(res: RunResult) -> tuple[bool, str]:
        if name in res.namespace:
            return True, ""
        return False, f"no encontré `{name}`"

    return {"label": label or f"Definiste `{name}`", "check": check}


def t_custom(label: str, fn: Callable[[RunResult], tuple[bool, str]]) -> dict:
    return {"label": label, "check": fn}
