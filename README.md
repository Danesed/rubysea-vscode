# Color Sea

Color Sea is a collection of seven dark VS Code themes built around the same surface-depth system and different accent families.

## Variants

- `Color Sea Orange`
- `Color Sea Red`
- `Color Sea Yellow`
- `Color Sea Purple`
- `Color Sea Green`
- `Color Sea Blue`
- `Color Sea Gray`

## Design Notes

- Shared structure: low-contrast UI surfaces, stronger editor selection layers, and a neutral text ladder derived from the editor background.
- Variant differences come from accent roles rather than from unstable background shifts.
- This release is published as a standalone theme set. The original source work comes from the MIT-licensed `rubysea-vscode` project by `barkerbg001`; the required attribution is preserved in `LICENSE`.

## Install Locally

```bash
npm install
npx vsce package
code --install-extension color-sea-1.0.6.vsix --force
```

Then open `Preferences: Color Theme` in VS Code and select one of the `Color Sea` variants.

## Development

- The source template lives in `themes/color-sea-template.json`.
- Generated themes live in `themes/color-sea-*.json`.
- Run `PYTHONDONTWRITEBYTECODE=1 python3 generate_themes.py` after changing the generator or template.
- Replace `images/logo.png` when the new icon is ready.
