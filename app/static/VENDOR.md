# Local browser libraries

Versions checked against the official npm registry and TermsFeed documentation on 2026-09-18.
All UI JavaScript, CSS and icon fonts are served from `app/static`; no runtime CDN is required.
Google Analytics and Matomo remain external, optional integrations enabled by configuration.

| Library | Version | Source |
| --- | --- | --- |
| bootstrap | 5.3.8 | [Upstream distribution](https://registry.npmjs.org/bootstrap/-/bootstrap-5.3.8.tgz) |
| @popperjs/core | 2.11.8 | [Upstream distribution](https://registry.npmjs.org/@popperjs/core/-/core-2.11.8.tgz) |
| jquery | 4.0.0 | [Upstream distribution](https://registry.npmjs.org/jquery/-/jquery-4.0.0.tgz) |
| datatables.net | 3.0.4 | [Upstream distribution](https://registry.npmjs.org/datatables.net/-/datatables.net-3.0.4.tgz) |
| datatables.net-bs5 | 3.0.4 | [Upstream distribution](https://registry.npmjs.org/datatables.net-bs5/-/datatables.net-bs5-3.0.4.tgz) |
| datatables.net-responsive | 4.0.3 | [Upstream distribution](https://registry.npmjs.org/datatables.net-responsive/-/datatables.net-responsive-4.0.3.tgz) |
| datatables.net-responsive-bs5 | 4.0.3 | [Upstream distribution](https://registry.npmjs.org/datatables.net-responsive-bs5/-/datatables.net-responsive-bs5-4.0.3.tgz) |
| datatables.net-scroller | 3.0.0 | [Upstream distribution](https://registry.npmjs.org/datatables.net-scroller/-/datatables.net-scroller-3.0.0.tgz) |
| datatables.net-scroller-bs5 | 3.0.0 | [Upstream distribution](https://registry.npmjs.org/datatables.net-scroller-bs5/-/datatables.net-scroller-bs5-3.0.0.tgz) |
| @fortawesome/fontawesome-free | 7.3.1 | [Upstream distribution](https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-7.3.1.tgz) |
| select2 | 4.1.0 | [Upstream distribution](https://registry.npmjs.org/select2/-/select2-4.1.0.tgz) |
| select2-bootstrap-5-theme | 1.3.0 | [Upstream distribution](https://registry.npmjs.org/select2-bootstrap-5-theme/-/select2-bootstrap-5-theme-1.3.0.tgz) |
| bootstrap5-toggle | 5.4.1 | [Upstream distribution](https://registry.npmjs.org/bootstrap5-toggle/-/bootstrap5-toggle-5.4.1.tgz) |
| bootstrap-show-password | 1.3.0 | [Upstream distribution](https://registry.npmjs.org/bootstrap-show-password/-/bootstrap-show-password-1.3.0.tgz) |
| prismjs | 1.30.0 | [Upstream distribution](https://registry.npmjs.org/prismjs/-/prismjs-1.30.0.tgz) |
| dotdotdot-js | 4.2.0 | [Upstream distribution](https://registry.npmjs.org/dotdotdot-js/-/dotdotdot-js-4.2.0.tgz) |
| cookieconsent | 4.2.0 | [Upstream distribution](https://www.termsfeed.com/public/cookie-consent/4.2.0/cookie-consent-code.js) |

## Updating

`vendor-versions.json` records the exact upstream versions, npm tarball integrity hashes,
and source-to-destination file mappings. Download the packages and verify the tarball
integrity before copying the listed distribution files. No npm install or build is needed
when deploying the dashboard. Licenses are retained in `licenses/`.

The DataTables files are bundles: concatenate the core, Bootstrap 5 adapter, Responsive,
Responsive Bootstrap 5 adapter, Scroller, and Scroller Bootstrap 5 adapter in that order,
with a newline and semicolon between JavaScript files. CSS contains the three Bootstrap 5
stylesheets in core, Responsive, Scroller order. Preserve upstream license headers.

Update Font Awesome CSS and webfonts together. Keep source maps beside the files that
reference them. Bootstrap 5.3.8, Popper 2.11.8, bootstrap-show-password 1.3.0 and the Select2
Bootstrap 5 theme 1.3.0 were already current and have been retained.

Cookie Consent uses the full `cookie-consent-code.js` distribution, not `cookie-consent.js`:
the latter is a loader that fetches code and a ping script from TermsFeed. Its unavailable
source-map reference is removed. Version 4.2 uses `termsfeed-com---` CSS classes and
`data-cookie-consent` script attributes; keep those in sync in `base.html`.

## Browser verification

Check DataTables sorting/search/paging, Responsive at mobile widths and Scroller;
Select2 selection/search; password visibility; checkbox toggles; topology truncation;
YAML highlighting; icon fonts; and HTML fragments loaded with jQuery. Exercise dropdowns
and modals as well as cookie acceptance/rejection and persistence. Block external requests
with analytics disabled to check that all UI dependencies are local.
