# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=11,<13", "picosvg>=0.23,<0.24", "resvg-py>=0.5,<0.6"]
# ///
"""Regression checks for geometry fidelity and delivered icon integrity."""

import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from PIL import Image, ImageChops, ImageStat
import resvg_py
import build_icon as icons


CIRCLE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
fill="none" stroke="currentColor" stroke-width="1.65">
<circle cx="12" cy="12" r="3"/></svg>'''


class IconBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        source = cls.root / "circle.svg"
        source.write_text(CIRCLE)
        license_file = cls.root / "LICENSE.txt"
        license_file.write_text("Self-authored circle geometry for this local test.\n")
        cls.args = SimpleNamespace(
            name="Circle", svg=source, original_svg=None, license=license_file,
            source_url="https://example.com/circle.svg", output=cls.root,
            background=["#AB761C", "#66400A"], dark_background=None,
            foreground="#FFF8E7", stroke_width=None, symbol_fraction=.625,
            flat_inset=100, flat_radius=186, menu_bar=True)
        icons.build(cls.args)
        cls.bundle = cls.root / "Circle"

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def copied_bundle(self, name):
        target = self.root / name
        shutil.copytree(self.bundle, target)
        return target

    def test_outlining_preserves_small_circle_geometry(self):
        outlined = icons.normalized(CIRCLE, "#FFFFFF", .625)
        original = CIRCLE.replace("currentColor", "#FFFFFF").replace(
            "viewBox=", 'x="192" y="192" width="640" height="640" viewBox=')

        def alpha(svg):
            data = resvg_py.svg_to_bytes(svg_string=svg, width=1024, height=1024)
            return Image.open(io.BytesIO(data)).convert("RGBA").getchannel("A")

        before, after = alpha(icons.wrap(original)), alpha(outlined)
        self.assertEqual(before.getbbox(), after.getbbox())
        error = ImageStat.Stat(ImageChops.difference(before, after)).mean[0]
        self.assertLess(error, .1, "Stroke outlining visibly changed the original circle")

    def test_retina_and_icns_representations_are_delivered(self):
        report = icons.verify(self.bundle)
        self.assertEqual(report["macos_slots"], 10)
        with Image.open(self.bundle / "Circle.icns") as image:
            image.load()
            self.assertEqual(image.size, (1024, 1024))
            self.assertEqual(len(image.info["sizes"]), 10)
        metadata = json.loads((self.bundle / "BUILD.json").read_text())
        self.assertEqual(metadata["native_validation"]["preview"], "not_run")

    def test_empty_native_layer_is_rejected(self):
        folder = self.copied_bundle("Empty")
        (folder / "Circle.icon" / "Assets" / "foreground.svg").write_text(icons.wrap(""))
        with self.assertRaisesRegex(ValueError, "renders empty"):
            icons.verify(folder)

    def test_wrong_retina_image_size_is_rejected(self):
        folder = self.copied_bundle("WrongSize")
        catalog = folder / "AppIcon.appiconset"
        shutil.copyfile(catalog / "icon_16x16.png", catalog / "icon_16x16@2x.png")
        with self.assertRaisesRegex(ValueError, "Wrong dimensions"):
            icons.verify(folder)

    def test_repack_retains_new_files_and_native_status(self):
        folder = self.copied_bundle("Repacked")
        icons.pack(folder)
        (folder / "review-note.txt").write_text("Native preview was skipped.\n")
        result = icons.pack(folder)
        with zipfile.ZipFile(result["archive"]) as archive:
            self.assertIn("Repacked/review-note.txt", archive.namelist())
        self.assertEqual(result["native_validation"]["preview"], "not_run")

    def test_existing_output_is_preserved(self):
        master = self.bundle / "Circle-1024.png"
        before = master.read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            icons.build(self.args)
        self.assertEqual(master.read_bytes(), before)

    def test_external_svg_resources_are_rejected(self):
        source = CIRCLE.replace('<circle cx="12" cy="12" r="3"/>',
                                '<use href="https://example.com/art.svg#logo"/>')
        with self.assertRaisesRegex(ValueError, "must be internal"):
            icons.normalized(source, "#FFFFFF", .625)


if __name__ == "__main__":
    unittest.main()
