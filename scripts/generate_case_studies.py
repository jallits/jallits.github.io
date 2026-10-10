#!/usr/bin/env python3
"""Generate transparent illustrative engagement scenarios, not client claims."""
from html import escape
import json
from generate_project_pages import ROOT, shell, arrow

services = json.loads((ROOT / 'case-studies/scenarios.json').read_text())
css = '''
.scenarios-intro h1 { font-size: clamp(38px, 4vw, 58px); letter-spacing: -2px; margin-bottom: 24px; }
.scenarios-intro > p:not(.eyebrow) { color: var(--muted); font-size: 16px; line-height: 1.8; max-width: 820px; }
.scenario-notice { padding: 20px 24px; border-left: 2px solid var(--violet); background: var(--surface); margin-top: 24px; }
.scenario-notice strong { color: var(--ink); }
.scenario-navigation { display: flex; flex-wrap: wrap; gap: 12px; margin: 32px 0 42px; }
.scenario-navigation a { padding: 12px 14px; border: 1px solid var(--line); font-size: 11px; color: var(--muted); }
.scenario-navigation a:hover { border-color: var(--accent); color: var(--accent); }
.scenario-service { padding-top: 34px; margin-top: 34px; border-top: 1px solid var(--line); }
.scenario-service > h2 { font-size: 32px; letter-spacing: -1px; margin-bottom: 28px; }
.scenario-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }
.scenario-case { background: var(--surface); border: 1px solid var(--line); padding: 30px; }
.scenario-case .eyebrow { color: var(--violet); font-size: 8px; margin-bottom: 20px; }
.scenario-case h3 { font-size: 25px; margin: 0 0 24px; }
.scenario-case h4 { font: 600 9px 'Courier New', monospace; letter-spacing: 1.3px; color: var(--accent); margin: 24px 0 12px; }
.scenario-case p:not(.eyebrow) { margin: 0; font-size: 14px; line-height: 1.8; color: var(--muted); }
.scenario-case .intended-outcome { border-top: 1px solid var(--line); margin-top: 24px; padding-top: 1px; }
.scenario-contact { margin-top: 48px; border-top: 1px solid var(--line); padding-top: 32px; }
.scenario-contact h2 { font-size: 32px; margin-bottom: 18px; }
.scenario-contact p { color: var(--muted); font-size: 15px; line-height: 1.8; margin-bottom: 24px; }
@media (max-width: 768px) { .scenario-grid { grid-template-columns: minmax(0, 1fr); } .scenario-case { padding: 26px; } .scenario-service > h2 { font-size: 28px; } }
'''
sections = []
for service in services:
    cards = []
    for number, case in enumerate(service['cases'], 1):
        cards.append(f'''<article class="scenario-case"><p class="eyebrow">ILLUSTRATIVE SCENARIO / 0{number}</p><h3>{escape(case['title'])}</h3>
<h4>THE CHALLENGE</h4><p>{escape(case['scenario'])}</p>
<h4>PROPOSED APPROACH</h4><p>{escape(case['approach'])}</p>
<h4>WHERE AI FITS</h4><p>{escape(case['ai'])}</p>
<div class="intended-outcome"><h4>INTENDED DELIVERABLE</h4><p>{escape(case['outcome'])}</p></div>
<h4>WHAT TO MEASURE</h4><p>{escape(case['evidence'])}</p></article>''')
    sections.append(f'''<section class="scenario-service" id="{service['slug']}" aria-labelledby="{service['slug']}-title"><h2 id="{service['slug']}-title">{escape(service['service'])}</h2><div class="scenario-grid">{''.join(cards)}</div></section>''')
nav = ''.join(f'<a href="#{service["slug"]}">{escape(service["service"])}</a>' for service in services)
body = f'''<nav class="project-breadcrumb" aria-label="Breadcrumb"><a href="../">JALLITS</a><span aria-hidden="true">/</span><span>Engagement scenarios</span></nav>
<div class="scenarios-intro"><p class="eyebrow">TEN SCENARIOS / FIVE SERVICES</p><h1>Challenges.<br>Paths forward.</h1><p>See how an engagement could connect a difficult engineering challenge with a practical approach, a useful deliverable, and evidence of progress.</p><p class="scenario-notice"><strong>Illustrative examples, not client case histories.</strong> These scenarios do not describe completed JALLITS engagements or verified client results. Deliverables and measures are proposed, not claimed outcomes.</p></div>
<nav class="scenario-navigation" aria-label="Browse scenarios by service">{nav}</nav>{''.join(sections)}
<section class="scenario-contact"><h2>Recognize the challenge?</h2><p>Let’s talk about your context and what a useful outcome would look like.</p><a class="button" href="../#connect">Discuss your challenges {arrow}</a></section>'''
(ROOT / 'case-studies/index.html').write_text(shell('Illustrative engagement scenarios', 'Two illustrative engagement scenarios for each JALLITS service, with proposed approaches, selective AI use, and measures of progress. These are not client case histories.', 'case-studies/', body, '../', css))
print('Generated ten illustrative scenarios across five services.')
