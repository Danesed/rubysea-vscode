# Publishing

This repo is prepared to ship as:

- extension name: `color-sea`
- display name: `Color Sea`
- publisher: `danesed`
- repository: `https://github.com/danesed/colorsea-vscode`

## Before Publishing

- replace `images/logo.png` with the final icon
- confirm the Marketplace publisher `danesed` exists
- confirm `danesed.color-sea` is the extension ID you want to keep long term
- keep the dual copyright notice in `LICENSE`

## Marketplace Setup

1. Create or confirm the publisher at [Visual Studio Marketplace](https://marketplace.visualstudio.com/manage).
2. Create an Azure DevOps Personal Access Token with Marketplace `Acquire` and `Manage`.
3. Log in:

```bash
npx vsce login danesed
```

## Build and Check

```bash
npm install
npm run package:vsix
```

Then install the generated `.vsix` locally and verify:

- all seven themes appear
- the new icon is visible
- the publisher is `danesed`
- the Marketplace metadata points to `colorsea-vscode`
- the preview images in `README.md` resolve from the public GitHub repo

## Publish

```bash
npx vsce publish
```

For later patch releases:

```bash
npx vsce publish patch
```

## Fresh Git Repo

If you want a clean repo with no inherited history:

```bash
mkdir ../colorsea-vscode
rsync -a --exclude '.git' --exclude 'node_modules' ./ ../colorsea-vscode/
cd ../colorsea-vscode
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin git@github.com:danesed/colorsea-vscode.git
git push -u origin main
```

Do that only after the icon is in place and you are satisfied with the final metadata.
