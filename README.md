# Dan Anthony Dorado Academic Portfolio

This repository contains a GitHub Pages-ready personal academic website for Dan Anthony Dorado. The site is built directly from the contents of `download_resume.pdf` and presents teaching, research, publications, projects, advising, talks, service, and contact information in a clean static structure.

An editable Markdown reference, `wiki.md`, is also included as a working resume mirror. When `wiki.md` is updated, the corresponding content in `index.html` should be updated as well.

A GitHub Actions workflow now supports that sync automatically: pushing a change to `wiki.md` on `main` runs the repo sync script and commits the refreshed `index.html` back to the branch.

## Project overview

- Static single-page academic portfolio built with HTML, CSS, and vanilla JavaScript
- GitHub Pages compatible with no build step required
- CV-heavy sections are currently rendered from JavaScript data blocks embedded in `index.html`
- Long sections such as talks and advising include lightweight client-side filters for readability

## Folder structure

```text
Website/
|-- index.html
|-- wiki.md
|-- download_resume.pdf
|-- assets/
|   |-- css/
|   |   `-- styles.css
|   |-- icons/
|   |   `-- favicon.svg
|   `-- js/
|       |-- content.js
|       `-- site.js
`-- README.md
```

## Suggested folder structure

If the site grows later, this structure will scale cleanly:

```text
Website/
|-- index.html
|-- pages/
|   |-- publications.html
|   |-- teaching.html
|   `-- talks.html
|-- assets/
|   |-- css/
|   |   |-- styles.css
|   |   `-- print.css
|   |-- icons/
|   |-- images/
|   `-- js/
|       |-- content.js
|       |-- site.js
|       `-- filters.js
|-- data/
|   |-- publications.json
|   |-- talks.json
|   `-- advising.json
`-- download_resume.pdf
```

## How to run locally

Because the site is static, you can preview it in either of these ways:

1. Open `index.html` directly in a browser.
2. Or serve the folder locally with a small HTTP server:

```powershell
python -m http.server 8000
```

Then visit `http://localhost:8000/`.

## How to deploy to GitHub Pages

This repository is already structured for a user or organization site such as `dddorado.github.io`.

1. Push the contents of this repository to the default branch of the `dddorado.github.io` repository.
2. In GitHub, open `Settings` -> `Pages`.
3. Set the source to `Deploy from a branch`.
4. Select the default branch and the `/ (root)` folder.
5. Save the settings and wait for GitHub Pages to publish the site.

Because asset paths are relative, the site will work correctly when hosted at the repository root.

## How to update sections later

Use `wiki.md` as the working Markdown reference for resume content, then mirror those edits into `index.html` so the published website stays aligned.

- Update profile, biography, appointments, talks, publications, advising, projects, or service first in `wiki.md`
- Keep the existing `##` and `###` section headings in `wiki.md` so the sync script can parse it reliably
- Pushing `wiki.md` to `main` triggers the workflow that refreshes `index.html`
- Adjust styling in `assets/css/styles.css` if the presentation needs to change
- Extend interactions in `assets/js/site.js` only if filters or behaviors need to change

For content additions on the site, follow the same object structure already used in the JavaScript data blocks embedded in `index.html`.

## Design rationale

- The visual direction is restrained, academic, and text-forward rather than corporate or promotional.
- The layout emphasizes readability with generous spacing, strong sectioning, and serif-led headings suited to an academic profile.
- Repeated CV content is rendered from data objects so the site remains maintainable without introducing a framework or build tooling.
- Long lists are made easier to browse through search and filter controls rather than collapsing important academic work into oversimplified summaries.

## GitHub Pages deployment checklist

- Confirm `index.html` is at the repository root
- Confirm all assets are committed under `assets/`
- Confirm `download_resume.pdf` is present if the CV download button should remain active
- Enable GitHub Pages from the repository root
- Verify `https://dddorado.github.io/` after deployment
- Test navigation, filters, and external links on desktop and mobile
- Update metadata in `index.html` later if a custom social preview image is added
