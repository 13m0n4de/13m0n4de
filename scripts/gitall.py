#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///

import re
from pathlib import Path

import requests

CLASSES = ("bg", "mut", "wm", "wl", "l0", "l1", "l2", "l3", "l4")
RAMP = (0.4, 0.62, 0.82, 1.0)

FLAVORS = {
    "light": {
        "base": "#eff1f5",
        "mantle": "#e6e9ef",
        "surface0": "#ccd0da",
        "overlay1": "#8c8fa1",
        "subtext0": "#6c6f85",
        "teal": "#179299",
    },
    "dark": {
        "base": "#24273a",
        "mantle": "#1e2030",
        "surface0": "#363a4f",
        "overlay1": "#8087a2",
        "subtext0": "#a5adcb",
        "teal": "#8bd5ca",
    },
}


def blend(a, b, t):
    rgb = zip(bytes.fromhex(a[1:]), bytes.fromhex(b[1:]), strict=True)
    return f"#{''.join(f'{round(x + (y - x) * t):02x}' for x, y in rgb)}"


def palette(flavor):
    return {
        "bg": flavor["mantle"],
        "mut": flavor["subtext0"],
        "wm": flavor["overlay1"],
        "wl": flavor["teal"],
        "l0": flavor["surface0"],
        **{
            f"l{i}": blend(flavor["base"], flavor["teal"], t)
            for i, t in enumerate(RAMP, 1)
        },
    }


def rules(colors):
    return "".join(f".gitall-heatmap .{c}{{fill:{colors[c]}}}" for c in CLASSES)


def recolor(svg, light, dark):
    css = rules(light) + "@media (prefers-color-scheme:dark){" + rules(dark) + "}"
    svg = re.sub(r"(?<=<style>).*(?=</style>)", css, svg, count=1, flags=re.S)
    return re.sub(
        r'(class="(\w+)" fill=")#[0-9a-fA-F]{6}"',
        lambda m: f'{m.group(1)}{light[m.group(2)]}"',
        svg,
    )


def main():
    resp = requests.get(
        "https://gitall.app/embed/13m0n4de.svg",
        params={
            "github": "13m0n4de",
            "gitlab": "13m0n4de",
            "gitea": "13m0n4de",
            "instance": "https://codeberg.org",
        },
    )
    resp.raise_for_status()
    svg = resp.text

    out = Path(__file__).resolve().parent.parent / "assets" / "gitall.svg"
    out.write_text(recolor(svg, palette(FLAVORS["light"]), palette(FLAVORS["dark"])))
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
