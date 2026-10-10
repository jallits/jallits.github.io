# Jallits website

A responsive engineering advisory website for Jallits, hosted on GitHub
Pages at **https://www.jallits.com**. It markets Engineering Effectiveness
Assessments, Fractional Engineering Leadership, Platform Modernization,
DevSecOps Transformation, and Technology Strategy Advisory. LinkedIn provides
the contact path; open source work is supporting content.

The new identity pairs a geometric J symbol with the uppercase JALLITS wordmark
and an engineering and technology advisory descriptor. Reusable logo and
social sharing assets live in `assets/`. The header and footer embed the SVG
wordmark directly so HTML previews do not need a separate logo request.

## Develop locally

From the existing repository checkout (no separate worktree is needed):

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open port 8000 in a local browser. No package installation or build is required.
Edit `index.html`, including its inline stylesheet. Styles are embedded so
HTML file previews do not depend on resolving a separate CSS request.
The site uses system fonts and locally vendored Three.js 0.180.0 for its
decorative WebGL scene. There are no third-party runtime requests, analytics,
or backend services. See `assets/vendor/README.md` for provenance and licensing.

The theme toggle stores your light/dark preference locally; dark is the default.
The inline geometric fallback remains visible when scripts, WebGL, or external
assets are unavailable. Reduced motion renders a still scene; animation pauses
when the hero is offscreen or the browser tab is hidden.

Edit `assets/scene.js` for the Three.js scene. Run the local HTTP server to test
JavaScript modules; opening the HTML as a file still shows the styled fallback.

## Publish

1. In the repository's **Settings → Pages**, select **GitHub Actions** as the
   build and deployment source.
2. Push to `master` (the current default branch) or `main`, or manually run the
   **Deploy website to GitHub Pages** workflow.
3. Set the Pages custom domain to `www.jallits.com`. The checked-in `CNAME`
   records the same domain.
4. At the DNS provider, add a CNAME record for `www` pointing to
   `jallits.github.io` (no scheme or path).
5. When GitHub verifies the DNS and provisions a certificate, enable
   **Enforce HTTPS**. Verify domain ownership using GitHub's recommended TXT
   record before directing DNS to Pages.

GitHub Pages also supports serving these static files directly from the root
of the default branch if branch deployment is preferred. No Jekyll processing
is needed; `.nojekyll` is included.

## Content and identity

- Company: https://www.linkedin.com/company/jallits
- Open source: https://github.com/jallits
- Keyringd: https://github.com/jallits/keyringd
- Keyring Manager: https://github.com/jallits/keyring-manager
- About Dan Jallits: https://dan.jallits.com/
- Personal LinkedIn: https://www.linkedin.com/in/djallits
- Personal X: https://x.com/danjallits
- Personal code: https://github.com/djallits

AI guidance covers all five services, including responsible adoption under
fractional engineering leadership.
It emphasizes measured value, simpler alternatives, and human accountability.

Keep project descriptions aligned with their repository documentation. The
site does not claim production readiness, license terms, or support guarantees.

## Commits

Use Conventional Commits, with a short imperative subject, such as
`feat(site): add project overview`. Keep the subject under 50 characters when
practical, omit the trailing period, and separate an explanatory body with a
blank line. Wrap body text at 72 characters and explain what changed and why.
