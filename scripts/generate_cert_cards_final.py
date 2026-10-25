def create_cert_svg(filename, issuer, title, code, icon_content):
    svg = f'''<svg width="490" height="76" viewBox="0 0 490 76" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
  <title id="t">{code} — {title}</title>
  <desc id="d">{issuer}: {title} ({code})</desc>
  <style>
  /* <![CDATA[ */
    .card {{ fill: #f6f8fa; stroke: #d0d7de; }}
    .issuer {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: 1.4px; fill: #656d76; }}
    .title {{ font: 600 15px ui-monospace, SFMono-Regular, Menlo, monospace; fill: #1f2328; }}
    .badge-bg {{ fill: #eaeef2; stroke: #d0d7de; }}
    .badge-text {{ font: 700 11px ui-monospace, SFMono-Regular, Menlo, monospace; fill: #0969da; text-anchor: middle; }}

    @media (prefers-color-scheme: dark) {{
      .card {{ fill: #161b22; stroke: #30363d; }}
      .issuer {{ fill: #8b949e; }}
      .title {{ fill: #f0f6fc; }}
      .badge-bg {{ fill: #21262d; stroke: #30363d; }}
      .badge-text {{ fill: #58a6ff; }}
    }}
  /* ]]> */
  </style>

  <rect class="card" x=".5" y=".5" width="489" height="75" rx="10"/>

  <!-- Brand Icon -->
  <g transform="translate(18, 22)">
    {icon_content}
  </g>

  <!-- Issuer & Title -->
  <text class="issuer" x="64" y="27">{issuer.upper()}</text>
  <text class="title" x="64" y="50">{title}</text>

  <!-- Exam / Level Badge Pill -->
  <rect class="badge-bg" x="394" y="25" width="78" height="26" rx="6"/>
  <text class="badge-text" x="433" y="42">{code}</text>
</svg>'''
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg)

# Azure Icon (32x32)
azure_icon = '''<svg width="32" height="32" viewBox="0 0 24 24" fill="#0078D4">
  <path d="M5.483 21.3H24L14.025 4.013l-3.038 8.347 5.836 6.938L5.483 21.3zM13.23 2.7L6.105 8.677 0 19.253h5.505v.014L13.23 2.7z"/>
</svg>'''

# Azure AI Icon (Azure + AI Sparkle 32x32)
azure_ai_icon = '''<svg width="32" height="32" viewBox="0 0 24 24">
  <path fill="#0078D4" d="M5.483 21.3H24L14.025 4.013l-3.038 8.347 5.836 6.938L5.483 21.3zM13.23 2.7L6.105 8.677 0 19.253h5.505v.014L13.23 2.7z"/>
  <circle cx="18" cy="6" r="4.5" fill="#50e6ff"/>
  <path d="M18 3.2L18.7 5.3L20.8 6L18.7 6.7L18 8.8L17.3 6.7L15.2 6L17.3 5.3Z" fill="#ffffff"/>
</svg>'''

# Google Logo 4-color (32x32)
google_icon = '''<svg width="32" height="32" viewBox="0 0 24 24">
  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.15z"/>
  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.35 24 12 24z"/>
  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.35 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
</svg>'''

# Linux Foundation Icon (32x32)
lf_icon = '''<svg width="32" height="32" viewBox="0 0 24 24">
  <path fill="#003B5C" d="M4.8 19.2h9.6V24H0V9.6h4.8v9.6z"/>
  <path fill="#00843D" d="M0 0v7.2h4.8V4.822h14.4V19.2h-2.4V24H24V0H0z"/>
</svg>'''

create_cert_svg('assets/cert-az900.svg', 'Microsoft Certified', 'Azure Fundamentals', 'AZ-900', azure_icon)
create_cert_svg('assets/cert-ai900.svg', 'Microsoft Certified', 'Azure AI Fundamentals', 'AI-900', azure_ai_icon)
create_cert_svg('assets/cert-google-educator.svg', 'Google for Education', 'Certified Educator', 'LEVEL 1', google_icon)
create_cert_svg('assets/cert-lfc191.svg', 'The Linux Foundation', 'Open Source Licensing', 'LFC191', lf_icon)

print('Generated all 4 certification cards!')
