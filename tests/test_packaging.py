import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_splot_is_not_pinned_to_a_sibling_checkout(self):
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
        splot_source = sources.get("splot") or sources.get("splot-runtime") or {}

        self.assertNotIn("path", splot_source)

        dependencies = pyproject["project"]["dependencies"]
        self.assertTrue(
            any("splot @ git+https://github.com/mikolaj92/splot.git@v0.4.1" == dependency for dependency in dependencies),
            dependencies,
        )
        self.assertFalse(any("@main" in dependency for dependency in dependencies), dependencies)

    def test_profile_is_toml_only(self):
        profile_dir = ROOT / "src" / "showmetheplayer" / "profiles" / "player-director"
        self.assertTrue((profile_dir / "profile.toml").is_file())
        self.assertFalse(list(profile_dir.glob("*.yaml")))

    def test_lokay_runs_the_canonical_product_gate(self):
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(pyproject["tool"]["lokay"]["test"], "uv run --extra dev pytest -q")


if __name__ == "__main__":
    unittest.main()
