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
            any("splot-runtime" in dependency and "github.com/mikolaj92/splot" in dependency for dependency in dependencies),
            dependencies,
        )
        self.assertFalse(
            any(dependency == "splot>=0.1.0" or dependency.startswith("splot==") for dependency in dependencies),
            dependencies,
        )


if __name__ == "__main__":
    unittest.main()
