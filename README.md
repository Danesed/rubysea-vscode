# Color Sea 🌊

**Color Sea** is a collection of 7 vibrant, deep dark themes for Visual Studio Code.

Designed for long coding sessions, it features **balanced deep blue/black backgrounds** and **high-contrast, neon-inspired accents** to keep your syntax distinct and readable.

## Themes

Each theme shares the same deep background structure but offers a unique accent personality:

- **Color Sea Blue**: Pop pink & yellow accents on a deep blue base.
- **Color Sea Orange**: Teal & gold pops on a warm deep background.
- **Color Sea Red**: Cyan & electric blue accents against a deep red/brown void.
- **Color Sea Green**: Rose gold & lavender accents on a deep forest floor.
- **Color Sea Purple**: Gold & cyan accents on a rich imperial purple base.
- **Color Sea Yellow**: Violet & pink accents on a deep umber background.
- **Color Sea Gray**: The classic balanced gray/blue theme.

## Installation

1. Open VS Code
2. Go to Extensions (`Cmd+Shift+X`)
3. Search for `Color Sea`
4. Install & Reload

## Customization

The backgrounds are set to absolute lightness targets for perfect balance:

- **Sidebar**: L=8 (Deep)
- **Editor**: L=10 (Slightly lighter)
- **Selections**: L=12

If you want to customize specific colors, add this to your `settings.json`:

```json
"workbench.colorCustomizations": {
    "[Color Sea Blue]": {
        "editor.background": "#050a14",
        "sideBar.background": "#020408"
    }
}
```

## Credits

Based on the original [Ruby Sea](https://marketplace.visualstudio.com/items?itemName=barkerbg001.rubysea-vscode) theme structure, but completely re-colored and re-balanced.

**Enjoy coding in the deep sea!** 🐙
