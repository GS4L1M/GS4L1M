"""Gera os painéis SVG animados (tema Blade Runner) do README de perfil do GitHub.

Uso:  python assets/gera_svgs.py
Os arquivos são gravados na mesma pasta deste script.
"""
import os
import random
from xml.sax.saxutils import escape as esc

random.seed(2049)

OUT = os.path.dirname(os.path.abspath(__file__))

# Paleta
BG = "#07030D"
PANEL = "#0B0614"
MAGENTA = "#FF2A6D"
CYAN = "#05D9E8"
ORANGE = "#FF8C1A"
PURPLE = "#B266FF"
TEXT = "#D1F7FF"
MUTED = "#7C6A99"

TITLE_FONT = "'Arial Black','Segoe UI Black','Helvetica Neue',Arial,sans-serif"
MONO = "Consolas,'SFMono-Regular','Liberation Mono','Courier New',monospace"
JP = "'Yu Gothic','Hiragino Kaku Gothic Pro',Meiryo,'MS Gothic','Noto Sans CJK JP',sans-serif"


# ---------------------------------------------------------------- blocos comuns
def defs_common():
    return f"""
  <filter id="neon" x="-30%" y="-60%" width="160%" height="220%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="b1"/>
    <feGaussianBlur in="SourceGraphic" stdDeviation="9" result="b2"/>
    <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="2"/>
  </filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#000" fill-opacity=".35"/>
  </pattern>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0H0V40" fill="none" stroke="{CYAN}" stroke-opacity=".06"/>
  </pattern>"""


def rain_pattern(pid, w=140, h=180, n=14, color="#9FD8FF", op=0.35, speed=0.55, slant=-4):
    lines = []
    for _ in range(n):
        x = random.uniform(0, w)
        y = random.uniform(0, h)
        ln = random.uniform(10, 26)
        o = round(random.uniform(op * 0.4, op), 2)
        for dy in (0, -h):  # repetido uma altura acima: a costura fica invisível
            lines.append(f'<line x1="{x:.1f}" y1="{y + dy:.1f}" x2="{x + slant:.1f}" y2="{y + dy + ln:.1f}" '
                         f'stroke="{color}" stroke-opacity="{o}" stroke-width="1"/>')
    return (f'<pattern id="{pid}" width="{w}" height="{h}" patternUnits="userSpaceOnUse">'
            f'{"".join(lines)}'
            f'<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="0 {h}" '
            f'dur="{speed}s" repeatCount="indefinite"/></pattern>')


def corners(x, y, w, h, color, size=18, sw=2):
    p = []
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        p.append(f'<path d="M{cx} {cy + dy * size}V{cy}H{cx + dx * size}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
    return "".join(p)


def flicker(dur=6.0, begin=0.0):
    return (f'<animate attributeName="opacity" values="1;1;.25;1;.7;1;1;.4;1" '
            f'keyTimes="0;.62;.64;.66;.7;.72;.9;.92;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')


def blink(dur=1.2):
    return f'<animate attributeName="opacity" values="1;0;1" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>'


def svg_open(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(label)}">')


# ---------------------------------------------------------------- cabeçalho
def buildings(y_base, min_h, max_h, color, win_colors, win_op, x0=0, x1=1200, flick=0.08):
    out = []
    x = x0
    while x < x1:
        w = random.randint(28, 70)
        h = random.randint(min_h, max_h)
        top = y_base - h
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h + 200}" fill="{color}"/>')
        if random.random() < .3:  # antena
            ax = x + random.randint(6, w - 6)
            out.append(f'<line x1="{ax}" y1="{top}" x2="{ax}" y2="{top - random.randint(10, 30)}" stroke="{color}" stroke-width="2"/>')
        for wy in range(top + 6, y_base, 9):
            for wx in range(x + 4, x + w - 5, 7):
                if random.random() < .22:
                    c = random.choice(win_colors)
                    o = round(random.uniform(win_op * .4, win_op), 2)
                    anim = ""
                    if random.random() < flick:
                        d = random.uniform(2, 9)
                        anim = (f'<animate attributeName="opacity" values="{o};.05;{o}" dur="{d:.1f}s" '
                                f'begin="{-random.uniform(0, d):.1f}s" repeatCount="indefinite"/>')
                    out.append(f'<rect x="{wx}" y="{wy}" width="3" height="4" fill="{c}" opacity="{o}">{anim}</rect>')
        x += w + random.randint(0, 6)
    return "".join(out)


def neon_sign(x, y, text, color, vertical=False, size=22, dur=5.0, begin=0.0, font=JP):
    if vertical:
        chars = "".join(f'<tspan x="{x}" dy="{size + 4 if i else 0}">{esc(c)}</tspan>' for i, c in enumerate(text))
        h = len(text) * (size + 4) + 14
        box = (f'<rect x="{x - size / 2 - 7}" y="{y - size - 6}" width="{size + 14}" height="{h}" rx="3" '
               f'fill="#0A0410" stroke="{color}" stroke-opacity=".7"/>')
    else:
        chars = esc(text)
        w = len(text) * size * .62 + 20
        box = (f'<rect x="{x - w / 2:.0f}" y="{y - size - 4}" width="{w:.0f}" height="{size + 14}" rx="3" '
               f'fill="#0A0410" stroke="{color}" stroke-opacity=".7"/>')
    t = (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="bold" fill="{color}" '
         f'text-anchor="middle" filter="url(#neon)">{chars}</text>')
    return f'<g>{box}{t}{flicker(dur, begin)}</g>'


def header():
    W, H = 1200, 460
    s = [svg_open(W, H, "GUSTAVO SALIM - Cientista de Dados e Desenvolvedor Python"), "<defs>", defs_common()]
    s.append(f"""
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#05020A"/>
    <stop offset=".45" stop-color="#1A0626"/>
    <stop offset=".75" stop-color="#4A0F3A"/>
    <stop offset="1" stop-color="#C2410C"/>
  </linearGradient>
  <radialGradient id="haze" cx="50%" cy="100%" r="60%">
    <stop offset="0" stop-color="{ORANGE}" stop-opacity=".55"/>
    <stop offset=".5" stop-color="{MAGENTA}" stop-opacity=".18"/>
    <stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0" stop-color="#FFF3D6" stop-opacity=".35"/>
    <stop offset="1" stop-color="#FFF3D6" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="headlight" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#FFF3D6" stop-opacity=".45"/>
    <stop offset="1" stop-color="#FFF3D6" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}" stop-opacity="0"/>
    <stop offset="1" stop-color="{BG}" stop-opacity="1"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="45%" r="75%">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".8"/>
  </radialGradient>
  <radialGradient id="flame" cx="50%" cy="80%" r="60%">
    <stop offset="0" stop-color="#FFF1C1"/>
    <stop offset=".4" stop-color="{ORANGE}"/>
    <stop offset="1" stop-color="#FF3D00" stop-opacity="0"/>
  </radialGradient>""")
    s.append(rain_pattern("rainA", n=16, op=.35, speed=.5))
    s.append(rain_pattern("rainB", w=90, h=120, n=10, op=.22, speed=.8, slant=-3))
    s.append("</defs>")

    s.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#haze)"/>')

    # holofotes varrendo o céu
    for cx, a0, a1, d in ((250, -25, 20, 14), (900, 15, -30, 18), (620, -10, 25, 22)):
        s.append(f'<g opacity=".55"><polygon points="{cx - 6},{H} {cx + 6},{H} {cx + 90},0 {cx - 90},0" fill="url(#beam)">'
                 f'<animateTransform attributeName="transform" type="rotate" values="{a0} {cx} {H};{a1} {cx} {H};{a0} {cx} {H}" '
                 f'dur="{d}s" repeatCount="indefinite"/></polygon></g>')

    # camada distante
    s.append(buildings(H - 70, 60, 170, "#1B0A2A", [ORANGE, MAGENTA, CYAN], .5, flick=.03))

    # pirâmide da Tyrell
    px, pw, ph = 930, 330, 250
    base = H - 60
    s.append(f'<polygon points="{px - pw / 2},{base} {px},{base - ph} {px + pw / 2},{base}" fill="#12061C" stroke="{ORANGE}" stroke-opacity=".35"/>')
    for i in range(1, 14):
        yy = base - i * ph / 14
        half = (pw / 2) * (1 - i / 14)
        o = .5 if i % 3 else .85
        s.append(f'<line x1="{px - half + 4:.1f}" y1="{yy:.1f}" x2="{px + half - 4:.1f}" y2="{yy:.1f}" stroke="{ORANGE}" '
                 f'stroke-opacity="{o}" stroke-dasharray="3 5"/>')
    s.append(f'<circle cx="{px}" cy="{base - ph + 6}" r="3" fill="#FFF1C1" filter="url(#neon)">{blink(2)}</circle>')

    # torres com chamas (a cena de abertura do filme)
    for fx, fy in ((120, H - 185), (205, H - 150), (1110, H - 170)):
        s.append(f'<rect x="{fx - 5}" y="{fy}" width="10" height="200" fill="#0E0518"/>')
        s.append(f'<circle cx="{fx}" cy="{fy - 10}" r="42" fill="{ORANGE}" opacity=".14" filter="url(#soft)">'
                 f'<animate attributeName="opacity" values=".14;.24;.1;.18;.14" dur="1.3s" repeatCount="indefinite"/></circle>')
        s.append(f'<ellipse cx="{fx}" cy="{fy - 16}" rx="10" ry="22" fill="url(#flame)" filter="url(#soft)">'
                 f'<animate attributeName="ry" values="22;30;18;26;22" dur="{random.uniform(.8, 1.4):.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="cy" values="{fy - 16};{fy - 22};{fy - 14};{fy - 19};{fy - 16}" dur="1.1s" repeatCount="indefinite"/></ellipse>')

    s.append(f'<rect width="{W}" height="{H}" fill="url(#rainB)"/>')

    # camada próxima
    s.append(buildings(H - 20, 90, 230, "#0A0410", [CYAN, MAGENTA, "#FFD6A5"], .8, x0=-10, x1=330, flick=.1))
    s.append(buildings(H - 20, 70, 200, "#0A0410", [CYAN, MAGENTA, "#FFD6A5"], .8, x0=1030, x1=1210, flick=.1))

    # letreiros de neon
    s.append(neon_sign(60, H - 210, "データ", MAGENTA, vertical=True, size=20, dur=4.3))
    s.append(neon_sign(292, H - 175, "未来", CYAN, vertical=True, size=20, dur=6.1, begin=1.3))
    s.append(neon_sign(1082, H - 215, "PYTHON", CYAN, size=15, dur=5.2, begin=.7, font=MONO))
    s.append(neon_sign(1160, H - 170, "機械学習", ORANGE, vertical=True, size=15, dur=7.3, begin=2.1))

    # spinner (carro voador) atravessando
    s.append(f"""<g>
    <animateTransform attributeName="transform" type="translate" values="-200 250;1400 215" dur="14s" repeatCount="indefinite"/>
    <polygon points="0,4 280,-30 280,50" fill="url(#headlight)"/>
    <polygon points="0,0 -18,-9 -48,-10 -64,-2 -66,4 -40,8 -6,7" fill="#1C1028" stroke="{CYAN}" stroke-opacity=".6"/>
    <polygon points="-22,-8 -40,-9 -46,-3 -24,-3" fill="{CYAN}" fill-opacity=".35"/>
    <circle cx="-64" cy="1" r="2.5" fill="{MAGENTA}" filter="url(#neon)">{blink(.6)}</circle>
    <circle cx="-2" cy="3" r="2" fill="#FFF" filter="url(#neon)"/>
  </g>""")
    s.append(f"""<g opacity=".75">
    <animateTransform attributeName="transform" type="translate" values="1300 300;-120 318" dur="22s" repeatCount="indefinite"/>
    <polygon points="0,0 12,-5 30,-5 38,1 26,4 4,4" fill="#1C1028"/>
    <circle cx="38" cy="0" r="1.8" fill="{CYAN}" filter="url(#neon)">{blink(.8)}</circle>
  </g>""")

    # névoa, chuva
    s.append(f'<rect y="{H - 150}" width="{W}" height="150" fill="url(#fog)"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#rainA)"/>')

    # título
    s.append(f'<rect x="300" y="84" width="600" height="160" fill="{BG}" fill-opacity=".55" filter="url(#soft)"/>')
    s.append(f'<text x="600" y="160" text-anchor="middle" font-family="{TITLE_FONT}" font-size="72" letter-spacing="6" '
             f'fill="#FFE3EE" stroke="{MAGENTA}" stroke-width="2" filter="url(#neon)">GUSTAVO SALIM{flicker(7, .5)}</text>')
    s.append(f'<text x="600" y="204" text-anchor="middle" font-family="{MONO}" font-size="21" letter-spacing="6" fill="{CYAN}" '
             f'filter="url(#neon)">CIENTISTA DE DADOS  //  DEV PYTHON</text>')
    s.append(f'<line x1="340" y1="226" x2="860" y2="226" stroke="{MAGENTA}" stroke-opacity=".7"/>')

    # HUD
    s.append(f'<g font-family="{MONO}" font-size="12" fill="{CYAN}" fill-opacity=".9">'
             f'<text x="28" y="36">TYRELL CORP. // DIVISÃO DE DADOS</text>'
             f'<text x="28" y="54" fill="{MUTED}">LOS ANGELES, 2049 — SETOR 7</text>'
             f'<text x="1172" y="36" text-anchor="end">SYS.STATUS: <tspan fill="{MAGENTA}">ONLINE</tspan></text>'
             f'<text x="1172" y="54" text-anchor="end" fill="{MUTED}">CHUVA ÁCIDA: 87%  ·  VISIB.: BAIXA</text></g>')
    s.append(f'<circle cx="1038" cy="32" r="4" fill="{MAGENTA}" filter="url(#neon)">{blink(1.4)}</circle>')
    s.append(corners(12, 12, W - 24, H - 24, CYAN, 26, 1.5))

    s.append(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- ficha do replicante
def eye(cx, cy, r):
    rings = []
    for i in range(10, 0, -1):
        rr = r * i / 10
        c = ORANGE if i % 3 == 0 else (CYAN if i > 4 else "#3AA8C1")
        rings.append(f'<circle cx="{cx}" cy="{cy}" r="{rr:.1f}" fill="none" stroke="{c}" stroke-opacity="{.25 + i * .05:.2f}" stroke-width="1.2"/>')
    spokes = []
    for a in range(0, 360, 12):
        spokes.append(f'<line x1="{cx}" y1="{cy - r * .35:.1f}" x2="{cx}" y2="{cy - r * .95:.1f}" stroke="{CYAN}" '
                      f'stroke-opacity=".35" transform="rotate({a} {cx} {cy})"/>')
    return f"""<g>
    <circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="#05020A" stroke="{CYAN}" stroke-opacity=".4"/>
    <g>{"".join(spokes)}<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></g>
    {"".join(rings)}
    <circle cx="{cx}" cy="{cy}" r="{r * .3:.1f}" fill="#000" stroke="{ORANGE}" stroke-width="1.5">
      <animate attributeName="r" values="{r * .3:.1f};{r * .42:.1f};{r * .22:.1f};{r * .3:.1f}" dur="5s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{cx - r * .12:.1f}" cy="{cy - r * .14:.1f}" r="{r * .07:.1f}" fill="#FFF" opacity=".85"/>
    <line x1="{cx - r - 14}" x2="{cx + r + 14}" y1="{cy - r - 10}" y2="{cy - r - 10}" stroke="{MAGENTA}" stroke-width="2" filter="url(#neon)">
      <animate attributeName="y1" values="{cy - r - 10};{cy + r + 10};{cy - r - 10}" dur="3.2s" repeatCount="indefinite"/>
      <animate attributeName="y2" values="{cy - r - 10};{cy + r + 10};{cy - r - 10}" dur="3.2s" repeatCount="indefinite"/>
    </line>
  </g>"""


def id_card():
    W, H = 1200, 400
    s = [svg_open(W, H, "Registro de identificação: Gustavo Salim, Cientista de Dados e Desenvolvedor Python"), "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    s.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="{PANEL}" stroke="{CYAN}" stroke-opacity=".25"/>')
    s.append(corners(20, 20, W - 40, H - 40, CYAN, 22, 2))

    s.append(f'<text x="48" y="62" font-family="{MONO}" font-size="15" letter-spacing="3" fill="{MAGENTA}" filter="url(#neon)">'
             f'&gt; REGISTRO DE IDENTIFICAÇÃO // NEXUS-DS</text>')
    s.append(f'<text x="1152" y="62" text-anchor="end" font-family="{MONO}" font-size="13" fill="{MUTED}">TESTE VOIGHT-KAMPFF: EM ANDAMENTO</text>')
    s.append(f'<line x1="48" y1="78" x2="1152" y2="78" stroke="{CYAN}" stroke-opacity=".25"/>')

    s.append(eye(190, 222, 92))
    s.append(f'<text x="190" y="362" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{CYAN}" fill-opacity=".75">'
             f'ANÁLISE DE ÍRIS<tspan fill="{MAGENTA}">_{blink(1)}</tspan></text>')

    fields = [
        ("NOME", "GUSTAVO SALIM"),
        ("MODELO", "CIENTISTA DE DADOS"),
        ("FUNÇÃO", "DESENVOLVEDOR PYTHON"),
        ("MISSÃO ATUAL", "MACHINE LEARNING — SCIKIT-LEARN, KERAS, TENSORFLOW"),
        ("LEITURA", "\"MÃOS À OBRA: APRENDIZADO DE MÁQUINA\" — A. GÉRON"),
        ("ESPECIALIDADE", "DADOS PÚBLICOS: DATASUS, ANP, OCDE, FMI"),
        ("DIRETRIZ", "TRANSFORMAR TABELAS BAGUNÇADAS EM RESPOSTAS"),
    ]
    y = 118
    for k, v in fields:
        s.append(f'<text x="340" y="{y}" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="2">{esc(k)}</text>')
        s.append(f'<text x="520" y="{y}" font-family="{MONO}" font-size="17" fill="{TEXT}">{esc(v)}</text>')
        s.append(f'<line x1="340" y1="{y + 11}" x2="1152" y2="{y + 11}" stroke="{CYAN}" stroke-opacity=".08"/>')
        y += 34
    s.append(f'<text x="340" y="{y + 6}" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="2">STATUS</text>')
    s.append(f'<circle cx="527" cy="{y + 1}" r="6" fill="{MAGENTA}" filter="url(#neon)">{blink(1.2)}</circle>')
    s.append(f'<text x="542" y="{y + 6}" font-family="{MONO}" font-size="17" fill="{MAGENTA}" filter="url(#neon)">ATIVO — APRENDENDO</text>')

    # código de barras
    bx = 900
    while bx < 1150:
        w = random.choice((1, 1, 2, 3))
        s.append(f'<rect x="{bx}" y="{y - 12}" width="{w}" height="22" fill="{TEXT}" fill-opacity=".55"/>')
        bx += w + random.choice((1, 2, 2, 3))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- habilidades
def chip(x, y, label, color, w=None):
    w = w or (len(label) * 9.6 + 28)
    return (f'<g><rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="30" rx="2" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".75"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 20}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{TEXT}">{esc(label)}</text></g>'), w


def skills():
    W, H = 1200, 400
    s = [svg_open(W, H, "Habilidades: Python, Pandas, NumPy, Scikit-Learn, Matplotlib, Streamlit, Jupyter, Power BI, SQL, HTML5, CSS, JavaScript, Git, GitHub; aprendendo TensorFlow e Keras"),
         "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')

    groups = [
        ("DADOS & MACHINE LEARNING", MAGENTA, ["Python", "Pandas", "NumPy", "Scikit-Learn", "Matplotlib", "Streamlit", "Jupyter"]),
        ("BI & BANCO DE DADOS", ORANGE, ["Power BI", "SQL"]),
        ("WEB", CYAN, ["HTML5", "CSS", "JavaScript"]),
        ("FERRAMENTAS", PURPLE, ["Git", "GitHub", "VS Code"]),
    ]
    px, py = 48, 24
    title, col, items = groups[0]
    s.append(f'<rect x="{px}" y="{py}" width="600" height="200" fill="{PANEL}" stroke="{col}" stroke-opacity=".35"/>')
    s.append(corners(px, py, 600, 200, col, 14, 2))
    s.append(f'<text x="{px + 20}" y="{py + 34}" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{col}">{esc(title)}</text>')
    cx, cy = px + 20, py + 54
    for it in items:
        w = len(it) * 9.6 + 28
        if cx + w > px + 580:
            cx, cy = px + 20, cy + 44
        c, w = chip(cx, cy, it, col, w)
        s.append(c)
        cx += w + 12
    s.append(f'<text x="{px + 20}" y="{py + 184}" font-family="{MONO}" font-size="12" fill="{MUTED}">MÓDULO PRINCIPAL · CARREGADO</text>')
    s.append(f'<circle cx="{px + 580}" cy="{py + 180}" r="4" fill="{col}" filter="url(#neon)">{blink(1.6)}</circle>')

    rx = 672
    for i, (title, col, items) in enumerate(groups[1:]):
        ry = py + i * 70
        s.append(f'<rect x="{rx}" y="{ry}" width="480" height="60" fill="{PANEL}" stroke="{col}" stroke-opacity=".35"/>')
        s.append(f'<rect x="{rx}" y="{ry}" width="4" height="60" fill="{col}" filter="url(#neon)"/>')
        s.append(f'<text x="{rx + 20}" y="{ry + 35}" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{col}">{esc(title)}</text>')
        cx = rx + 480 - 14
        for it in reversed(items):
            w = len(it) * 9.6 + 28
            cx -= w
            c, _ = chip(cx, ry + 15, it, col, w)
            s.append(c)
            cx -= 10

    # upgrade em andamento
    uy = 250
    s.append(f'<rect x="48" y="{uy}" width="1104" height="80" fill="{PANEL}" stroke="{ORANGE}" stroke-opacity=".35"/>')
    s.append(corners(48, uy, 1104, 80, ORANGE, 12, 2))
    s.append(f'<text x="70" y="{uy + 33}" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{ORANGE}">UPGRADE EM ANDAMENTO</text>')
    s.append(f'<text x="70" y="{uy + 58}" font-family="{MONO}" font-size="16" fill="{TEXT}">TensorFlow  ·  Keras  ·  Redes Neurais</text>')
    bx, bw = 560, 500
    s.append(f'<rect x="{bx}" y="{uy + 32}" width="{bw}" height="16" fill="none" stroke="{ORANGE}" stroke-opacity=".6"/>')
    s.append(f'<rect x="{bx + 3}" y="{uy + 35}" width="{bw * .62:.0f}" height="10" fill="{ORANGE}" filter="url(#neon)">'
             f'<animate attributeName="width" values="0;{bw * .62:.0f};{bw * .62:.0f};0" keyTimes="0;.7;.95;1" dur="6s" repeatCount="indefinite"/></rect>')
    s.append(f'<text x="{bx + bw + 14}" y="{uy + 45}" font-family="{MONO}" font-size="13" fill="{ORANGE}">SYNC{blink(.9)}</text>')

    s.append(f'<text x="48" y="{uy + 118}" font-family="{MONO}" font-size="13" fill="{MUTED}">'
             f'&gt; sys.diagnostico() concluído · 15 módulos ativos · 3 em sincronização</text>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- cards de projeto
def wrap(text, maxc):
    lines, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > maxc:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def project_card(num, title, jp, desc, tags, color):
    W, H = 400, 300
    s = [svg_open(W, H, f"Projeto {title}: {desc}"), "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="{PANEL}" stroke="{color}" stroke-opacity=".5"/>')
    s.append(corners(8, 8, W - 16, H - 16, color, 16, 2.5))
    s.append(f'<text x="26" y="40" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">ARQUIVO DE CASO #{num:02d}</text>')
    s.append(f'<text x="374" y="42" text-anchor="end" font-family="{JP}" font-size="16" fill="{color}" filter="url(#neon)">{esc(jp)}{flicker(5 + num, num * .7)}</text>')
    s.append(f'<text x="26" y="82" font-family="{TITLE_FONT}" font-size="25" fill="{TEXT}" stroke="{color}" stroke-width=".6" filter="url(#neon)">{esc(title)}</text>')
    s.append(f'<line x1="26" y1="98" x2="374" y2="98" stroke="{color}" stroke-opacity=".4"/>')
    for i, ln in enumerate(wrap(desc, 40)):
        s.append(f'<text x="26" y="{126 + i * 21}" font-family="{MONO}" font-size="14" fill="{TEXT}" fill-opacity=".85">{esc(ln)}</text>')
    tx = 26
    for t in tags:
        w = len(t) * 8 + 18
        s.append(f'<rect x="{tx}" y="222" width="{w}" height="22" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".6"/>'
                 f'<text x="{tx + w / 2}" y="237" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{color}">{esc(t)}</text>')
        tx += w + 8
    s.append(f'<text x="26" y="274" font-family="{MONO}" font-size="13" fill="{color}">&gt; ACESSAR ARQUIVO<tspan>_{blink(1)}</tspan></text>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- título de seção
def section(title, sub, color):
    W, H = 1200, 90
    s = [svg_open(W, H, title), "<defs>", defs_common(),
         f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>',
         "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<text x="48" y="54" font-family="{TITLE_FONT}" font-size="30" letter-spacing="4" fill="{TEXT}" stroke="{color}" stroke-width=".8" filter="url(#neon)">{esc(title)}</text>')
    s.append(f'<text x="1152" y="54" text-anchor="end" font-family="{MONO}" font-size="14" fill="{MUTED}">&gt; {esc(sub)}</text>')
    s.append(f'<rect x="48" y="70" width="1104" height="2" fill="url(#ln)"/>')
    s.append(f'<rect x="48" y="68" width="60" height="6" fill="{color}" filter="url(#neon)">'
             f'<animate attributeName="x" values="48;1092;48" dur="7s" repeatCount="indefinite"/></rect>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- rodapé
def footer():
    W, H = 1200, 320
    s = [svg_open(W, H, "Todos esses momentos se perderão no tempo, como lágrimas na chuva. Roy Batty"), "<defs>", defs_common(),
         rain_pattern("rainF", n=18, op=.4, speed=.45),
         f'<linearGradient id="fsky" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{H}"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#2A0A3A"/></linearGradient>',
         "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="url(#fsky)"/>')
    s.append(f'<polygon points="0,{H} 0,{H - 40} 420,{H - 60} 800,{H - 60} 1200,{H - 35} 1200,{H}" fill="#05020A"/>')
    s.append(f'<g fill="#05020A"><rect x="880" y="{H - 115}" width="14" height="60"/><rect x="872" y="{H - 120}" width="30" height="8"/></g>')
    s.append(f'<circle cx="887" cy="{H - 124}" r="3" fill="{MAGENTA}" filter="url(#neon)">{blink(1.5)}</circle>')
    s.append(f'<text x="600" y="118" text-anchor="middle" font-family="{MONO}" font-size="25" fill="{TEXT}" filter="url(#neon)">'
             f'"Todos esses momentos se perderão no tempo,</text>')
    s.append(f'<text x="600" y="158" text-anchor="middle" font-family="{MONO}" font-size="25" fill="{TEXT}" filter="url(#neon)">'
             f'como lágrimas na chuva."</text>')
    # "digitação": uma cortina da cor do céu que vai se abrindo da esquerda para a direita.
    # Sem animação, a cortina fica fora da tela e o texto aparece normalmente.
    for y0, t0, t1 in ((88, 0, .35), (128, .35, .65)):
        s.append(f'<rect x="1200" y="{y0}" width="1200" height="42" fill="url(#fsky)">'
                 f'<animate attributeName="x" values="0;0;1200;1200" keyTimes="0;{t0};{t1};1" dur="12s" repeatCount="indefinite"/></rect>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#rainF)"/>')
    s.append(f'<text x="600" y="202" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="5" fill="{MAGENTA}" filter="url(#neon)">— ROY BATTY</text>')
    s.append(f'<text x="600" y="{H - 14}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">'
             f'MAIS HUMANO QUE HUMANO  ·  GS4L1M  ·  2049</text>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


PROJECTS = [
    (1, "SAÚDE MENTAL", "健康",
     "Extração e análise de dados do DATASUS (SIH e SIM): internações por saúde mental e suicídios no Brasil e em MG, 2024–2025.",
     ["Python", "Pandas", "Streamlit"], MAGENTA),
    (2, "ANÁLISE ANP", "燃料",
     "Dashboard dos preços de combustíveis da ANP: gasolina, diesel e etanol por estado, município, bairro e bandeira.",
     ["Python", "Pandas", "Streamlit"], ORANGE),
    (3, "MÃOS À OBRA ML", "学習",
     "Estudos do livro de Machine Learning do Aurélien Géron: notebooks reescritos em Python, em módulos e em português.",
     ["Python", "Scikit-Learn"], CYAN),
]

if __name__ == "__main__":
    files = {
        "br-header.svg": header(),
        "br-id.svg": id_card(),
        "br-sec-skills.svg": section("MÓDULOS", "sys.diagnostico()", CYAN),
        "br-skills.svg": skills(),
        "br-sec-projects.svg": section("ARQUIVOS DE CASO", "ls ./projetos --destaque", MAGENTA),
        "br-sec-activity.svg": section("REGISTRO DE ATIVIDADE", "cat ./atividade.log", ORANGE),
        "br-sec-contact.svg": section("CANAL DE CONTATO", "ping gustavo", PURPLE),
        "br-footer.svg": footer(),
    }
    for p in PROJECTS:
        files[f"br-proj-{p[0]}.svg"] = project_card(*p)
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{name:22s} {len(svg.encode()) // 1024:4d} KB")
