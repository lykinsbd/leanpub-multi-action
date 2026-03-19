# Leanpub Multi Action

[![CI](https://github.com/lykinsbd/leanpub-multi-action/actions/workflows/tests.yml/badge.svg?branch=dev)](https://github.com/lykinsbd/leanpub-multi-action/actions/workflows/tests.yml)

A GitHub Action to interact with the [Leanpub API](https://leanpub.com/help/api).
Preview, publish, and check job status for your Leanpub books — directly from your GitHub workflows.

## Quick Start

```yaml
- name: "Preview Book"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "preview"
```

## Inputs

| Name | Required | Default | Description |
|------|----------|---------|-------------|
| `leanpub-api-key` | Yes | — | Leanpub API key (requires a [Pro plan](https://leanpub.com/help/api)). Store as a [GitHub Secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions). |
| `leanpub-book-slug` | Yes | — | Book slug — the path component after `https://leanpub.com/`. |
| `action` | Yes | — | Action to perform: `preview`, `publish`, `check-status`, or `book-summary`. |
| `email-readers` | No | `"false"` | Email readers about a new publish. Only used with `publish`. |
| `release-notes` | No | — | Release notes for the publish. Only used with `publish`. |
| `subset` | No | `"false"` | Preview only the files listed in `Subset.txt`. Only used with `preview`. |
| `single-file` | No | — | Path to a Markdown file for single-file preview. Only used with `preview`. |

## Examples

### Full preview on push

```yaml
---
name: "Preview on Push"

"on":
  push:
    branches: ["preview"]

jobs:
  preview:
    runs-on: "ubuntu-latest"
    steps:
      - name: "Preview Book"
        uses: "lykinsbd/leanpub-multi-action@v2"
        with:
          leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
          leanpub-book-slug: "mygreatbook"
          action: "preview"
```

### Subset preview

Preview only the files listed in your book's `Subset.txt`:

```yaml
- name: "Subset Preview"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "preview"
    subset: "true"
```

### Single-file preview

Preview a single Markdown file without modifying `Subset.txt`.
The output PDF is saved as `{slug}-single-file.pdf` in your Dropbox previews folder.

```yaml
- name: "Checkout"
  uses: "actions/checkout@v4"
- name: "Single File Preview"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "preview"
    single-file: "manuscript/chapter-05.md"
```

### Publish with release notes

```yaml
- name: "Publish"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "publish"
    email-readers: "true"
    release-notes: "Chapter 5 added"
```

### Check job status

```yaml
- name: "Check Status"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "check-status"
```

### Get book summary

Retrieve book metadata including download URLs, word count, and sales info:

```yaml
- name: "Book Summary"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "book-summary"
```

## CLI Usage

The action also ships as a standalone CLI tool called `lma`.

```bash
uv tool install leanpub-multi-action
```

or with pip:

```bash
pip install leanpub-multi-action
```

```bash
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook preview
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook preview --subset
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook preview --single-file chapter.md
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook publish --email-readers --release-notes "v2"
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook check-status
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook book-summary
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[Apache-2.0](LICENSE)
