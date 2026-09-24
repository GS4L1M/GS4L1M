"""Gera os SVGs animados (chuva do Matrix) do README de perfil do GitHub."""
import random
from xml.sax.saxutils import escape

random.seed(1999)  # ano do filme :)

CHARS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:.=*+-<>¦"
GREEN = "#00FF41"
HEAD = "#D6FFE0"
BG = "#0D0208"


def rain(width, height, col_w=20, font=16, min_len=8, max_len=22, opacity=1.0):
    """Colunas de caracteres caindo, com a cabeça clara e o rastro sumindo."""
    parts = []
    for i, x in enumerate(range(col_w // 2, width, col_w)):
        n = random.randint(min_len, max_len)
        dur = random.uniform(4.0, 11.0)
        delay = -random.uniform(0, dur)  # negativo: já começa no meio da queda
        span = n * font
        tspans = []
        for k in range(n):
            ch = escape(random.choice(CHARS))
            y = k * font
            if k == n - 1:
                tspans.append(f'<tspan x="{x}" y="{y}" fill="{HEAD}">{ch}</tspan>')
            else:
                op = round(0.12 + 0.88 * (k / (n - 1)) ** 1.6, 2)
                tspans.append(f'<tspan x="{x}" y="{y}" fill-opacity="{op}">{ch}</tspan>')
        parts.append(
            f'<text class="c">{"".join(tspans)}'
            f'<animateTransform attributeName="transform" type="translate" from="0 {-span}" to="0 {height + font}" '
            f'dur="{dur:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/></text>'
        )
    return (
        f'<g opacity="{opacity}" font-size="{font}">' + "".join(parts) + "</g>"
    )


STYLE = f"""
<style>
  text {{ font-family: 'MS Gothic','Hiragino Kaku Gothic Pro','Noto Sans Mono CJK JP','Courier New',monospace; }}
  .c {{ fill: {GREEN}; }}
  .name {{ font-family: 'Courier New',Consolas,monospace; font-weight: bold; fill: {GREEN}; letter-spacing: 6px;
           animation: flicker 6s infinite; }}
  .sub {{ font-family: 'Courier New',Consolas,monospace; fill: {GREEN}; letter-spacing: 3px; }}
  @keyframes flicker {{
    0%, 91%, 93%, 96%, 100% {{ opacity: 1; transform: translateX(0); }}
    92% {{ opacity: .35; transform: translateX(-3px); }}
    95% {{ opacity: .6; transform: translateX(3px); }}
  }}
  .cursor {{ fill: {GREEN}; animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>"""

GLOW = """
<defs>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="vignette" cx="50%" cy="50%" r="70%">
    <stop offset="55%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity=".85"/>
  </radialGradient>
</defs>"""


def header():
    w, h = 1200, 320
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="GUSTAVO SALIM - Cientista de Dados e Desenvolvedor Python">
{GLOW}{STYLE}
<rect width="{w}" height="{h}" fill="{BG}"/>
{rain(w, h, opacity=0.9)}
<rect width="{w}" height="{h}" fill="url(#vignette)"/>
<rect x="250" y="95" width="700" height="140" rx="6" fill="{BG}" fill-opacity=".82" stroke="{GREEN}" stroke-opacity=".5"/>
<text class="name" x="600" y="170" font-size="60" text-anchor="middle" filter="url(#glow)">GUSTAVO SALIM</text>
<text class="sub" x="590" y="212" font-size="20" text-anchor="middle">&gt; Cientista de Dados &amp; Dev Python</text>
<rect class="cursor" x="878" y="197" width="11" height="19"/>
</svg>
"""


def divider():
    w, h = 1200, 60
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Chuva de código do Matrix">
{STYLE}
<rect width="{w}" height="{h}" rx="4" fill="{BG}"/>
{rain(w, h, col_w=16, font=12, min_len=4, max_len=9, opacity=0.8)}
</svg>
"""


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    for name, svg in (("matrix-header.svg", header()), ("matrix-divider.svg", divider())):
        with open(f"{out}/{name}", "w", encoding="utf-8") as f:
            f.write(svg)
        print(name, len(svg.encode()) // 1024, "KB")
