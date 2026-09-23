#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=11,<13", "picosvg>=0.23,<0.24", "resvg-py>=0.5,<0.6"]
# ///
"""Build and inspect a local macOS icon bundle from standalone vector artwork."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image, ImageCms
from picosvg.svg import SVG
from picosvg.svg_transform import Affine2D
import resvg_py


NS = "http://www.w3.org/2000/svg"
BASELINE = "2026-09-23"
SLOTS = {
    (16, 1): b"icp4", (16, 2): b"ic11", (32, 1): b"icp5",
    (32, 2): b"ic12", (128, 1): b"ic07", (128, 2): b"ic13",
    (256, 1): b"ic08", (256, 2): b"ic14", (512, 1): b"ic09",
    (512, 2): b"ic10",
}
ICC = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


class IconSVG(SVG):
    @property
    def tolerance(self):
        # Font-oriented defaults distort small circular strokes when enlarged.
        box = self.view_box()
        return min(super().tolerance, min(box.w, box.h) / 100000)

    def _stroke(self, shape):
        # Skia's stroker uses absolute tolerances. Work at app-icon resolution
        # so a 24-unit Lucide circle does not become visibly squared off.
        box = self.view_box()
        factor = max(1, 1024 / max(box.w, box.h))
        enlarged = shape.apply_transform(Affine2D.identity().scale(factor))
        enlarged.stroke_width *= factor
        enlarged.stroke_dashoffset *= factor
        if enlarged.stroke_dasharray != "none":
            enlarged.stroke_dasharray = " ".join(
                str(float(value) * factor)
                for value in re.split(r"[,\s]+", enlarged.stroke_dasharray.strip()))
        for path in super()._stroke(enlarged):
            yield path.apply_transform(Affine2D.identity().scale(1 / factor))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_svg(text):
    """Accept self-contained vector geometry, without resolving external content."""
    require("<!DOCTYPE" not in text.upper() and "<!ENTITY" not in text.upper(),
            "SVG DTDs and entities are unsupported")
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    root = etree.fromstring(text.encode(), parser)
    allowed = {"svg", "g", "defs", "path", "circle", "ellipse", "rect", "line",
               "polyline", "polygon", "clipPath", "use", "linearGradient",
               "radialGradient", "stop", "title", "desc"}
    require(etree.QName(root).localname == "svg", "Input is not an SVG")
    for node in root.iter():
        if not isinstance(node.tag, str):
            continue
        require(etree.QName(node).localname in allowed,
                f"Unsupported SVG element: {etree.QName(node).localname}")
        for key, value in node.attrib.items():
            local = etree.QName(key).localname.lower()
            require(not local.startswith("on"), "SVG event handlers are unsupported")
            if local == "href":
                require(value.startswith("#"), "SVG resources must be internal")
            for ref in re.findall(r"url\s*\((.*?)\)", value, re.I):
                require(ref.strip().strip("\"'").startswith("#"),
                        "SVG resources must be internal")
    return root


def color(value):
    require(re.fullmatch(r"#[0-9a-fA-F]{6}", value), "Colors must use #RRGGBB")
    return value.upper()


def tagged(value):
    return "srgb:" + ",".join(f"{int(value[i:i + 2], 16) / 255:.5f}"
                              for i in (1, 3, 5)) + ",1.00000"


def normalized(text, ink, fraction, stroke_width=None):
    root = read_svg(text)
    for node in root.iter():
        for key, value in list(node.attrib.items()):
            node.set(key, re.sub("currentcolor", ink, value, flags=re.I))
    if stroke_width is not None:
        root.set("stroke-width", str(stroke_width))
    svg = IconSVG(root)
    box = svg.view_box()
    require(box is not None and box.w > 0 and box.h > 0, "SVG needs a positive viewBox")
    require(all(math.isfinite(x) for x in (box.x, box.y, box.w, box.h)),
            "SVG viewBox must be finite")
    outlined = svg.topicosvg(ndigits=6, inplace=True)
    shape_root = etree.fromstring(outlined.tostring().encode())
    scale = 1024 * fraction / max(box.w, box.h)
    x = (1024 - box.w * scale) / 2 - box.x * scale
    y = (1024 - box.h * scale) / 2 - box.y * scale
    content = "".join(etree.tostring(n, encoding="unicode") for n in shape_root)
    placed = wrap(f'<g transform="translate({x} {y}) scale({scale})">{content}</g>')
    result = SVG.fromstring(placed).topicosvg(ndigits=4).tostring()
    require("stroke=" not in result, "Stroke expansion failed")
    return result


def wrap(content):
    return (f'<svg xmlns="{NS}" width="1024" height="1024" '
            f'viewBox="0 0 1024 1024">{content}</svg>')


def inner(svg):
    return "".join(etree.tostring(n, encoding="unicode") for n in read_svg(svg))


def flat_svg(foreground, args, logical_size=512):
    inset = args.flat_inset
    side = 1024 - 2 * inset
    optical = 1.08 if logical_size <= 32 else 1
    background_id = "app-background"
    existing_ids = {node.get("id") for node in read_svg(foreground).iter()}
    while background_id in existing_ids:
        background_id += "-background"
    background = f'''<defs><linearGradient id="{background_id}" x1="0.25" y1="0"
        x2="0.75" y2="1"><stop stop-color="{args.background[0]}"/>
        <stop offset="1" stop-color="{args.background[1]}"/></linearGradient></defs>
        <rect x="{inset}" y="{inset}" width="{side}" height="{side}"
        rx="{args.flat_radius}" fill="url(#{background_id})"/>'''
    artwork = (f'<g transform="translate({inset} {inset}) scale({side / 1024})">'
               f'<g transform="translate(512 512) scale({optical}) translate(-512 -512)">'
               f'{inner(foreground)}</g></g>')
    return wrap(background + artwork)


def render(svg, size, path, template=False):
    oversample = 4 if size <= 128 else 2
    raw = resvg_py.svg_to_bytes(svg_string=svg, width=size * oversample,
                                height=size * oversample, skip_system_fonts=True)
    with Image.open(io.BytesIO(raw)) as source:
        image = source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    require(image.getchannel("A").getbbox() is not None, "Artwork renders empty")
    if template:
        black = Image.new("RGBA", image.size, (0, 0, 0, 0))
        black.putalpha(image.getchannel("A"))
        image = black
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True, icc_profile=ICC)


def gradient(colors):
    return {"linear-gradient": [tagged(c) for c in colors],
            "orientation": {"start": {"x": .25, "y": 0}, "stop": {"x": .75, "y": 1}}}


def native_document(args):
    dark = args.dark_background or [
        "#" + "".join(f"{round(int(c[i:i + 2], 16) * .5):02x}" for i in (1, 3, 5))
        for c in args.background]
    return {
        "features": ["refractivity", "specular-location"],
        "fill-specializations": [
            {"value": gradient(args.background)},
            {"appearance": "dark", "value": gradient(dark)},
            {"appearance": "tinted", "value": {"automatic-gradient": "gray:0.72000,1.00000"}},
        ],
        "groups": [{
            "name": "Glass Symbol", "lighting": "individual", "blur-material": .12,
            "refractivity": {"enabled": True, "depth": .15, "strength": .25},
            "specular": "inside", "shadow": {"kind": "neutral", "opacity": .22},
            "translucency": {"enabled": True, "value": .25},
            "layers": [{"name": args.name, "image-name": "foreground.svg", "glass": True,
                        "fill-specializations": [
                            {"value": "automatic"},
                            {"appearance": "tinted", "value": {"solid": "gray:0.96000,1.00000"}},
                        ],
                        "position": {"scale": 1, "translation-in-points": [0, 0]}}],
        }],
        "supported-platforms": {"squares": ["macOS"]},
    }


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def png_name(size, scale):
    return f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"


def check_png(path, expected):
    with Image.open(path) as image:
        image.load()
        require(image.size == (expected, expected), f"Wrong dimensions: {path.name}")
        require(image.mode == "RGBA", f"Missing RGBA: {path.name}")
        require(bool(image.info.get("icc_profile")), f"Missing color profile: {path.name}")
        require(image.getchannel("A").getbbox() is not None, f"Empty artwork: {path.name}")
        require(image.getpixel((0, 0))[3] == 0, f"Opaque outside margin: {path.name}")


def asset_names(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "image-name":
                yield child
            elif key == "image-name-specializations":
                for variant in child:
                    if isinstance(variant.get("value"), str):
                        yield variant["value"]
            else:
                yield from asset_names(child)
    elif isinstance(value, list):
        for child in value:
            yield from asset_names(child)


def verify(folder):
    folder = folder.resolve()
    metadata = json.loads((folder / "BUILD.json").read_text())
    name = metadata["name"]
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name), "Invalid asset name")
    require(bool((folder / "LICENSE.txt").read_text().strip()), "Empty license")
    original = folder / "Source" / "original.svg"
    require(hashlib.sha256(original.read_bytes()).hexdigest() == metadata["source_sha256"],
            "Original source changed without updating provenance")
    read_svg((folder / "Source" / "foreground.svg").read_text())
    native = folder / f"{name}.icon"
    document = json.loads((native / "icon.json").read_text())
    names = list(asset_names(document))
    require(bool(names), "Native document has no artwork references")
    for filename in names:
        path = (native / "Assets" / filename).resolve()
        require(path.is_relative_to((native / "Assets").resolve()) and path.is_file(),
                f"Missing or invalid native asset: {filename}")
        if path.suffix.lower() == ".svg":
            root = read_svg(path.read_text())
            box = SVG.fromstring(etree.tostring(root, encoding="unicode")).view_box()
            require(box is not None and box.w == 1024 and box.h == 1024,
                    f"Native SVG must use a 1024 canvas: {filename}")
            rendered = resvg_py.svg_to_bytes(svg_string=etree.tostring(root, encoding="unicode"),
                                             width=1024, height=1024, skip_system_fonts=True)
            with Image.open(io.BytesIO(rendered)) as image:
                require(image.convert("RGBA").getchannel("A").getbbox() is not None,
                        f"Native SVG renders empty: {filename}")
    catalog = folder / "AppIcon.appiconset"
    manifest = json.loads((catalog / "Contents.json").read_text())
    entries = manifest["images"]
    require(len(entries) == 10, "AppIcon catalog needs all 10 macOS slots")
    seen = set()
    for entry in entries:
        dimensions = entry["size"].split("x")
        require(len(dimensions) == 2 and dimensions[0] == dimensions[1], "Non-square slot")
        slot = (int(dimensions[0]), int(entry["scale"].removesuffix("x")))
        require(entry["idiom"] == "mac" and slot in SLOTS and slot not in seen,
                f"Invalid or duplicated AppIcon slot: {slot}")
        seen.add(slot)
        require(Path(entry["filename"]).name == entry["filename"], "Invalid PNG filename")
        check_png(catalog / entry["filename"], slot[0] * slot[1])
    check_png(folder / f"{name}-1024.png", 1024)
    data = (folder / f"{name}.icns").read_bytes()
    require(data[:4] == b"icns" and len(data) >= 8, "Invalid ICNS header")
    require(struct.unpack(">I", data[4:8])[0] == len(data), "Invalid ICNS length")
    expected = {kind: size * scale for (size, scale), kind in SLOTS.items()}
    seen, offset = set(), 8
    while offset < len(data):
        require(offset + 8 <= len(data), "Truncated ICNS entry")
        kind, length = data[offset:offset + 4], struct.unpack(">I", data[offset + 4:offset + 8])[0]
        require(kind in expected and kind not in seen, "Unexpected or duplicate ICNS entry")
        require(length > 8 and offset + length <= len(data), "Truncated ICNS payload")
        with Image.open(io.BytesIO(data[offset + 8:offset + length])) as image:
            image.load()
            require(image.size == (expected[kind], expected[kind]), "ICNS dimensions mismatch")
        seen.add(kind)
        offset += length
    require(seen == set(expected), "ICNS representations missing")
    with Image.open(folder / f"{name}.icns") as image:
        image.load()
        require(image.size == (1024, 1024), "ICNS master does not decode")
    for imageset in (folder / "MenuBar").glob("*.imageset"):
        doc = json.loads((imageset / "Contents.json").read_text())
        require(doc["properties"]["template-rendering-intent"] == "template", "Not a template")
        require({x["scale"] for x in doc["images"]} == {"1x", "2x"}, "Missing menu scale")
        for entry in doc["images"]:
            check_png(imageset / entry["filename"], 18 * int(entry["scale"][0]))
    return {"name": name, "macos_slots": 10, "icns_representations": 10,
            "native_validation": metadata["native_validation"]}


def pack(folder):
    result = verify(folder)
    archive = folder.with_name(folder.name + ".zip")
    with tempfile.NamedTemporaryFile(prefix=".icon-bundle-", suffix=".zip",
                                     dir=archive.parent, delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
            for path in sorted(folder.rglob("*")):
                require(not path.is_symlink(), "Refusing to archive a symbolic link")
                if path.is_file():
                    zipped.write(path, Path(folder.name) / path.relative_to(folder))
        with zipfile.ZipFile(temp_path) as zipped:
            require(zipped.testzip() is None, "Archive integrity check failed")
        temp_path.replace(archive)
    finally:
        temp_path.unlink(missing_ok=True)
    return {**result, "archive": str(archive)}


def build(args):
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.name),
            "Name must be an ASCII asset name, up to 64 letters/digits/hyphens/underscores")
    require(.2 <= args.symbol_fraction <= .85, "Symbol fraction must be between .2 and .85")
    require(0 < args.flat_inset < 256, "Flat inset must be between 0 and 256")
    require(0 < args.flat_radius <= (1024 - 2 * args.flat_inset) / 2, "Invalid flat radius")
    if args.stroke_width is not None:
        require(math.isfinite(args.stroke_width) and args.stroke_width > 0, "Invalid stroke width")
    source = args.svg.read_text(encoding="utf-8")
    original = (args.original_svg or args.svg).read_bytes()
    read_svg(original.decode("utf-8"))
    require(bool(args.license.read_text().strip()), "Provide the actual source license or notice")
    foreground = normalized(source, args.foreground, args.symbol_fraction, args.stroke_width)
    folder = args.output / args.name
    require(not folder.exists() and not folder.with_name(folder.name + ".zip").exists(),
            "Output already exists; use a fresh name/directory to preserve existing work")
    folder.mkdir(parents=True)
    (folder / "Source").mkdir()
    (folder / "Source" / "original.svg").write_bytes(original)
    (folder / "Source" / "input.svg").write_text(source, encoding="utf-8")
    (folder / "Source" / "foreground.svg").write_text(foreground, encoding="utf-8")
    shutil.copyfile(args.license, folder / "LICENSE.txt")
    native = folder / f"{args.name}.icon"
    (native / "Assets").mkdir(parents=True)
    (native / "Assets" / "foreground.svg").write_text(foreground, encoding="utf-8")
    save_json(native / "icon.json", native_document(args))
    catalog = folder / "AppIcon.appiconset"
    entries, chunks = [], []
    for (size, scale), kind in SLOTS.items():
        filename = png_name(size, scale)
        render(flat_svg(foreground, args, size), size * scale, catalog / filename)
        entries.append({"filename": filename, "idiom": "mac", "size": f"{size}x{size}", "scale": f"{scale}x"})
        payload = (catalog / filename).read_bytes()
        chunks.append(kind + struct.pack(">I", len(payload) + 8) + payload)
    save_json(catalog / "Contents.json", {"images": entries, "info": {"author": "xcode", "version": 1}})
    payload = b"".join(chunks)
    (folder / f"{args.name}.icns").write_bytes(b"icns" + struct.pack(">I", len(payload) + 8) + payload)
    shutil.copyfile(catalog / png_name(512, 2), folder / f"{args.name}-1024.png")
    (folder / "Source" / "flattened.svg").write_text(flat_svg(foreground, args), encoding="utf-8")
    if args.menu_bar:
        menu = folder / "MenuBar" / f"{args.name}Status.imageset"
        artwork = normalized(source, args.foreground, .94, args.stroke_width)
        entries = []
        for scale in (1, 2):
            filename = f"status{'@2x' if scale == 2 else ''}.png"
            render(artwork, 18 * scale, menu / filename, template=True)
            entries.append({"idiom": "universal", "scale": f"{scale}x", "filename": filename})
        save_json(menu / "Contents.json", {"images": entries, "info": {"author": "xcode", "version": 1},
                  "properties": {"template-rendering-intent": "template"}})
    save_json(folder / "BUILD.json", {
        "name": args.name, "source_url": args.source_url, "source_sha256": hashlib.sha256(original).hexdigest(),
        "specification_baseline": BASELINE,
        "native_validation": {"opened": "not_run", "preview": "not_run", "xcode_build": "not_run"},
        "static_rendering": "Vector-derived fallback, not a native Liquid Glass preview",
    })
    (folder / "README.md").write_text(f"""# {args.name}

Open `{args.name}.icon` with the current Apple Icon Composer. Keep this directory
package intact. Add it to the Xcode Project navigator and app target; set the
target's App Icon name to `{args.name}` (without the extension).

`AppIcon.appiconset`, `{args.name}.icns`, and the 1024 px PNG are static alternatives.
The catalog contains 16, 32, 128, 256, and 512 pt at both 1x and 2x. Every size was
rendered from vectors, with sRGB profiles and transparent outside margins. Small
16/32 pt representations use a modest optical scale adjustment. The flattened
enclosure is an adjustable approximation, not Apple's exact current mask.

`Source/foreground.svg` is the outlined, normalized artwork; `flattened.svg` is
the static composition. `input.svg` preserves the supplied artwork and
`original.svg` preserves the original supplied source, or input when no separate
original was provided. Keep `LICENSE.txt` with distributed third-party notices.
Source URL and hash, specification baseline, and validation status are in
`BUILD.json`. Optional menu-bar images use 18 pt template rendering at 1x/2x.

Native glass is configured in the document. Distinct refraction and inside/outside
highlights require macOS 27 or later; recheck current Apple guidance before release.
The system renders the native enclosure and Retina sizes from the vector document.

This package was authored programmatically. Native Icon Composer opening,
preview, and Xcode compilation have not been performed by this script. If a
local Mac is available, record actual results in BUILD.json and update this
paragraph before repacking; otherwise skip native preview and deliver the files.
""", encoding="utf-8")
    return pack(folder)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build", help="Create a new icon directory and ZIP")
    create.add_argument("--name", required=True)
    create.add_argument("--svg", type=Path, required=True)
    create.add_argument("--original-svg", type=Path)
    create.add_argument("--license", type=Path, required=True)
    create.add_argument("--source-url", required=True)
    create.add_argument("--output", type=Path, required=True)
    create.add_argument("--background", type=color, nargs=2, default=["#497B77", "#214E51"])
    create.add_argument("--dark-background", type=color, nargs=2)
    create.add_argument("--foreground", type=color, default="#EEF5EF")
    create.add_argument("--stroke-width", type=float, help="Override inherited root stroke width")
    create.add_argument("--symbol-fraction", type=float, default=.625)
    create.add_argument("--flat-inset", type=float, default=100)
    create.add_argument("--flat-radius", type=float, default=186)
    create.add_argument("--menu-bar", action="store_true")
    for verb in ("verify", "pack"):
        commands.add_parser(verb).add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = build(args) if args.command == "build" else (
            verify(args.directory) if args.command == "verify" else pack(args.directory))
    except (ValueError, OSError, KeyError, etree.XMLSyntaxError, json.JSONDecodeError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
