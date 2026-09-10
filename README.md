# Vietnamese Lark Library

A single-page index of Lark enablement docs for partners and customers in Vietnam.
Each card links to the source document on Lark. The page itself is only the table of contents.

Live: https://nixthinh-bit.github.io/lark-vn-library/

Tiếng Việt: [README.vi.md](README.vi.md)

## Updating

Content lives in `content.json`, not in the HTML. To add or change a document:

1. Edit `content.json`: a document entry has title, description, audience, level, language,
   read time, and a `shared` flag. You can also add a new entry or a whole new group.
2. Rebuild:

   ```
   python3 build.py
   ```

   This reads `content.json` and overwrites `index.html`. The header counts recalculate on their own.

`build.py` only needs editing to change colours or add a new section layout.

## Files

| File | Role |
|---|---|
| `index.html` | Generated page. This is what GitHub Pages serves. |
| `content.json` | All content: groups, documents, metadata. |
| `build.py` | Generator. `python3 build.py` regenerates `index.html`. |

## Layout

Seven groups, each with its own layout so the page does not read as one repeated grid:
split feature, numbered steps, row list, vertical stack, tabbed grid, two-column panels,
and a dark support band.

One self-contained file. No CDN, no external fonts, no network calls, so it renders the
same inside a Lark preview.
