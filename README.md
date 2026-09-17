# Academic paper website base

This `gh-pages` branch hosts [Self-Foveate](https://www.mubuky.com/Self-Foveate/) and serves as a reusable, static academic project-page base. It uses ordinary HTML, CSS, and a small progressive-enhancement script; no build system or JavaScript framework is required.

## Reuse for another paper

1. Copy `index.html`, `static/css/`, and `static/js/` into the new site's publishing branch. Keep the original repository's paper-specific `main` branch separate.
2. Replace the metadata in `<head>`, publication title, authors, affiliations, resource links, and BibTeX. Keep the full paper title in the single `h1`. The optional `.publication-name` and `.publication-subtitle` spans provide a compact mobile hierarchy.
3. Replace TL;DR, abstract, section text, figures, and table values. Do not leave Self-Foveate text, alt descriptions, example results, or URLs in the new project.
4. Place original figures in `static/images/`. Generate the responsive derivatives below, and update each `picture`, image dimensions, alt text, caption, and full-size link together.
5. Update the home link, section-navigation anchors, and entries in `#research-menu`. Preserve the navigation IDs unless you also update `static/js/index.js`.
6. Run the checks below, inspect desktop and mobile layouts, then publish through the target repository's configured GitHub Pages branch.

### Files

- `index.html`: content and semantic components.
- `static/css/index.css`: design tokens, responsive layout, component styles.
- `static/js/index.js`: mobile navigation, More Research disclosure, table overflow hints.
- `static/css/bulma.min.css`: base styles and resource buttons.
- `static/js/fontawesome.all.min.js`: SVG icons; do not add the legacy icon-font CSS, which references absent webfont files.
- `static/images/`: original research figures; `responsive/` contains generated WebP derivatives.
- `scripts/prepare_images.py`: optional image-asset preparation.
- `scripts/check_site.py`: dependency-free static checks.

Google Sans, Noto Sans, and Academicons are loaded externally. The CSS includes local sans-serif fallbacks. The page content, navigation links, original figure links, and horizontal tables remain usable without JavaScript.

## Visual system

Edit the variables at the top of `static/css/index.css` first:

| Token | Default | Purpose |
| --- | --- | --- |
| `--page-width` | 1120px | Main content and figures |
| `--reading-width` | 920px | Abstract and citation |
| `--page-gutter` | 32px / 20px on mobile | Page-side spacing |
| `--section-space` | 72px / 60px / 48px | Section rhythm |
| `--color-link` | #3273dc | Links and highlighted results |
| `--color-surface` | #f7f9fc | Subtle data and code surfaces |

Keep the white background, natural letter spacing, uniform resource buttons, and restrained borders. Avoid enclosing every paragraph or figure in a card. Do not add hover movement or scroll-reveal effects that hide content.

Breakpoints are 1024px, 768px, 480px, and 340px. Long titles shrink and separate into name/detail on small screens; body text remains readable rather than shrinking to fit.

## Content components

### Sections and reading columns

Use a `paper-section` with an ID, a matching `aria-labelledby`, a `page-shell`, and a `section-heading`. Add `reading-shell` for sustained prose, or `paper-section--subtle` for a data-heavy section.

The default narrative order is overview → method details/example → trends → complete results. Change the order to match the paper rather than filling unnecessary sections.

### Feature lists

`feature-list` lays out three concise points in columns and stacks them on mobile. Use `feature-list--numbered` for ordered stages or levels. Preserve `role="list"` when visually removing bullets. Keep a heading and its explanatory sentence together in each list item.

### Figures

Use `paper-figure`, `figure-link`, and `figure-caption`. Wide, detailed diagrams use the full content width; `figure-grid` places two related charts side by side and stacks them on mobile.

Each figure should have:

- a `picture` with responsive sources and a fallback `img`;
- numeric intrinsic `width`/`height`, meaningful `alt`, `loading="lazy"`, and `decoding="async"`;
- a link to the unchanged original, usable without a modal or JavaScript;
- a brief, non-italic caption explaining the metric or figure, without introducing unsupported scientific claims.

To generate WebP derivatives (Python 3.9+ and Pillow required):

```sh
python -m pip install Pillow
python scripts/prepare_images.py "static/images/*.png"
```

By default this generates 640px, 1280px, and 2400px widths without upscaling. If a source is smaller, use the actual generated widths in `srcset`; do not advertise files that do not exist. Originals are never overwritten. When adjusting page widths, also review the images' `sizes` attributes.

### Results tables

Use `data-table` within `table-wrapper` and `table-shell data-scroll-table`. Keep real table markup so values stay comparable:

- Put each model family in a separate `tbody`.
- Add `column-group` and a `column-group-label` span to top-level column groups; the label stays beside the fixed Settings column while its group is being viewed.
- Use column header `scope="col"` / `scope="colgroup"` and row header `scope="row"`.
- Apply `sticky-column` only to the intended row-label column, not every first cell of multi-level headers.
- Mark each model-family header with `group-row`, `scope="rowgroup"`, and a `group-label` span. This label remains visible while scrolling.
- Give each scroll region `tabindex="0"`, `role="region"`, and a unique `aria-labelledby`. Associate its uniquely identified `table-scroll-hint` using `aria-describedby`.
- Keep `best` / `second` styles tied to verified data. Do not infer new best values as part of a visual refresh.

The script detects real overflow and hides the scroll hint when unnecessary. Settings labels stay fixed; data can scroll horizontally. A subtle edge shadow disappears at the end.

### Navigation and end matter

More Research is a click-controlled disclosure, not an ARIA application menu. Add ordinary links to `#research-menu`. Escape closes the dropdown first, then the mobile navigation, and returns focus to its control. Outside clicks and leaving the navigation with Tab close it.

Citation uses a horizontally scrollable `pre` block. Keep footer links and attribution compact. This base is derived from the Nerfies academic template; preserve applicable attribution and third-party notices when redistributing it.

## Validation

Preview locally:

```sh
python -m http.server 8000
```

Then visit `http://localhost:8000`. Static checks:

```sh
python scripts/check_site.py
node --check static/js/index.js
git diff --check
```

Before publishing, inspect at least 1440×900, 768×1024, 390×844, and 320px wide:

- The full title is present; authors and resource buttons do not overlap.
- The body has no horizontal overflow; detailed figures have working full-size links.
- Table scrolling keeps Settings and model-family labels visible, including after scrolling to the far right.
- More Research and the mobile menu work with Enter/Space, Tab, Escape, and touch; focus is visible.
- All fonts/images load without failed requests; reduced-motion and JavaScript-disabled modes remain usable.
- The scientific text, links, figures, table values, and citation match the paper's authoritative source.

The static checker does not validate scientific accuracy, remote-link availability, or visual appearance. Keep those review steps explicit.
