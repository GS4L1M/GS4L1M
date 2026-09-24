"""Gera os painéis SVG animados (tema DedSec / Watch Dogs 2) do README de perfil do GitHub.

Uso:  python assets/gera_svgs.py
Os arquivos são gravados na mesma pasta deste script. A foto (assets/foto.jpg)
é embutida dentro do painel do profiler.
"""
import base64
import os
import random
from xml.sax.saxutils import escape as esc

random.seed(2016)  # ano do Watch Dogs 2

OUT = os.path.dirname(os.path.abspath(__file__))

# Paleta
BG = "#0A0A0F"
PANEL = "#111118"
CYAN = "#00F0FF"
PINK = "#FF2E88"
YELLOW = "#F5E663"
WHITE = "#F2F2F2"
GREEN = "#39FF14"
MUTED = "#6E7191"

TITLE = "'Arial Black','Segoe UI Black',Impact,'Helvetica Neue',Arial,sans-serif"
MONO = "Consolas,'SFMono-Regular','Liberation Mono','Courier New',monospace"

# caveira pixelada (desenho próprio)
SKULL = [
    "...######...",
    "..########..",
    ".##########.",
    ".##..##..##.",
    ".#...##...#.",
    ".##########.",
    "..###..###..",
    "...######...",
    "...#.##.#...",
    "...######...",
]


# ---------------------------------------------------------------- blocos comuns
def svg_open(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">')


def defs_common():
    return f"""
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="b1"/>
    <feGaussianBlur in="SourceGraphic" stdDeviation="7" result="b2"/>
    <feMerge><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="1" fill="#000" fill-opacity=".35"/>
  </pattern>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
    <rect width="2" height="2" fill="{CYAN}" fill-opacity=".10"/>
  </pattern>"""


def blink(dur=1.0):
    return f'<animate attributeName="opacity" values="1;0;1" dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>'


def jitter(dx, dur, begin=0.0):
    """Tremidinha de glitch: fica parado quase o tempo todo e dá uns saltos."""
    vals = f"0 0;0 0;{dx} 0;{-dx} 1;0 0;0 0;{dx * 2} -1;0 0"
    return (f'<animateTransform attributeName="transform" type="translate" values="{vals}" '
            f'keyTimes="0;.8;.82;.84;.86;.93;.95;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" calcMode="discrete"/>')


def glitch_text(x, y, text, size, color=WHITE, anchor="start", font=TITLE, dur=4.0, spacing=2, glow=True):
    """Texto com as cópias ciano e rosa deslocadas (efeito RGB split)."""
    common = f'x="{x}" y="{y}" font-family="{font}" font-size="{size}" letter-spacing="{spacing}" text-anchor="{anchor}"'
    t = esc(text)
    return (f'<g><text {common} fill="{CYAN}" opacity=".85" transform="translate(-3 0)">{t}{jitter(-6, dur, .3)}</text>'
            f'<text {common} fill="{PINK}" opacity=".85" transform="translate(3 0)">{t}{jitter(6, dur)}</text>'
            f'<text {common} fill="{color}"{" filter=" + chr(34) + "url(#glow)" + chr(34) if glow else ""}>{t}{jitter(2, dur, .1)}</text></g>')


def skull(x, y, s, color=WHITE, eyes=PINK, eye_blink=True):
    out = [f'<g>']
    for r, row in enumerate(SKULL):
        for c, ch in enumerate(row):
            if ch == "#":
                out.append(f'<rect x="{x + c * s}" y="{y + r * s}" width="{s}" height="{s}" fill="{color}"/>')
    # olhos acesos
    for ex in (2, 7):
        anim = blink(2.4) if eye_blink else ""
        out.append(f'<rect x="{x + ex * s}" y="{y + 3 * s}" width="{s * 2 if ex == 7 else s * 2}" height="{s}" fill="{eyes}" filter="url(#glow)">{anim}</rect>')
    out.append("</g>")
    return "".join(out)


def sticker(x, y, text, bg, fg, rot, size=15, pad=10):
    w = len(text) * size * .68 + pad * 2
    h = size + pad * 1.4
    return (f'<g transform="rotate({rot} {x} {y})"><rect x="{x - w / 2:.0f}" y="{y - h / 2:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{bg}"/>'
            f'<text x="{x}" y="{y + size * .36:.0f}" text-anchor="middle" font-family="{TITLE}" font-size="{size}" fill="{fg}">{esc(text)}</text></g>')


def glitch_bars(w, h, n=6, dur=5.0):
    out = []
    for i in range(n):
        y = random.randint(0, h - 10)
        bh = random.randint(2, 9)
        bw = random.randint(80, 420)
        x = random.randint(0, w - bw)
        c = random.choice((CYAN, PINK, WHITE))
        t = random.uniform(.1, .85)
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{c}" opacity="0">'
                   f'<animate attributeName="opacity" values="0;0;.55;0;0" keyTimes="0;{t:.2f};{t + .01:.2f};{t + .03:.2f};1" '
                   f'dur="{dur + i * .7:.1f}s" repeatCount="indefinite"/></rect>')
    return "".join(out)


def corners(x, y, w, h, color, size=16, sw=3):
    p = []
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        p.append(f'<path d="M{cx} {cy + dy * size}V{cy}H{cx + dx * size}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
    return "".join(p)


# ---------------------------------------------------------------- cabeçalho
def header():
    W, H = 1200, 440
    s = [svg_open(W, H, "GUSTAVO SALIM - Cientista de Dados e Desenvolvedor Python - tema DedSec"), "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')

    # colunas de hex subindo no fundo
    for x in range(14, W, 46):
        lines = "".join(f'<tspan x="{x}" dy="16">{random.choice(["0x", "1", "0", "FF", "3A", "NaN", "null", "01"])}'
                        f'{random.randint(0, 255):02X}</tspan>' for _ in range(40))
        d = random.uniform(14, 30)
        s.append(f'<text font-family="{MONO}" font-size="11" fill="{CYAN}" fill-opacity="{random.uniform(.05, .16):.2f}">{lines}'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -320" dur="{d:.1f}s" repeatCount="indefinite"/></text>')

    # stickers estilo grafite
    s.append(sticker(150, 70, "#LIMPEOSNULOS", PINK, WHITE, -6))
    s.append(sticker(1050, 64, "404 NULOS", YELLOW, BG, 5))
    s.append(sticker(1080, 390, "HACKEIE OS DADOS", CYAN, BG, -4, size=13))
    s.append(sticker(420, 400, "ctOS = LIXO", WHITE, BG, 4, size=13))

    # caveira
    s.append(skull(912, 130, 13))

    # título
    s.append(glitch_text(96, 220, "GUSTAVO SALIM", 82, dur=4.5, spacing=3))
    s.append(f'<rect x="100" y="244" width="620" height="34" fill="{PINK}"/>')
    s.append(f'<text x="114" y="268" font-family="{TITLE}" font-size="19" letter-spacing="3" fill="{WHITE}">CIENTISTA DE DADOS // DEV PYTHON</text>')

    # terminal
    s.append(f'<g font-family="{MONO}" font-size="16">'
             f'<text x="100" y="318" fill="{MUTED}">&gt; ssh gustavo@ctos.sf --bypass</text>'
             f'<text x="100" y="342" fill="{GREEN}">[OK] firewall da Blume desativado</text>'
             f'<text x="100" y="366" fill="{CYAN}">[OK] ACESSO LIBERADO <tspan fill="{WHITE}">_{blink(.9)}</tspan></text></g>')

    s.append(glitch_bars(W, H))
    s.append(corners(14, 14, W - 28, H - 28, CYAN, 24, 3))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- profiler do ctOS
def profiler(photo_b64):
    W, H = 1200, 440
    s = [svg_open(W, H, "ctOS Profiler: Gustavo Salim, Cientista de Dados e Desenvolvedor Python"), "<defs>", defs_common(),
         '<clipPath id="ph"><rect x="60" y="70" width="300" height="340"/></clipPath>', "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="{PANEL}"/>')
    s.append(corners(20, 20, W - 40, H - 40, PINK, 20, 3))

    # foto com mira e scanner
    s.append(f'<g clip-path="url(#ph)"><image x="60" y="50" width="300" height="360" href="data:image/jpeg;base64,{photo_b64}" '
             f'xlink:href="data:image/jpeg;base64,{photo_b64}" preserveAspectRatio="xMidYMid slice"/>'
             f'<rect x="60" y="70" width="300" height="340" fill="url(#scan)"/>'
             f'<rect x="60" y="70" width="300" height="3" fill="{CYAN}" filter="url(#glow)">'
             f'<animate attributeName="y" values="70;407;70" dur="3.5s" repeatCount="indefinite"/></rect></g>')
    s.append(f'<rect x="60" y="70" width="300" height="340" fill="none" stroke="{CYAN}" stroke-opacity=".6"/>')
    s.append(corners(52, 62, 316, 356, CYAN, 22, 3))
    # mira no rosto
    s.append(f'<g stroke="{PINK}" stroke-width="2" fill="none"><rect x="150" y="100" width="120" height="130">'
             f'<animate attributeName="stroke-opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></rect>'
             f'<line x1="210" y1="92" x2="210" y2="104"/><line x1="210" y1="226" x2="210" y2="238"/></g>')
    s.append(f'<text x="60" y="56" font-family="{MONO}" font-size="12" fill="{CYAN}">ID: GS4L1M · MATCH 99.7%</text>')

    # cabeçalho do profiler
    s.append(f'<text x="400" y="80" font-family="{TITLE}" font-size="30" letter-spacing="2" fill="{WHITE}">ctOS PROFILER</text>')
    s.append(f'<rect x="720" y="58" width="150" height="28" fill="{PINK}"/>'
             f'<text x="795" y="78" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{WHITE}">ALVO HACKEADO</text>')
    s.append(f'<line x1="400" y1="98" x2="1150" y2="98" stroke="{CYAN}" stroke-opacity=".35"/>')

    fields = [
        ("NOME", "Gustavo Salim", WHITE),
        ("OCUPAÇÃO", "Cientista de Dados & Dev Python", CYAN),
        ("RENDA", "convertida integralmente em café", WHITE),
        ("HISTÓRICO", "achou uma tabela com 400 valores nulos e não chorou", WHITE),
        ("CRIME RECENTE", "treinou um modelo sem pedir permissão ao ctOS", WHITE),
        ("FRAQUEZA", "gráficos de pizza com 14 fatias", WHITE),
        ("AFILIAÇÃO", "DedSec · célula de dados", PINK),
    ]
    y = 132
    for k, v, c in fields:
        s.append(f'<text x="400" y="{y}" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{MUTED}">{esc(k)}</text>')
        s.append(f'<text x="560" y="{y}" font-family="{MONO}" font-size="17" fill="{c}">{esc(v)}</text>')
        y += 36

    # nível de ameaça
    s.append(f'<text x="400" y="{y + 12}" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{MUTED}">AMEAÇA</text>')
    for i in range(12):
        c = YELLOW if i < 6 else (PINK if i < 10 else "#2A2A35")
        s.append(f'<rect x="{560 + i * 24}" y="{y - 2}" width="18" height="18" fill="{c}"/>')
    s.append(f'<text x="860" y="{y + 12}" font-family="{MONO}" font-size="14" fill="{PINK}">ALTA · para planilhas mal feitas{blink(1.4)}</text>')
    s.append(glitch_bars(W, H, n=4, dur=6))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- arsenal (apps do celular)
APPS = [
    ("Py", "Python", CYAN), ("Pd", "Pandas", PINK), ("Np", "NumPy", YELLOW), ("Sk", "Scikit-Learn", CYAN),
    ("Mt", "Matplotlib", PINK), ("St", "Streamlit", YELLOW), ("Jp", "Jupyter", CYAN), ("BI", "Power BI", PINK),
    ("SQL", "SQL", YELLOW), ("H5", "HTML5", CYAN), ("CSS", "CSS", PINK), ("JS", "JavaScript", YELLOW),
    ("Git", "Git", CYAN), ("GH", "GitHub", PINK), ("VS", "VS Code", YELLOW),
]


def arsenal():
    W, H = 1200, 460
    s = [svg_open(W, H, "Arsenal: " + ", ".join(a[1] for a in APPS) + ". Baixando: TensorFlow e Keras."),
         "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')

    # "celular" do lado esquerdo
    s.append(f'<rect x="60" y="30" width="250" height="400" rx="28" fill="{PANEL}" stroke="{WHITE}" stroke-opacity=".5" stroke-width="3"/>')
    s.append(f'<rect x="150" y="44" width="70" height="8" rx="4" fill="{WHITE}" fill-opacity=".3"/>')
    s.append(skull(128, 110, 10, eye_blink=True))
    s.append(f'<text x="185" y="250" text-anchor="middle" font-family="{TITLE}" font-size="22" fill="{WHITE}">DedSec OS</text>')
    s.append(f'<text x="185" y="276" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{CYAN}">v2.0 · 15 apps</text>')
    s.append(f'<text x="185" y="370" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">bateria: 3%</text>')
    s.append(f'<text x="185" y="390" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">café: 0%</text>')

    # grade de apps
    s.append(f'<text x="360" y="58" font-family="{TITLE}" font-size="22" letter-spacing="2" fill="{WHITE}">APPS INSTALADOS</text>')
    gx, gy, cw, ch = 360, 80, 162, 88
    for i, (ic, name, col) in enumerate(APPS):
        cx = gx + (i % 5) * cw
        cy = gy + (i // 5) * ch
        s.append(f'<rect x="{cx}" y="{cy}" width="52" height="52" rx="12" fill="{col}"/>')
        s.append(f'<text x="{cx + 26}" y="{cy + 33}" text-anchor="middle" font-family="{TITLE}" font-size="{18 if len(ic) < 3 else 14}" fill="{BG}">{esc(ic)}</text>')
        s.append(f'<text x="{cx + 62}" y="{cy + 31}" font-family="{MONO}" font-size="13" fill="{WHITE}">{esc(name)}</text>')

    # download em andamento
    by = 360
    s.append(f'<rect x="360" y="{by}" width="790" height="70" fill="{PANEL}" stroke="{YELLOW}" stroke-opacity=".6"/>')
    s.append(f'<text x="380" y="{by + 28}" font-family="{MONO}" font-size="13" letter-spacing="2" fill="{YELLOW}">BAIXANDO NOVOS APPS</text>')
    s.append(f'<text x="380" y="{by + 54}" font-family="{MONO}" font-size="16" fill="{WHITE}">TensorFlow · Keras · Redes Neurais</text>')
    s.append(f'<rect x="760" y="{by + 26}" width="300" height="18" fill="none" stroke="{YELLOW}"/>')
    s.append(f'<rect x="763" y="{by + 29}" width="186" height="12" fill="{YELLOW}">'
             f'<animate attributeName="width" values="0;186;186;0" keyTimes="0;.7;.95;1" dur="5s" repeatCount="indefinite"/></rect>')
    s.append(f'<text x="1072" y="{by + 41}" font-family="{MONO}" font-size="14" fill="{YELLOW}">62%</text>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- operações (projetos)
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


def operation(num, title, desc, tags, color, status, status_color):
    W, H = 400, 320
    s = [svg_open(W, H, f"Operação {title}: {desc}"), "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="{PANEL}"/>')
    s.append(f'<rect x="8" y="8" width="{W - 16}" height="6" fill="{color}"/>')
    s.append(corners(8, 8, W - 16, H - 16, color, 14, 3))
    s.append(f'<text x="26" y="44" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{MUTED}">OPERAÇÃO #{num:02d}</text>')
    s.append(sticker(318, 38, status, status_color, BG, 3, size=11, pad=7))
    s.append(glitch_text(26, 88, title, 25, dur=5 + num, spacing=1))
    for i, ln in enumerate(wrap(desc, 40)):
        s.append(f'<text x="26" y="{124 + i * 21}" font-family="{MONO}" font-size="14" fill="{WHITE}" fill-opacity=".88">{esc(ln)}</text>')
    tx = 26
    for t in tags:
        w = len(t) * 8 + 18
        s.append(f'<rect x="{tx}" y="238" width="{w}" height="22" fill="{color}" fill-opacity=".14" stroke="{color}"/>'
                 f'<text x="{tx + w / 2}" y="253" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{color}">{esc(t)}</text>')
        tx += w + 8
    s.append(f'<text x="26" y="292" font-family="{MONO}" font-size="13" fill="{color}">&gt; invadir repositório<tspan>_{blink(1)}</tspan></text>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- transmissões (frases)
QUOTES = [
    ("Qualquer tecnologia suficientemente avançada é indistinguível de mágica.", "ARTHUR C. CLARKE", CYAN),
    ("Se você acha que entende a mecânica quântica, você não entende a mecânica quântica.", "RICHARD FEYNMAN", PINK),
    ("O que observamos não é a natureza em si, mas a natureza exposta ao nosso método de questionamento.", "WERNER HEISENBERG", YELLOW),
    ("Só podemos ver um pouco do futuro, mas o suficiente para perceber que há muito a fazer.", "ALAN TURING", CYAN),
    ("O futuro já chegou. Só não está uniformemente distribuído.", "WILLIAM GIBSON", PINK),
    ("Nem tudo que pode ser contado conta, e nem tudo que conta pode ser contado.", "WILLIAM B. CAMERON", YELLOW),
]


def transmissions():
    W = 1200
    cw, ch, gap = 552, 150, 24
    rows = (len(QUOTES) + 1) // 2
    H = 40 + rows * (ch + gap)
    s = [svg_open(W, H, "Transmissões interceptadas: " + " / ".join(f"{q} ({a})" for q, a, _ in QUOTES)),
         "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    for i, (q, a, col) in enumerate(QUOTES):
        x = 36 + (i % 2) * (cw + gap + 12)
        y = 20 + (i // 2) * (ch + gap)
        s.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{PANEL}"/>')
        s.append(f'<rect x="{x}" y="{y}" width="5" height="{ch}" fill="{col}"/>')
        s.append(f'<text x="{x + 24}" y="{y + 28}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{MUTED}">'
                 f'TRANSMISSÃO #{i + 1:02d} · SINAL <tspan fill="{col}">■■■■□</tspan></text>')
        for j, ln in enumerate(wrap(f"“{q}”", 52)):
            s.append(f'<text x="{x + 24}" y="{y + 60 + j * 23}" font-family="{MONO}" font-size="17" fill="{WHITE}">{esc(ln)}</text>')
        s.append(f'<text x="{x + cw - 20}" y="{y + ch - 16}" text-anchor="end" font-family="{TITLE}" font-size="13" letter-spacing="2" fill="{col}">— {esc(a)}</text>')
    s.append(glitch_bars(W, H, n=4, dur=7))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- título de seção
def section(title, sub, color):
    W, H = 1200, 96
    s = [svg_open(W, H, title), "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(skull(40, 26, 4, eyes=color))
    s.append(glitch_text(106, 62, title, 32, dur=6, spacing=2))
    s.append(f'<text x="1160" y="60" text-anchor="end" font-family="{MONO}" font-size="14" fill="{MUTED}">&gt; {esc(sub)}</text>')
    s.append(f'<rect x="40" y="80" width="1120" height="3" fill="{color}"/>')
    s.append(f'<rect x="40" y="78" width="70" height="7" fill="{WHITE}"><animate attributeName="x" values="40;1090;40" dur="6s" repeatCount="indefinite"/></rect>')
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- rodapé
def footer():
    W, H = 1200, 300
    s = [svg_open(W, H, "Deus não joga dados com o universo. Mas alguém precisa limpar os dados dele. Nós somos DedSec."),
         "<defs>", defs_common(), "</defs>"]
    s.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
    s.append(skull(546, 26, 9))
    s.append(f'<text x="600" y="150" text-anchor="middle" font-family="{MONO}" font-size="21" fill="{WHITE}">'
             f'“Deus não joga dados com o universo.” <tspan fill="{MUTED}" font-size="14">— Einstein</tspan></text>')
    s.append(f'<text x="600" y="184" text-anchor="middle" font-family="{MONO}" font-size="21" fill="{PINK}" filter="url(#glow)">'
             f'Mas alguém precisa limpar os dados dele.</text>')
    s.append(glitch_text(600, 250, "NÓS SOMOS DEDSEC", 40, anchor="middle", dur=5, spacing=4))
    s.append(f'<text x="600" y="284" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">'
             f'CONEXÃO ENCERRADA · LIMPE SEUS NULOS · GS4L1M<tspan fill="{CYAN}">_{blink(1)}</tspan></text>')
    s.append(glitch_bars(W, H, n=5, dur=5))
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append("</svg>")
    return "".join(s)


OPERATIONS = [
    (1, "SAÚDE MENTAL",
     "Extração e análise de dados do DATASUS (SIH e SIM): internações por saúde mental e suicídios no Brasil e em MG, 2024–2025.",
     ["Python", "Pandas", "Streamlit"], PINK, "CONCLUÍDA", GREEN),
    (2, "ANÁLISE ANP",
     "Dashboard dos preços de combustíveis da ANP: gasolina, diesel e etanol por estado, município, bairro e bandeira.",
     ["Python", "Pandas", "Streamlit"], YELLOW, "CONCLUÍDA", GREEN),
    (3, "MÃOS À OBRA ML",
     "Estudos do livro de Machine Learning do Aurélien Géron: notebooks reescritos em Python, em módulos e em português.",
     ["Python", "Scikit-Learn"], CYAN, "EM ANDAMENTO", YELLOW),
]

if __name__ == "__main__":
    with open(os.path.join(OUT, "foto.jpg"), "rb") as f:
        photo = base64.b64encode(f.read()).decode()
    files = {
        "ds-header.svg": header(),
        "ds-profiler.svg": profiler(photo),
        "ds-sec-arsenal.svg": section("ARSENAL", "ls ~/apps", CYAN),
        "ds-arsenal.svg": arsenal(),
        "ds-sec-ops.svg": section("OPERAÇÕES", "ls ./projetos --destaque", PINK),
        "ds-sec-quotes.svg": section("TRANSMISSÕES INTERCEPTADAS", "tail -f /dev/universo", YELLOW),
        "ds-quotes.svg": transmissions(),
        "ds-sec-activity.svg": section("ATIVIDADE", "cat ./invasoes.log", CYAN),
        "ds-sec-contact.svg": section("CONTATO", "ping gustavo", PINK),
        "ds-footer.svg": footer(),
    }
    for o in OPERATIONS:
        files[f"ds-op-{o[0]}.svg"] = operation(*o)
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"{name:22s} {len(svg.encode()) // 1024:4d} KB")
