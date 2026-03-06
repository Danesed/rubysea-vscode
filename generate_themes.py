#!/usr/bin/env python3
"""
Generate VS Code theme variants from a neutral template.

The generator keeps the shared Color Sea surface relationships while allowing each variant to define its own accent roles.
"""

import json
import os
import re
import colorsys
import math

# ─────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────
PUBLISHER_NAME = "danesed"
EXTENSION_NAME = "color-sea"
DISPLAY_NAME   = "Color Sea"
REPO_URL       = "https://github.com/danesed/colorsea-vscode"

# ─────────────────────────────────────────────────────────────
#  TEMPLATE COLOR ROLE MAP
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

def clamp(value, low, high):
    return max(low, min(high, value))

def shift_hue(hue, delta):
    return (hue + delta) % 360

def signed_hue_delta(start, end):
    return (end - start + 540) % 360 - 180

def hue_distance(start, end):
    return abs(signed_hue_delta(start, end))

def srgb_channel_to_linear(channel):
    value = channel / 255.0
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4

def relative_luminance(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    red = srgb_channel_to_linear(r)
    green = srgb_channel_to_linear(g)
    blue = srgb_channel_to_linear(b)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue

def contrast_ratio(color_a, color_b):
    lighter = max(relative_luminance(color_a), relative_luminance(color_b))
    darker = min(relative_luminance(color_a), relative_luminance(color_b))
    return (lighter + 0.05) / (darker + 0.05)

def rgb_to_oklab(hex_color):
    red, green, blue = hex_to_rgb(hex_color)
    red = srgb_channel_to_linear(red)
    green = srgb_channel_to_linear(green)
    blue = srgb_channel_to_linear(blue)

    l = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    m = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    s = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue

    l_root = l ** (1 / 3)
    m_root = m ** (1 / 3)
    s_root = s ** (1 / 3)

    return (
        0.2104542553 * l_root + 0.7936177850 * m_root - 0.0040720468 * s_root,
        1.9779984951 * l_root - 2.4285922050 * m_root + 0.4505937099 * s_root,
        0.0259040371 * l_root + 0.7827717662 * m_root - 0.8086757660 * s_root,
    )

def oklab_delta(color_a, color_b):
    light_a, a_a, b_a = rgb_to_oklab(color_a)
    light_b, a_b, b_b = rgb_to_oklab(color_b)
    chroma_a = (a_a * a_a + b_a * b_a) ** 0.5
    chroma_b = (a_b * a_b + b_b * b_b) ** 0.5
    hue_a = math.atan2(b_a, a_a)
    hue_b = math.atan2(b_b, a_b)
    diff = abs(hue_a - hue_b)
    if diff > math.pi:
        diff = (2 * math.pi) - diff
    return (
        abs(light_a - light_b),
        abs(chroma_a - chroma_b),
        diff * 180 / math.pi,
    )

# ─────────────────────────────────────────────────────────────
#  ROLE MODEL + PALETTES
# ─────────────────────────────────────────────────────────────
REFERENCE_HSL = {name: hex_to_hsl(value) for name, value in SOURCE_COLORS.items()}

RUBY_SURFACE_MODEL = {
    "deep_lightness": REFERENCE_HSL["BG_DEEP"][2],
    "deep_saturation_cap": REFERENCE_HSL["BG_DEEP"][1],
    "editor_hue_shift": signed_hue_delta(REFERENCE_HSL["BG_DEEP"][0], REFERENCE_HSL["BG_EDITOR"][0]),
    "editor_saturation_delta": REFERENCE_HSL["BG_EDITOR"][1] - REFERENCE_HSL["BG_DEEP"][1],
    "editor_lightness": REFERENCE_HSL["BG_EDITOR"][2],
    "mid_hue_shift": signed_hue_delta(REFERENCE_HSL["BG_DEEP"][0], REFERENCE_HSL["BG_MID"][0]),
    "mid_saturation_delta": REFERENCE_HSL["BG_MID"][1] - REFERENCE_HSL["BG_DEEP"][1],
    "mid_lightness": REFERENCE_HSL["BG_MID"][2],
}

RUBY_NEUTRAL_MODEL = {
    role: {
        "hue_shift": signed_hue_delta(REFERENCE_HSL["BG_EDITOR"][0], REFERENCE_HSL[role][0]),
        "saturation_scale": REFERENCE_HSL[role][1] / max(REFERENCE_HSL["BG_EDITOR"][1], 1),
        "lightness": REFERENCE_HSL[role][2],
    }
    for role in ("FG_MUTED", "FG_MAIN", "FG_BRIGHT", "ANSI_DIM", "SHADOW")
}

NEUTRAL_SATURATION_LIMITS = {
    "FG_MUTED": (14, 36),
    "FG_MAIN": (8, 18),
    "FG_BRIGHT": (12, 32),
    "ANSI_DIM": (8, 18),
    "SHADOW": (20, 100),
}

SURFACE_VALIDATION = {
    "sidebar_editor_ratio": (1.06, 1.11),
    "sidebar_editor_dlight": (0.02, 0.04),
    "sidebar_editor_dchroma_max": 0.02,
    "sidebar_editor_dhue_max": 4.0,
    "editor_mid_ratio": (1.70, 1.90),
    "editor_mid_dlight": (0.13, 0.19),
    "editor_mid_dchroma": (0.028, 0.07),
    "editor_mid_dhue_max": 8.0,
    "selection_margin": 0.55,
}

TEXT_VALIDATION = {
    "foreground": {"ratio": 4.5, "dlight": 0.18, "dchroma": 0.02, "dhue": 8.0},
    "editor.foreground": {"ratio": 6.2, "dlight": 0.22, "dchroma": 0.02, "dhue": 8.0},
    "descriptionForeground": {"ratio": 9.0, "dlight": 0.30, "dchroma": 0.02, "dhue": 8.0},
    "button.background": {"ratio": 3.9, "dlight": 0.10, "dchroma": 0.04, "dhue": 10.0},
    "editorWarning.foreground": {"ratio": 4.2, "dlight": 0.10, "dchroma": 0.03, "dhue": 10.0},
    "editorInfo.foreground": {"ratio": 4.2, "dlight": 0.10, "dchroma": 0.03, "dhue": 10.0},
    "editorError.foreground": {"ratio": 3.75, "dlight": 0.10, "dchroma": 0.03, "dhue": 10.0},
}

THEME_SPECS = {
    "Orange": {
        "surface_seed": "#3A261B",
        "accent_primary": "#FB5607",
        "accent_warning": "#FFBE0B",
        "accent_info": "#4D8EFF",
        "accent_added": "#56CFE1",
        "accent_error": "#FF2D3B",
        "accent_warm": "#FF9F1C",
    },
    "Red": {
        "surface_seed": "#341A23",
        "accent_primary": "#FF4D5A",
        "accent_warning": "#F7B801",
        "accent_info": "#3A86FF",
        "accent_added": "#72E3FF",
        "accent_error": "#FF2D3B",
        "accent_warm": "#FB5607",
    },
    "Yellow": {
        "surface_seed": "#47341B",
        "accent_primary": "#FFBE0B",
        "accent_warning": "#FFE45E",
        "accent_info": "#7B8CFF",
        "accent_added": "#72DDF7",
        "accent_error": "#FF2D3B",
        "accent_warm": "#F18701",
    },
    "Purple": {
        "surface_seed": "#31284B",
        "accent_primary": "#8B5CF6",
        "accent_warning": "#F7B801",
        "accent_info": "#4CC9F0",
        "accent_added": "#C77DFF",
        "accent_error": "#FF2D3B",
        "accent_warm": "#F35B04",
    },
    "Green": {
        "surface_seed": "#163639",
        "accent_primary": "#2EC4B6",
        "accent_warning": "#FFD166",
        "accent_info": "#00A6FB",
        "accent_added": "#80FFDB",
        "accent_error": "#FF2D3B",
        "accent_warm": "#FF9F1C",
    },
    "Blue": {
        "surface_seed": "#1A2D4A",
        "accent_primary": "#FF595E",
        "accent_warning": "#FFD166",
        "accent_info": "#00BBF9",
        "accent_added": "#90E0EF",
        "accent_error": "#FF2D3B",
        "accent_warm": "#FB8500",
    },
    "Gray": {
        "surface_seed": "#2F3444",
        "accent_primary": "#FF595E",
        "accent_warning": "#FFCA3A",
        "accent_info": "#5C7CFA",
        "accent_added": "#72DDF7",
        "accent_error": "#FF2D3B",
        "accent_warm": "#FF9F1C",
    },
}

LIGHT_ACCENT_COLORS = {
    "Orange": "#FFE08A",
    "Red": "#FFD6D9",
    "Yellow": "#FFF0A8",
    "Purple": "#DDD2FF",
    "Green": "#C8FFF4",
    "Blue": "#D1F1FF",
    "Gray": "#D8E8FF",
}


# ─────────────────────────────────────────────────────────────
#  GENERATION LOGIC
# ─────────────────────────────────────────────────────────────
def build_surface_roles(surface_seed):
    surface_hue, surface_saturation, _ = hex_to_hsl(surface_seed)
    surface_saturation = min(surface_saturation, RUBY_SURFACE_MODEL["deep_saturation_cap"])

    bg_deep = hsl_to_hex(
        surface_hue,
        surface_saturation,
        RUBY_SURFACE_MODEL["deep_lightness"],
    )
    bg_editor = hsl_to_hex(
        shift_hue(surface_hue, RUBY_SURFACE_MODEL["editor_hue_shift"]),
        clamp(surface_saturation + RUBY_SURFACE_MODEL["editor_saturation_delta"], 0, 100),
        RUBY_SURFACE_MODEL["editor_lightness"],
    )
    bg_mid = hsl_to_hex(
        shift_hue(surface_hue, RUBY_SURFACE_MODEL["mid_hue_shift"]),
        clamp(surface_saturation + RUBY_SURFACE_MODEL["mid_saturation_delta"], 0, 100),
        RUBY_SURFACE_MODEL["mid_lightness"],
    )
    bg_editor = tune_surface_contrast(
        bg_editor,
        bg_deep,
        *SURFACE_VALIDATION["sidebar_editor_ratio"],
    )
    bg_mid = tune_surface_contrast(
        bg_mid,
        bg_editor,
        *SURFACE_VALIDATION["editor_mid_ratio"],
    )
    bg_mid = tune_surface_chroma(
        bg_mid,
        bg_editor,
        SURFACE_VALIDATION["editor_mid_dchroma"][1],
        *SURFACE_VALIDATION["editor_mid_ratio"],
    )

    return {
        "BG_DEEP": bg_deep,
        "BG_EDITOR": bg_editor,
        "BG_MID": bg_mid,
    }

def derive_neutral_role(bg_editor_hex, role_name):
    editor_hue, editor_saturation, _ = hex_to_hsl(bg_editor_hex)
    role_model = RUBY_NEUTRAL_MODEL[role_name]
    sat_min, sat_max = NEUTRAL_SATURATION_LIMITS[role_name]
    saturation = clamp(editor_saturation * role_model["saturation_scale"], sat_min, sat_max)
    return hsl_to_hex(
        shift_hue(editor_hue, role_model["hue_shift"]),
        saturation,
        role_model["lightness"],
    )

def lift_until_contrast(color_hex, background_hex, minimum_ratio):
    hue, saturation, lightness = hex_to_hsl(color_hex)
    while contrast_ratio(color_hex, background_hex) < minimum_ratio and lightness < 96:
        lightness += 1
        color_hex = hsl_to_hex(hue, saturation, lightness)
    return color_hex

def tune_surface_contrast(color_hex, anchor_hex, minimum_ratio, maximum_ratio):
    hue, saturation, lightness = hex_to_hsl(color_hex)
    for _ in range(200):
        ratio = contrast_ratio(color_hex, anchor_hex)
        if minimum_ratio <= ratio <= maximum_ratio:
            break
        if ratio < minimum_ratio and lightness < 96:
            lightness += 0.25
        elif ratio > maximum_ratio and lightness > 0:
            lightness -= 0.25
        else:
            break
        color_hex = hsl_to_hex(hue, saturation, lightness)
    return color_hex

def tune_surface_chroma(color_hex, anchor_hex, maximum_dchroma, minimum_ratio, maximum_ratio):
    hue, saturation, lightness = hex_to_hsl(color_hex)
    for _ in range(200):
        _, dchroma, _ = oklab_delta(color_hex, anchor_hex)
        if dchroma <= maximum_dchroma or saturation <= 0:
            break
        saturation = max(0, saturation - 0.5)
        color_hex = hsl_to_hex(hue, saturation, lightness)
        color_hex = tune_surface_contrast(color_hex, anchor_hex, minimum_ratio, maximum_ratio)
        hue, saturation, lightness = hex_to_hsl(color_hex)
    return color_hex

def build_role_palette(spec):
    surfaces = build_surface_roles(spec["surface_seed"])
    bg_editor = surfaces["BG_EDITOR"]
    fg_muted = lift_until_contrast(
        derive_neutral_role(bg_editor, "FG_MUTED"),
        bg_editor,
        TEXT_VALIDATION["foreground"]["ratio"],
    )
    fg_main = lift_until_contrast(
        derive_neutral_role(bg_editor, "FG_MAIN"),
        bg_editor,
        TEXT_VALIDATION["editor.foreground"]["ratio"],
    )
    fg_bright = lift_until_contrast(
        derive_neutral_role(bg_editor, "FG_BRIGHT"),
        bg_editor,
        TEXT_VALIDATION["descriptionForeground"]["ratio"],
    )

    return {
        **surfaces,
        "FG_MUTED": fg_muted,
        "FG_MAIN": fg_main,
        "FG_BRIGHT": fg_bright,
        "ACCENT_PRI": spec["accent_primary"],
        "ACCENT_SEC": spec["accent_warning"],
        "ACCENT_TER": spec["accent_info"],
        "ACCENT_QUA": spec["accent_added"],
        "ACCENT_OP": spec.get("accent_warm", spec["accent_primary"]),
        "ERROR": spec["accent_error"],
        "SHADOW": derive_neutral_role(bg_editor, "SHADOW"),
        "ANSI_DIM": derive_neutral_role(bg_editor, "ANSI_DIM"),
    }

def build_color_map(spec):
    palette = build_role_palette(spec)
    return {SOURCE_COLORS[key]: value for key, value in palette.items()}

def validate_range(errors, label, value, lower, upper):
    if value < lower or value > upper:
        errors.append(f"{label}={value:.3f} outside {lower:.3f}..{upper:.3f}")

def validate_theme(name, theme_data):
    colors = theme_data["colors"]
    errors = []

    sidebar_background = colors["sideBar.background"]
    editor_background = colors["editor.background"]
    editor_selection = colors["editor.selectionBackground"]

    surface_ratio = contrast_ratio(sidebar_background, editor_background)
    surface_dlight, surface_dchroma, _ = oklab_delta(sidebar_background, editor_background)
    surface_hue = hue_distance(hex_to_hsl(sidebar_background)[0], hex_to_hsl(editor_background)[0])

    validate_range(
        errors,
        "sidebar/editor contrast",
        surface_ratio,
        *SURFACE_VALIDATION["sidebar_editor_ratio"],
    )
    validate_range(
        errors,
        "sidebar/editor OKLab dL",
        surface_dlight,
        *SURFACE_VALIDATION["sidebar_editor_dlight"],
    )
    if surface_dchroma > SURFACE_VALIDATION["sidebar_editor_dchroma_max"]:
        errors.append(
            f"sidebar/editor OKLab dC={surface_dchroma:.3f} above {SURFACE_VALIDATION['sidebar_editor_dchroma_max']:.3f}"
        )
    if surface_hue > SURFACE_VALIDATION["sidebar_editor_dhue_max"]:
        errors.append(
            f"sidebar/editor hue delta={surface_hue:.1f} above {SURFACE_VALIDATION['sidebar_editor_dhue_max']:.1f}"
        )

    selection_ratio = contrast_ratio(editor_background, editor_selection)
    selection_dlight, selection_dchroma, _ = oklab_delta(editor_background, editor_selection)
    selection_hue = hue_distance(hex_to_hsl(editor_background)[0], hex_to_hsl(editor_selection)[0])

    validate_range(
        errors,
        "editor/selection contrast",
        selection_ratio,
        *SURFACE_VALIDATION["editor_mid_ratio"],
    )
    validate_range(
        errors,
        "editor/selection OKLab dL",
        selection_dlight,
        *SURFACE_VALIDATION["editor_mid_dlight"],
    )
    validate_range(
        errors,
        "editor/selection OKLab dC",
        selection_dchroma,
        *SURFACE_VALIDATION["editor_mid_dchroma"],
    )
    if selection_hue > SURFACE_VALIDATION["editor_mid_dhue_max"]:
        errors.append(
            f"editor/selection hue delta={selection_hue:.1f} above {SURFACE_VALIDATION['editor_mid_dhue_max']:.1f}"
        )
    if selection_ratio <= surface_ratio + SURFACE_VALIDATION["selection_margin"]:
        errors.append(
            "editor selection layer is not sufficiently stronger than the sidebar/editor separation"
        )

    for color_key, thresholds in TEXT_VALIDATION.items():
        foreground = colors[color_key]
        ratio = contrast_ratio(foreground, editor_background)
        dlight, dchroma, _ = oklab_delta(foreground, editor_background)
        hue = hue_distance(hex_to_hsl(foreground)[0], hex_to_hsl(editor_background)[0])

        if ratio < thresholds["ratio"]:
            errors.append(f"{color_key} contrast={ratio:.3f} below {thresholds['ratio']:.3f}")
        if (
            dlight < thresholds["dlight"]
            and dchroma < thresholds["dchroma"]
            and hue < thresholds["dhue"]
        ):
            errors.append(
                f"{color_key} is not perceptually distinct enough from editor.background"
            )

    if errors:
        joined = "\n  - ".join(errors)
        raise ValueError(f"{name} failed validation:\n  - {joined}")

    return {
        "surface_ratio": surface_ratio,
        "selection_ratio": selection_ratio,
        "editor_fg_ratio": contrast_ratio(colors["editor.foreground"], editor_background),
        "info_ratio": contrast_ratio(colors["editorInfo.foreground"], editor_background),
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

def generate_theme(source_str, name, spec, light_accent=None):
    color_map = build_color_map(spec)
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

    metrics = validate_theme(name, theme_data)
    return json.dumps(theme_data, indent=2) + "\n", metrics

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "themes", "color-sea-template.json")
    template_filename = os.path.basename(source_path)
    
    # 1. READ SOURCE (but do not edit specific file)
    print(f"📖 Reading source template: {source_path}")
    with open(source_path, "r") as f:
        source_str = f.read()

    themes_dir = os.path.join(script_dir, "themes")
    os.makedirs(themes_dir, exist_ok=True)

    # 2. CLEAN UP OLD FILES (dark/, light/, and generated theme files)
    for old_dir in ["dark", "light"]:
        odir = os.path.join(script_dir, old_dir)
        if os.path.isdir(odir):
            import shutil
            shutil.rmtree(odir)
            print(f"🗑️  Removed {old_dir}/ directory")

    # Remove generated files in themes/ to avoid duplicates, but keep the template source.
    for f in os.listdir(themes_dir):
        if f == template_filename:
            continue
        if f.startswith("color-sea-") and f.endswith(".json"):
            os.remove(os.path.join(themes_dir, f))

    # 3. GENERATE THEMES
    print(f"\n🎨 Generating {DISPLAY_NAME} themes...")
    generated_themes = []

    for color_name, spec in THEME_SPECS.items():
        theme_label = f"{DISPLAY_NAME} {color_name}"
        filename    = f"color-sea-{color_name.lower()}.json"
        filepath    = os.path.join(themes_dir, filename)
        light_accent = LIGHT_ACCENT_COLORS.get(color_name)

        print(f"  → {theme_label}")
        theme_json, metrics = generate_theme(source_str, theme_label, spec, light_accent)
        
        with open(filepath, "w") as f:
            f.write(theme_json)

        print(
            "     "
            f"surface={metrics['surface_ratio']:.3f} "
            f"selection={metrics['selection_ratio']:.3f} "
            f"editor-fg={metrics['editor_fg_ratio']:.3f} "
            f"info={metrics['info_ratio']:.3f}"
        )
        
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

    # Only include generated themes (the template source is excluded)
    pkg["contributes"]["themes"] = generated_themes

    with open(pkg_path, "w") as f:
        json.dump(pkg, f, indent=2)
        f.write("\n")

    print(f"\n📦 Updated package.json:")
    print(f"   Name: {pkg['name']}")
    print(f"   Display Name: {pkg['displayName']}")
    print(f"   Publisher: {pkg['publisher']}")
    print(f"   Themes: {len(generated_themes)}")

    print("\n🎉 Generation complete! Ready to package.")

if __name__ == "__main__":
    main()
