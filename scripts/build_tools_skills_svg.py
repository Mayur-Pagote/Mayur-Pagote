with open('tools_skills_d.txt', 'r', encoding='utf-8') as f:
    d = f.read()

# Build dark and light SVG
# viewBox with padding
pad_x = 10
pad_y = 10
vb_w = 527 + 2 * pad_x
vb_h = 179 + 2 * pad_y

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

with open('assets/tools-skills-dark.svg', 'w', encoding='utf-8') as f:
    f.write(svg_dark)

with open('assets/tools-skills-light.svg', 'w', encoding='utf-8') as f:
    f.write(svg_light)

with open('assets/tools-skills.svg', 'w', encoding='utf-8') as f:
    f.write(svg_resp)

print('Successfully generated assets/tools-skills*.svg')
