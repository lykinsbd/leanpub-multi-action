# Leanpub multi-action

Interact with Leanpub via GitHub Actions

## Inputs

### `leanpub-api-key`

**Required** The Leanpub API key for your account, which requires a "Pro" plan on Leanpub.com.
Recommended to place this in a GitHub Secret named `LEANPUB_API_KEY`.

### `leanpub-book-slug`

**Required** The "slugified" name of your book, i.e. "mygreatbook" for "My Great Book".
Per Leanpub's [API documentation](https://leanpub.com/help/api), it is "the part of the URL for your book after `https://leanpub.com/"`.

### `action`

**Required** The action to perform. One of: `preview`, `publish`, or `check-status`.

### `email-readers`

Boolean, set to `"true"` to email readers about a new publish. Only used with `action: publish`.

### `release-notes`

Release notes for the publish. Only used with `action: publish`.

## Example Usage

Below is an example workflow file:

```YAML
---
name: "Push to Preview"

"on":
  push:
    branches: ["preview"]
  workflow_dispatch: null

jobs:
  preview_build:
    runs-on: "ubuntu-latest"
    steps:
      - name: "Preview Build"
        uses: "lykinsbd/leanpub-multi-action@v2"
        with:
          leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
          leanpub-book-slug: "mygreatbook"
          action: "preview"
```

### Publish with release notes

```YAML
- name: "Publish"
  uses: "lykinsbd/leanpub-multi-action@v2"
  with:
    leanpub-api-key: "${{ secrets.LEANPUB_API_KEY }}"
    leanpub-book-slug: "mygreatbook"
    action: "publish"
    email-readers: "true"
    release-notes: "Chapter 5 added"
```

### CLI Usage

```bash
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook preview
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook publish --email-readers --release-notes "v2"
lma --leanpub-api-key YOUR_KEY --book-slug mygreatbook check-status
```
