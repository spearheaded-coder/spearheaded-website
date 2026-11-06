# Spearheaded — website

Static website for Spearheaded (private client planning, Toronto). Hosted on Netlify; every push to `main` publishes the site.

## Structure

- `src/pages/` — page bodies (one file per page, with title/description at the top)
- `src/assets/` — stylesheet and script
- `src/static/` — favicon, robots.txt, sitemap.xml
- `tools/film.py` — generates the hero film (sky, weather and engraved summit)
- `build_site.py` — assembles pages with the shared header, footer and artwork into `dist/`
- `check_site.py` — checks markup, links, form labels and wording

## Updating

```bash
python3 build_site.py      # rebuild dist/
python3 check_site.py dist # check before publishing
git commit -am "Describe the change" && git push
```

## Before launch

- Fill the placeholders: phone, email, regulatory disclosure, privacy policy details, founder sentence, portrait.
- Remove the `X-Robots-Tag = "noindex"` line from `netlify.toml`.
- Point spearheaded.ca at the Netlify site.
