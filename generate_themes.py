#!/usr/bin/env python3
"""
Generate "Color Sea" VSCode theme variants. 

Refactored from Ruby Sea. Now generates standalone themes into the `themes/` directory.
"""

import json
import os
import re
import colorsys

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────
PUBLISHER_NAME = "danilodanese"  # Change this to your actual publisher ID
EXTENSION_NAME = "color-sea"
DISPLAY_NAME   = "Color Sea"
REPO_URL       = "https://github.com/danilodanese/color-sea"  # Update this!


# Lightness targets for consistent deep dark backgrounds
TARGET_L_DEEP   = 10     # Sidebar / Panel
TARGET_L_EDITOR = 12    # Main Editor
TARGET_L_MID    = 14    # Selections

# ─────────────────────────────────────────────────────────────
#  SOURCE THEME COLOR MAP (Ruby Sea template)
# ─────────────────────────────────────────────────────────────
SOURCE_COLORS = {
    "BG_DEEP":      "#0e1b2a",
    "BG_EDITOR":    "#122236",
    "BG_MID":       "#214b78",
    "FG_MUTED":     "#6592b3",
    "FG_MAIN":      "#a2aabc",
    "FG_BRIGHT":    "#c5d3e0",
    "ACCENT_PRI":   "#ff4c5a",
    "ACCENT_SEC":   "#ffd580",
    "ACCENT_TER":   "#3da5f6",
    "ACCENT_QUA":   "#62c6ff",
    "ACCENT_OP":    "#ff6b57",
    "ERROR":        "#ff2d3b",
    "SHADOW":       "#00030F",
    "ANSI_DIM":     "#444a5e",
}

# ─────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(round(r)), int(round(g)), int(round(b)))

def hex_to_hsl(h):
    r, g, b = [x / 255.0 for x in hex_to_rgb(h)]
    hue, lig, sat = colorsys.rgb_to_hls(r, g, b)
    return (hue * 360, sat * 100, lig * 100)

def hsl_to_hex(h, s, l):
    h_n, s_n, l_n = h / 360.0, s / 100.0, l / 100.0
    r, g, b = colorsys.hls_to_rgb(h_n, l_n, s_n)
    return rgb_to_hex(r * 255, g * 255, b * 255)

def adjust_lightness(hex_color, delta_l):
    h, s, l = hex_to_hsl(hex_color)
    l = max(0, min(100, l + delta_l))
    return hsl_to_hex(h, s, l)

def set_lightness(hex_color, target_l):
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h, s, target_l)

def derive_fg_main(bg_editor_hex):
    h, s, l = hex_to_hsl(bg_editor_hex)
    return hsl_to_hex(h, max(8, s * 0.20), 72)

def derive_fg_bright(bg_editor_hex):
    h, s, l = hex_to_hsl(bg_editor_hex)
    return hsl_to_hex(h, max(12, s * 0.35), 87)

def derive_shadow(bg_deep_hex):
    h, s, l = hex_to_hsl(bg_deep_hex)
    return hsl_to_hex(h, s * 0.5, max(0, l - 4))

def derive_ansi_dim(bg_editor_hex):
    h, s, l = hex_to_hsl(bg_editor_hex)
    return hsl_to_hex(h, max(8, s * 0.25), 28)

# ─────────────────────────────────────────────────────────────
#  PALETTES
# ─────────────────────────────────────────────────────────────
DARK_PALETTES = {
    "Orange": {
        "BG_DEEP":    "#481E0C", "BG_EDITOR":  "#642A11", "BG_MID":     "#7D3515", "FG_MUTED":   "#9D4924",
        "ACCENT_PRI": "#2A9D8F", "ACCENT_SEC": "#E9C46A", "ACCENT_TER": "#00B4D8", "ACCENT_QUA": "#F4A261", "ACCENT_OP":  "#E76F51", "ERROR":      "#EF233C",
    },
    "Red": {
        "BG_DEEP":    "#551420", "BG_EDITOR":  "#701F2D", "BG_MID":     "#7E2D3B", "FG_MUTED":   "#954452",
        "ACCENT_PRI": "#00BBF9", "ACCENT_SEC": "#FFD60A", "ACCENT_TER": "#F15BB5", "ACCENT_QUA": "#00F5D4", "ACCENT_OP":  "#F49CBB", "ERROR":      "#FFBA08",
    },
    "Yellow": {
        "BG_DEEP":    "#37270C", "BG_EDITOR":  "#4D3611", "BG_MID":     "#604415", "FG_MUTED":   "#7F5A1C",
        "ACCENT_PRI": "#9B5DE5", "ACCENT_SEC": "#F15BB5", "ACCENT_TER": "#3A86FF", "ACCENT_QUA": "#00F5D4", "ACCENT_OP":  "#FF006E", "ERROR":      "#EF233C",
    },
    "Purple": {
        "BG_DEEP":    "#2C1E5D", "BG_EDITOR":  "#3C2E6D", "BG_MID":     "#4A3C7B", "FG_MUTED":   "#615392",
        "ACCENT_PRI": "#FFD60A", "ACCENT_SEC": "#FF006E", "ACCENT_TER": "#00F5D4", "ACCENT_QUA": "#E0AAFF", "ACCENT_OP":  "#FFC300", "ERROR":      "#EF233C",
    },
    "Green": {
        "BG_DEEP":    "#14322F", "BG_EDITOR":  "#1C4642", "BG_MID":     "#235752", "FG_MUTED":   "#2F736C",
        "ACCENT_PRI": "#F15BB5", "ACCENT_SEC": "#FFC300", "ACCENT_TER": "#9B5DE5", "ACCENT_QUA": "#00F5D4", "ACCENT_OP":  "#F4A261", "ERROR":      "#EF233C",
    },
    "Blue": {
        "BG_DEEP":    "#102E54", "BG_EDITOR":  "#173F75", "BG_MID":     "#224E87", "FG_MUTED":   "#39659E",
        "ACCENT_PRI": "#F15BB5", "ACCENT_SEC": "#FEE440", "ACCENT_TER": "#9B5DE5", "ACCENT_QUA": "#00BBF9", "ACCENT_OP":  "#F49CBB", "ERROR":      "#EF233C",
    },
    "Gray": {
        "BG_DEEP":    "#262930", "BG_EDITOR":  "#363940", "BG_MID":     "#44474E", "FG_MUTED":   "#5B5E65",
        "ACCENT_PRI": "#FF6E40", "ACCENT_SEC": "#1DE9B6", "ACCENT_TER": "#448AFF", "ACCENT_QUA": "#FFAB40", "ACCENT_OP":  "#FF8A65", "ERROR":      "#FF1744",
    },
}

LIGHT_ACCENT_COLORS = {
    "Orange":  "#FCD1BE", "Red":     "#FCCCD5", "Yellow":  "#F2D8B0",
    "Purple":  "#DED4FF", "Green":   "#C1E8E4", "Blue":    "#C8DFFF", "Gray":    "#D3D6DD",
}


# ─────────────────────────────────────────────────────────────
#  GENERATION LOGIC
# ─────────────────────────────────────────────────────────────

def build_color_map(palette):
    bg_deep   = set_lightness(palette["BG_DEEP"], TARGET_L_DEEP)
    bg_editor = set_lightness(palette["BG_EDITOR"], TARGET_L_EDITOR)
    bg_mid    = set_lightness(palette["BG_MID"], TARGET_L_MID)

    fg_main   = derive_fg_main(bg_editor)
    fg_bright = derive_fg_bright(bg_editor)
    shadow    = derive_shadow(bg_deep)
    ansi_dim  = derive_ansi_dim(bg_editor)

    return {
        SOURCE_COLORS["BG_DEEP"]:    bg_deep,
        SOURCE_COLORS["BG_EDITOR"]:  bg_editor,
        SOURCE_COLORS["BG_MID"]:     bg_mid,
        SOURCE_COLORS["FG_MUTED"]:   palette["FG_MUTED"],
        SOURCE_COLORS["FG_MAIN"]:    fg_main,
        SOURCE_COLORS["FG_BRIGHT"]:  fg_bright,
        SOURCE_COLORS["ACCENT_PRI"]: palette["ACCENT_PRI"],
        SOURCE_COLORS["ACCENT_SEC"]: palette["ACCENT_SEC"],
        SOURCE_COLORS["ACCENT_TER"]: palette["ACCENT_TER"],
        SOURCE_COLORS["ACCENT_QUA"]: palette["ACCENT_QUA"],
        SOURCE_COLORS["ACCENT_OP"]:  palette["ACCENT_OP"],
        SOURCE_COLORS["ERROR"]:      palette["ERROR"],
        SOURCE_COLORS["SHADOW"]:     shadow,
        SOURCE_COLORS["ANSI_DIM"]:   ansi_dim,
    }

def apply_color_map(source_json_str, color_map):
    result = source_json_str
    for src, tgt in sorted(color_map.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = re.compile(re.escape(src.lower()) + r'([0-9a-fA-F]{0,2})(?=["\s,}])', re.IGNORECASE)
        result = pattern.sub(lambda m: tgt.lower() + m.group(1).lower(), result)
    return result

def clean_json(content):
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r',\s*([}\]])', r'\1', content)
    return content

def generate_theme(source_str, name, palette, light_accent=None):
    color_map = build_color_map(palette)
    themed_str = apply_color_map(source_str, color_map)
    clean = clean_json(themed_str)
    
    try:
        theme_data = json.loads(clean)
    except json.JSONDecodeError:
        # Try harder cleanup
        clean = re.sub(r',\s*,', ',', clean)
        theme_data = json.loads(clean)

    theme_data["name"] = name
    theme_data["type"] = "dark"

    if light_accent:
        la = light_accent.lower()
        colors = theme_data.get("colors", {})
        colors["editorBracketMatch.background"] = la + "20"
        colors["editor.findMatchBorder"] = la
        colors["editorBracketMatch.border"] = la + "70"
        colors["editor.selectionHighlightBackground"] = la + "15"
        theme_data["colors"] = colors

    return json.dumps(theme_data, indent=2) + "\n"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "themes", "rubysea-color-theme.json")
    
    # 1. READ SOURCE (but do not edit specific file)
    print(f"📖 Reading source template: {source_path}")
    with open(source_path, "r") as f:
        source_str = f.read()

    themes_dir = os.path.join(script_dir, "themes")
    os.makedirs(themes_dir, exist_ok=True)

    # 2. ClEANUP OLD FILES (dark/, light/, and old theme files)
    for old_dir in ["dark", "light"]:
        odir = os.path.join(script_dir, old_dir)
        if os.path.isdir(odir):
            import shutil
            shutil.rmtree(odir)
            print(f"🗑️  Removed {old_dir}/ directory")

    # Remove generated files in themes/ to avoid duplicates, BUT KEEP RUBY SEA SOURCE
    for f in os.listdir(themes_dir):
        if f.startswith("color-sea-") and f.endswith(".json"):
            os.remove(os.path.join(themes_dir, f))

    # 3. GENERATE THEMES
    print(f"\n🎨 Generating {DISPLAY_NAME} themes...")
    generated_themes = []

    for color_name, palette in DARK_PALETTES.items():
        theme_label = f"{DISPLAY_NAME} {color_name}"
        filename    = f"color-sea-{color_name.lower()}.json"
        filepath    = os.path.join(themes_dir, filename)
        light_accent = LIGHT_ACCENT_COLORS.get(color_name)

        print(f"  → {theme_label}")
        theme_json = generate_theme(source_str, theme_label, palette, light_accent)
        
        with open(filepath, "w") as f:
            f.write(theme_json)
        
        generated_themes.append({
            "label": theme_label,
            "uiTheme": "vs-dark",
            "path": f"./themes/{filename}"
        })

    # 4. UPDATE PACKAGE.JSON
    pkg_path = os.path.join(script_dir, "package.json")
    with open(pkg_path, "r") as f:
        pkg = json.load(f)

    # Update metadata
    pkg["name"] = EXTENSION_NAME
    pkg["displayName"] = DISPLAY_NAME
    pkg["publisher"] = PUBLISHER_NAME
    pkg["description"] = "A collection of vibrant, deep dark themes for VS Code."
    pkg["repository"]["url"] = REPO_URL
    pkg["homepage"] = f"{REPO_URL}/blob/main/README.md"
    pkg["bugs"]["url"] = f"{REPO_URL}/issues"

    # Only include generated themes (Ruby Sea source is excluded)
    pkg["contributes"]["themes"] = generated_themes

    with open(pkg_path, "w") as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")

    print(f"\n📦 Updated package.json:")
    print(f"   Name: {pkg['name']}")
    print(f"   Display Name: {pkg['displayName']}")
    print(f"   Publisher: {pkg['publisher']}")
    print(f"   Themes: {len(generated_themes)}")

    # 5. RENAME SOURCE FILE TO AVOID CONFUSION (Optional, but good practice)
    # We'll just leave it as is for now, as it's not contributing to the package.

    print("\n🎉 Refactor complete! Ready to package.")

if __name__ == "__main__":
    main()
