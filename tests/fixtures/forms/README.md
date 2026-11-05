# Form fixtures for `jk formcheck`

Static pages that reproduce engine traps. Serve the folder (`python3 -m http.server 8651 --directory
tests/fixtures/forms`), open a page, paste `jk formcheck` output into the browser's JS console.

| Page | Expected result |
|---|---|
| `lever-like.html` | `form: "application"` (not the site search), `required: 5`, empty = Email, Resume/CV, privacy checkbox. The answered Yes/No/Unsure group counts once and is filled; the "Accepted: .pdf, .docx" hint is not an attached file. |
| `no-labels.html` | `required: 0` plus a `warning` (labels aren't `<label>`, as on Gem) — zero is not proof. |
