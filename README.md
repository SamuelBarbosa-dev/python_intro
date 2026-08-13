# 🐍 PyLab — Python de cero a funciones

App de Streamlit para que estudiantes de posgrado aprendan Python rápido:
**teoría mínima + código ejecutable + mini tips + retos que se corrigen solos.**

La ruta llega exactamente hasta **funciones**, que es la meta del curso.

---

## Cómo se ejecuta

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

Se abre en `http://localhost:8501`. No hace falta nada más: ni base de datos, ni
cuentas, ni internet (salvo por la fuente tipográfica, que degrada sin problema).

---

## Qué trae

| Sección | Qué hace |
|---|---|
| **10 lecciones** | De `print("Hola")` a funciones. Cada ejemplo se ejecuta con un botón. |
| **🧪 Sandbox libre** | Editor de Python real, con `input()` simulado y errores traducidos al español. |
| **🏆 16 retos** | Se autoevalúan: dicen qué caso falló, con qué valor y por qué. Traen pista y solución. |
| **📋 Chuleta** | Todo el curso en una página, descargable en `.md`. |
| **📈 Mi progreso** | XP, niveles y avance lección por lección. |
| **💡 Mini tips** | Repartidos por todas las lecciones + un tip rotativo en la barra lateral. |

**28 preguntas de quiz** con retroalimentación inmediata y **16 retos**
autoevaluados (49 ejemplos ejecutables en total).

### Contenido de las lecciones

1. Empieza aquí — cómo estudiar (y cómo no)
2. Variables y tipos — `int`, `float`, `str`, `bool`, `None`, casting, PEP 8
3. Operadores — `//`, `%`, comparación, lógicos, cortocircuito, precedencia
4. Cadenas de texto — f-strings, slicing, `strip/split/join/replace`
5. Entrada y salida — `input()`, formato de `print()`, `try/except`
6. Condicionales — `if/elif/else`, indentación, guard clauses, ternario
7. Bucles — `for`, `range`, `enumerate`, `zip`, `while`, `break`, comprensiones
8. Listas y tuplas — métodos, copia vs. referencia, desempaquetado
9. Diccionarios y conjuntos — `.get()`, `.items()`, conteo, `set`
10. Funciones — `def`, `return`, defaults, `*args`/`**kwargs`, ámbito, `lambda`

---

## Estructura del proyecto

```
app.py        Navegación y páginas (sandbox, retos, chuleta, progreso)
lessons.py    Todo el contenido: lecciones, quizzes y retos con sus tests
ui.py         Estilos + componentes (hero, tarjetas, callouts, quiz, reto)
sandbox.py    Motor de ejecución: lista blanca, timeout, errores en español
```

Para **agregar una lección** basta con añadir un diccionario a `LESSONS` en
`lessons.py`; los bloques son tuplas declarativas (`"md"`, `"code"`, `"tip"`,
`"cards"`, `"table"`, `"cmp"`...). Para **agregar un reto**, añade un diccionario
con sus `tests` usando los helpers `t_func`, `t_var`, `t_num`,
`t_stdout_contains`, `t_rerun_contains` o `t_custom`.

---

## Sobre la sandbox (importante)

El código del estudiante se ejecuta **en el mismo proceso de Streamlit**, con:

- lista blanca de módulos (`math`, `random`, `datetime`, `json`, `re`...);
- bloqueo de `open`, `eval`, `exec`, `__import__` y de los atributos de escape;
- `print` capturado, `input()` alimentado desde la caja «Entrada»;
- corte a los 8 segundos (bucles infinitos) y tope de salida (20 000 caracteres);
- errores traducidos al español con una pista de cómo arreglarlos.

Es una barrera **pedagógica**, no una caja de seguridad real: sirve para que un
estudiante no borre un archivo sin querer, no para resistir a alguien que quiera
saltársela a propósito. Úsala en tu máquina o en un servidor del curso, no la
publiques en internet abierta.

---

## Publicarla en Streamlit Community Cloud (gratis)

1. Entra a **[share.streamlit.io](https://share.streamlit.io)** e inicia sesión
   con la cuenta de GitHub dueña del repositorio.
2. **Create app → Deploy a public app from GitHub** y completa:
   - Repository: `mister-ty/python_intro`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: el subdominio gratuito que quieras, p. ej. `pylab-posgrado`
     → queda como `https://pylab-posgrado.streamlit.app`
3. **Deploy**. En un par de minutos la URL queda pública y lista para pasarla al
   curso. Cada `git push` a `main` la redespliega sola.

No hay que configurar nada más: `requirements.txt` instala Streamlit y
`.streamlit/config.toml` aplica el tema oscuro.

> ⚠️ Antes de repartir el enlace, lee la sección anterior sobre la sandbox: la
> app ejecuta el código Python de quien entre. En Streamlit Cloud eso ocurre
> dentro de un contenedor aislado y desechable de ellos (no en tu máquina), pero
> conviene igual compartir el enlace con el grupo del curso y no en abierto.

---

## Si tu carpeta local tiene una llave `}` en la ruta

Streamlit, cuando no encuentra un `secrets.toml`, arma su mensaje de error con
`.format()` sobre una cadena que incluye la ruta del proyecto. Si esa ruta
contiene una `}`, la app ni siquiera arranca:

```
ValueError: Single '}' encountered in format string
```

Solución: crea un archivo vacío `.streamlit/secrets.toml` (está en el
`.gitignore`, como debe ser, así que no viaja en el repositorio) o renombra la
carpeta quitándole la llave. En Streamlit Cloud el problema no existe.
