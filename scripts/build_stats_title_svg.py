import matplotlib.font_manager as fm
from matplotlib.textpath import TextPath
from matplotlib.path import Path

font_path = 'amsterdam_font_extracted/Amsterdam.ttf'
fp = fm.FontProperties(fname=font_path, size=72)
tp = TextPath((0, 0), 'Stats', prop=fp)
bbox = tp.get_extents()

w = bbox.x1 - bbox.x0
h = bbox.y1 - bbox.y0

def to_svg(path, bbox):
    codes = path.codes
    verts = path.vertices
    cmds = []
    i = 0
    while i < len(verts):
        code = codes[i]
        if code == Path.MOVETO:
            x = verts[i][0] - bbox.x0
            y = bbox.y1 - verts[i][1]
            cmds.append(f'M {x:.2f} {y:.2f}')
            i += 1
        elif code == Path.LINETO:
            x = verts[i][0] - bbox.x0
            y = bbox.y1 - verts[i][1]
            cmds.append(f'L {x:.2f} {y:.2f}')
            i += 1
        elif code == Path.CURVE3:
            x1 = verts[i][0] - bbox.x0
            y1 = bbox.y1 - verts[i][1]
            x2 = verts[i+1][0] - bbox.x0
            y2 = bbox.y1 - verts[i+1][1]
            cmds.append(f'Q {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f}')
            i += 2
        elif code == Path.CURVE4:
            x1 = verts[i][0] - bbox.x0
            y1 = bbox.y1 - verts[i][1]
            x2 = verts[i+1][0] - bbox.x0
            y2 = bbox.y1 - verts[i+1][1]
            x3 = verts[i+2][0] - bbox.x0
            y3 = bbox.y1 - verts[i+2][1]
            cmds.append(f'C {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} {x3:.2f} {y3:.2f}')
            i += 3
        elif code == Path.CLOSEPOLY:
            cmds.append('Z')
            i += 1
        else:
            i += 1
    return ' '.join(cmds)

d = to_svg(tp, bbox)

pad_x = 10
pad_y = 10
vb_w = round(w + 2 * pad_x)
vb_h = round(h + 2 * pad_y)

svg_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad_x} {-pad_y} {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" fill="none">
  <path d="{d}" fill="#ffffff" fill-rule="evenodd" />
</svg>'''

svg_light = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad_x} {-pad_y} {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" fill="none">
  <path d="{d}" fill="#1f2328" fill-rule="evenodd" />
</svg>'''

svg_resp = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad_x} {-pad_y} {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" fill="none">
<style>
/* <![CDATA[ */
  .title-text {{ fill: #1f2328; }}
  @media (prefers-color-scheme: dark) {{
    .title-text {{ fill: #ffffff; }}
  }}
/* ]]> */
</style>
  <path class="title-text" d="{d}" fill-rule="evenodd" />
</svg>'''

with open('assets/stats-title-dark.svg', 'w', encoding='utf-8') as f:
    f.write(svg_dark)

with open('assets/stats-title-light.svg', 'w', encoding='utf-8') as f:
    f.write(svg_light)

with open('assets/stats-title.svg', 'w', encoding='utf-8') as f:
    f.write(svg_resp)

print('Generated assets/stats-title*.svg successfully')
