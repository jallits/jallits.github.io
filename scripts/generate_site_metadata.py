#!/usr/bin/env python3
"""Refresh homepage JSON-LD after changes to copy or advisory offerings."""
from pathlib import Path
from html import unescape
import re
from search_metadata import structured_data

root = Path(__file__).resolve().parents[1]
page = root / 'index.html'
html = page.read_text()
title = unescape(re.search(r'<title>(.*?)</title>', html, re.S)[1])
description = unescape(re.search(r'<meta name="description" content="([^"]+)"', html)[1])
html, count = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda _: structured_data(title, description), html, flags=re.S)
if count != 1:
    raise ValueError('Expected exactly one homepage structured-data script')
page.write_text(html)
print('Generated homepage organization, website, page, person, and service metadata.')
