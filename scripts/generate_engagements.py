#!/usr/bin/env python3
"""Generate engagement models and deliverable examples from reviewed content."""
from html import escape
import json
from generate_project_pages import ROOT, shell, arrow

services = json.loads((ROOT / 'engagements/services.json').read_text())
css = '''
.engagement-intro h1 { font-size: clamp(38px, 4vw, 58px); letter-spacing: -2px; margin-bottom: 24px; }
.engagement-intro > p:not(.eyebrow) { color: var(--muted); font-size: 16px; line-height: 1.8; max-width: 820px; }
.engagement-nav { display: flex; flex-wrap: wrap; gap: 12px; margin: 30px 0 42px; }
.engagement-nav a { padding: 12px 14px; border: 1px solid var(--line); font-size: 11px; color: var(--muted); }
.engagement-nav a:hover { border-color: var(--accent); color: var(--accent); }
.engagement-service { border-top: 1px solid var(--line); padding-top: 34px; margin-top: 34px; }
.engagement-service h2 { font-size: 32px; letter-spacing: -1px; margin-bottom: 16px; }
.engagement-model { color: var(--accent); font: 11px 'Courier New', monospace; margin: 0 0 28px; }
.engagement-columns { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 48px; }
.engagement-columns h3 { font-size: 20px; margin-top: 0; }
.engagement-columns p, .engagement-columns li, .engagement-steps p { color: var(--muted); font-size: 14px; line-height: 1.8; }
.engagement-columns ul { padding-left: 18px; margin: 0 0 28px; }
.engagement-columns li { margin-bottom: 10px; }
.engagement-columns .scope-note { font-size: 12px; padding: 16px 20px; border-left: 2px solid var(--violet); background: var(--surface); }
.engagement-section { border-top: 1px solid var(--line); padding-top: 38px; margin-top: 48px; }
.engagement-section h2 { font-size: 34px; margin-bottom: 24px; }
.engagement-section > p { color: var(--muted); font-size: 15px; line-height: 1.8; max-width: 850px; }
.engagement-steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; margin: 28px 0; }
.engagement-step { padding: 24px; border: 1px solid var(--line); background: var(--surface); }
.engagement-step h3 { font-size: 22px; }
.engagement-step p { margin-bottom: 0; }
.scope-list { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 40px; color: var(--muted); padding-left: 20px; font-size: 14px; line-height: 1.8; margin-bottom: 28px; }
@media (max-width: 768px) { .engagement-columns, .engagement-steps, .scope-list { grid-template-columns: minmax(0, 1fr); } .engagement-columns { gap: 18px; } .engagement-service h2, .engagement-section h2 { font-size: 28px; } }
'''
sections = []
for service in services:
    deliverables = ''.join(f'<li>{escape(item)}</li>' for item in service['deliverables'])
    sections.append(f'''<section class="engagement-service" id="{service['slug']}" aria-labelledby="{service['slug']}-title"><h2 id="{service['slug']}-title">{escape(service['name'])}</h2><p class="engagement-model">{escape(service['model'])}</p><div class="engagement-columns"><div><h3>When it fits</h3><p>{escape(service['fit'])}</p><h3>How we work</h3><p>{escape(service['work'])}</p><h3>What we need from you</h3><p>{escape(service['inputs'])}</p></div><div><h3>Typical deliverables</h3><ul>{deliverables}</ul><p class="scope-note">{escape(service['boundary'])}</p><a class="text-link" href="../case-studies/#{service['slug']}">Explore illustrative scenarios {arrow}</a></div></div></section>''')
nav = ''.join(f'<a href="#{service["slug"]}">{escape(service["name"])}</a>' for service in services)
body = f'''<nav class="project-breadcrumb" aria-label="Breadcrumb"><a href="../">JALLITS</a><span aria-hidden="true">/</span><span>Engagements</span></nav><div class="engagement-intro"><p class="eyebrow">HOW WE WORK TOGETHER</p><h1>A clear scope.<br>A useful outcome.</h1><p>Start with the challenge. Agree on the outcome. Choose the level of support that fits your organization. These engagement models and typical deliverables provide a starting point; scope, cadence, duration, and commercial terms are agreed for each engagement.</p></div><nav class="engagement-nav" aria-label="Browse engagement models">{nav}<a href="#first-conversation">The first conversation</a></nav>{''.join(sections)}
<section id="first-conversation" class="engagement-section" aria-labelledby="conversation-title"><p class="eyebrow">THE FIRST CONVERSATION</p><h2 id="conversation-title">Bring the challenge.<br>We’ll explore the next step.</h2><p>A short outline of the situation, the people involved, and your desired outcome is enough to start. You don’t need to arrive with a chosen service or a finished solution.</p><div class="engagement-steps"><article class="engagement-step"><p class="eyebrow">01 / CONTEXT</p><h3>What’s getting in the way?</h3><p>Discuss the business context, engineering challenges, urgency, and constraints. Understand what you have tried and where progress is stuck.</p></article><article class="engagement-step"><p class="eyebrow">02 / OUTCOME</p><h3>What would better look like?</h3><p>Clarify the decisions, capabilities, or delivery improvements you need. Identify stakeholders and what evidence would demonstrate meaningful progress.</p></article><article class="engagement-step"><p class="eyebrow">03 / FIT</p><h3>What support makes sense?</h3><p>Explore whether an assessment, leadership support, a focused roadmap, or another approach fits. If there is a fit, identify what is needed to define a proposal.</p></article></div><p>The conversation is about fit and direction. Any engagement follows a separately agreed scope and commercial terms.</p><a class="button" href="https://www.linkedin.com/in/djallits">Connect with Dan on LinkedIn {arrow}</a></section>
<section class="engagement-section" aria-labelledby="scope-title"><p class="eyebrow">BEFORE THE WORK BEGINS</p><h2 id="scope-title">Make the agreement explicit.</h2><p>Define the work together so expectations, responsibilities, and review points are clear.</p><ul class="scope-list"><li>Objectives, success criteria, and a baseline where appropriate</li><li>Deliverables, boundaries, and implementation responsibilities</li><li>Stakeholders, decision rights, and escalation paths</li><li>Access, participation, and working cadence</li><li>Duration, availability, fees, and commercial terms</li><li>Progress reviews, change control, and handoff expectations</li></ul><a class="text-link" href="../#connect">Discuss your challenges {arrow}</a></section>'''
(ROOT / 'engagements/index.html').write_text(shell('Engineering Advisory Engagements & Deliverables', 'Explore JALLITS engineering advisory engagement models, typical deliverables, fractional leadership, and what to expect from the first conversation.', 'engagements/', body, '../', css))
print('Generated five engagement models and first-conversation guidance.')
