#!/usr/bin/env python3
"""Render committed project README snapshots using the homepage shell.

Run from any working directory. Requires Python 3 and Pandoc; deployed pages
are already generated and need neither at runtime or in GitHub Actions.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import json
import re
import subprocess
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
home = (ROOT / 'index.html').read_text()
styles = re.search(r'<style>(.*?)</style>', home, re.S)[1]
header = re.search(r'<header\b.*?</header>', home, re.S)[0]
footer = re.search(r'<footer\b.*?</footer>', home, re.S)[0]
theme_scripts = re.findall(r'<script>(.*?)</script>', home, re.S)
sources = json.loads((ROOT / 'projects/sources.json').read_text())
arrow = '<svg class="arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>'
project_css = '''
.project-page { padding-block: 50px 80px; }
.project-breadcrumb { display: flex; gap: 14px; color: var(--muted); font: 11px 'Courier New', monospace; margin-bottom: 28px; }
.project-tools { display: flex; flex-wrap: wrap; align-items: center; gap: 20px; border-block: 1px solid var(--line); padding: 20px 0; margin-bottom: 42px; }
.project-tools .button { padding: 13px 18px; }
.project-tools p { font: 11px 'Courier New', monospace; color: var(--muted); margin: 0; }
.readme-layout { display: grid; grid-template-columns: minmax(0, 1fr) 240px; gap: 70px; align-items: start; }
.readme { min-width: 0; line-height: 1.8; font-size: 15px; overflow-wrap: anywhere; }
.readme h1 { font-size: 48px; letter-spacing: -2px; margin: 0 0 22px; }
.readme h2 { font-size: 28px; letter-spacing: -.8px; margin: 46px 0 20px; padding-top: 22px; border-top: 1px solid var(--line); }
.readme h3 { font-size: 22px; margin: 32px 0 16px; }
.readme h4 { font-size: 18px; margin: 24px 0 12px; }
.readme p, .readme ul, .readme ol { color: var(--muted); margin-block: 16px; }
.readme strong { color: var(--ink); }
.readme li { margin-block: 8px; }
.readme a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; }
.readme blockquote { margin: 24px 0; padding: 8px 24px; border-left: 2px solid var(--violet); background: var(--surface); }
.readme pre { overflow-x: auto; padding: 24px; background: var(--surface); border: 1px solid var(--line); font-size: 12px; line-height: 1.6; overflow-wrap: normal; }
.readme code { font-family: 'Courier New', monospace; font-size: .9em; color: var(--ink); background: var(--surface-raised); padding: 2px 4px; }
.readme pre code { background: none; padding: 0; font-size: inherit; }
.readme table { display: block; width: 100%; max-width: 100%; overflow-x: auto; border-collapse: collapse; font-size: 13px; }
.readme th, .readme td { text-align: left; border: 1px solid var(--line); padding: 12px 16px; min-width: 140px; }
.readme th { color: var(--ink); background: var(--surface-raised); }
.readme td { color: var(--muted); }
.readme img { max-width: 100%; height: auto; }
.readme-toc { position: sticky; top: 28px; max-height: calc(100vh - 56px); overflow-y: auto; border-left: 1px solid var(--line); padding-left: 22px; }
.readme-toc p { font: 10px 'Courier New', monospace; letter-spacing: 1.5px; color: var(--accent); margin: 0 0 18px; }
.readme-toc ul { list-style: none; padding: 0; margin: 0; }
.readme-toc li { margin-bottom: 12px; }
.readme-toc a { color: var(--muted); font-size: 12px; line-height: 1.5; }
.readme-toc a:hover { color: var(--accent); }
.project-index h1 { font-size: 54px; letter-spacing: -2px; margin-bottom: 24px; }
.project-index > p { color: var(--muted); max-width: 650px; font-size: 15px; line-height: 1.8; margin-bottom: 32px; }
@media (max-width: 900px) { .readme-layout { grid-template-columns: minmax(0, 1fr) 190px; gap: 30px; } }
@media (max-width: 600px) { .project-page { padding-block: 32px 50px; } .readme-layout { grid-template-columns: minmax(0, 1fr); } .readme-toc { display: none; } .readme h1, .project-index h1 { font-size: 36px; letter-spacing: -1px; } .readme { font-size: 14px; } .readme h2 { font-size: 26px; } .readme pre { padding: 18px; font-size: 11px; } .project-tools { gap: 16px; margin-bottom: 30px; } }
'''

class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.current = [dict(attrs)['id'], '']
    def handle_data(self, data):
        if self.current is not None:
            self.current[1] += data
    def handle_endtag(self, tag):
        if tag == 'h2' and self.current is not None:
            self.items.append(self.current)
            self.current = None


def shell(title, description, canonical_path, body, base):
    def navigation(fragment):
        return re.sub(r'href="#([^\"]*)"', lambda m: 'href="' + base + ('#' + m[1] if m[1] else '') + '"', fragment)
    return f'''<!doctype html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#06090f">
  <script>{theme_scripts[0]}</script>
  <title>{escape(title)} — JALLITS</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <link rel="canonical" href="https://www.jallits.com/{canonical_path}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title, quote=True)} — JALLITS">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="https://www.jallits.com/{canonical_path}">
  <meta property="og:image" content="https://www.jallits.com/assets/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{base}assets/mark.svg" type="image/svg+xml">
  <style>{styles}\n{project_css}</style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  {navigation(header)}
  <main id="main" class="project-page wrap">{body}</main>
  {navigation(footer)}
  <script>{theme_scripts[-1]}</script>
</body>
</html>
'''

for slug, source in sources.items():
    directory = ROOT / 'projects' / slug
    fragment = subprocess.run(
        ['pandoc', '--from=gfm', '--to=html5', '--wrap=none', '--no-highlight', str(directory / 'README.md')],
        check=True, capture_output=True, text=True,
    ).stdout
    # Relative repository links belong to their source repository, not this site.
    def resolve(match):
        attribute, quote, url = match.groups()
        if url.startswith('#') or urlsplit(url).scheme or url.startswith('//'):
            return match[0]
        if attribute == 'src':
            base = source['repository'].replace('github.com', 'raw.githubusercontent.com') + '/' + source['commit'] + '/'
        else:
            base = source['repository'] + '/blob/' + source['commit'] + '/'
        return f'{attribute}={quote}{escape(urljoin(base, url), quote=True)}{quote}'
    fragment = re.sub(r'\b(href|src)=("|\')(.*?)\2', resolve, fragment)
    headings = Headings()
    headings.feed(fragment)
    toc = ''.join(f'<li><a href="#{escape(id, quote=True)}">{escape(text)}</a></li>' for id, text in headings.items)
    body = f'''<nav class="project-breadcrumb" aria-label="Breadcrumb"><a href="../../">JALLITS</a><span aria-hidden="true">/</span><a href="../">Projects</a><span aria-hidden="true">/</span><span>{escape(source['name'])}</span></nav>
<div class="project-tools"><a class="button" href="{source['repository']}">View on GitHub {arrow}</a><a class="text-link" href="{source['repository']}/blob/{source['commit']}/README.md">README source {arrow}</a><p>README SNAPSHOT / {source['commit'][:7]}</p></div>
<div class="readme-layout"><article class="readme" aria-label="{escape(source['name'])} README">{fragment}</article><nav class="readme-toc" aria-label="README contents"><p>ON THIS PAGE</p><ul>{toc}</ul></nav></div>'''
    (directory / 'index.html').write_text(shell(source['name'], f"Read the {source['name']} project README, including its planning status, architecture, roadmap, and contribution guidance.", f'projects/{slug}/', body, '../../'))

cards = ''.join(f'''<article class="project-card"><div class="tags"><span>LINUX</span><span>PLANNING &amp; DESIGN</span></div><h2>{escape(source['name'])}</h2><p>Read the project’s overview, proposed architecture, roadmap, and contribution guidance.</p><a class="project-link" href="{slug}/">Read the README {arrow}</a></article>''' for slug, source in sources.items())
body = f'''<div class="project-index"><nav class="project-breadcrumb" aria-label="Breadcrumb"><a href="../">JALLITS</a><span aria-hidden="true">/</span><span>Projects</span></nav><p class="eyebrow">BUILDING IN THE OPEN</p><h1>Open source projects.</h1><p>Explore our Linux projects through their own documentation. Both are currently in planning and design; these READMEs describe proposals, not released applications.</p><div class="project-grid">{cards}</div></div>'''
(ROOT / 'projects/index.html').write_text(shell('Open source projects', 'Read the Keyringd and Keyring Manager project documentation from JALLITS.', 'projects/', body, '../'))
print('Generated project directory and both README pages.')
