"""Factual JSON-LD shared by generated pages; no ratings or client claims."""
import json
from pathlib import Path

SITE = 'https://www.jallits.com/'
ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    'projects': 'Open source projects',
    'keyringd': 'Keyringd',
    'keyring-manager': 'Keyring Manager',
    'case-studies': 'Illustrative engagement scenarios',
    'engagements': 'Engagements',
}


def structured_data(title, description, path=''):
    url = SITE + path
    organization = {
        '@type': 'Organization', '@id': SITE + '#organization',
        'name': 'JALLITS', 'url': SITE, 'logo': SITE + 'assets/logo.svg',
        'sameAs': ['https://www.linkedin.com/company/jallits', 'https://github.com/jallits'],
    }
    graph = [organization, {
        '@type': 'WebSite', '@id': SITE + '#website', 'name': 'JALLITS',
        'url': SITE, 'inLanguage': 'en', 'publisher': {'@id': SITE + '#organization'},
    }, {
        '@type': 'WebPage', '@id': url + '#webpage', 'url': url,
        'name': title, 'description': description, 'inLanguage': 'en',
        'isPartOf': {'@id': SITE + '#website'},
        'publisher': {'@id': SITE + '#organization'},
    }]
    if path:
        items = [{'@type': 'ListItem', 'position': 1, 'name': 'JALLITS', 'item': SITE}]
        route = ''
        for position, part in enumerate(path.strip('/').split('/'), 2):
            route += part + '/'
            items.append({'@type': 'ListItem', 'position': position, 'name': NAMES.get(part, part), 'item': SITE + route})
        graph.append({'@type': 'BreadcrumbList', '@id': url + '#breadcrumbs', 'itemListElement': items})
        graph[2]['breadcrumb'] = {'@id': url + '#breadcrumbs'}
    else:
        graph.append({
            '@type': 'Person', '@id': 'https://dan.jallits.com/#person',
            'name': 'Dan Jallits', 'url': 'https://dan.jallits.com/',
            'sameAs': ['https://www.linkedin.com/in/djallits', 'https://github.com/djallits', 'https://x.com/danjallits'],
        })
        services = json.loads((ROOT / 'engagements/services.json').read_text())
        organization['hasOfferCatalog'] = {
            '@type': 'OfferCatalog', 'name': 'Engineering and technology advisory services',
            'itemListElement': [{
                '@type': 'Offer', 'itemOffered': {
                    '@type': 'Service', 'name': service['name'],
                    'url': SITE + 'engagements/#' + service['slug'],
                    'provider': {'@id': SITE + '#organization'},
                },
            } for service in services],
        }
    value = json.dumps({'@context': 'https://schema.org', '@graph': graph}, indent=2)
    # Keep generated JSON inside its script element even if future copy has HTML.
    return '<script type="application/ld+json">\n' + value.replace('<', '\\u003c') + '\n</script>'
