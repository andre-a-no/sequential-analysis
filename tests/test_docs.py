# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""The Python code of the documentation runs: each page's blocks in order, in one namespace."""
import contextlib
import importlib.util
import io
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r"^```python\n(.*?)^```", re.S | re.M)
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
OPTIONAL = {"sequential_analysis.plotting": "matplotlib"}  # a page using the module needs the optional dependency


def pages():
    return sorted((ROOT / "docs").rglob("*.md"))


@unittest.skipUnless((ROOT / "docs").is_dir() and (ROOT / "mkdocs.yml").exists(), "the documentation is not here")
class Documentation(unittest.TestCase):
    def test_every_python_block_runs(self):
        for page in pages():
            blocks = BLOCK.findall(page.read_text(encoding="utf-8"))
            if not blocks:
                continue
            with self.subTest(page=str(page.relative_to(ROOT))):
                needed = [dep for module, dep in OPTIONAL.items() if any(module in block for block in blocks)]
                missing = [dep for dep in needed if importlib.util.find_spec(dep) is None]
                if missing:
                    self.skipTest(f"needs {', '.join(missing)}")
                if "matplotlib" in needed:
                    import matplotlib

                    matplotlib.use("Agg")  # no windows
                namespace: dict = {"__name__": "__docs__"}
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    for block in blocks:
                        exec(compile(block, str(page), "exec"), namespace)
                if "matplotlib.pyplot" in sys.modules:
                    sys.modules["matplotlib.pyplot"].close("all")
                self.assertTrue(output.getvalue().strip(), "a tutorial should show its results")

    def test_navigation_lists_every_page(self):
        nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        for page in pages():
            self.assertIn(str(page.relative_to(ROOT / "docs")), nav)

    def test_guide_pages_describe_themselves(self):
        """Each page of the user guide has a description for search results and its question as the title."""
        for page in sorted((ROOT / "docs" / "guide").glob("*.md")):
            with self.subTest(page=page.name):
                text = page.read_text(encoding="utf-8")
                match = FRONT_MATTER.match(text)
                self.assertIsNotNone(match, "no front matter")
                self.assertTrue(match.group(1).startswith("description: "))
                self.assertLess(len(match.group(1)), 400)
                self.assertRegex(text[match.end():], r"\A\n?# \S")

    def test_llms_txt_links_to_pages_that_exist(self):
        text = (ROOT / "docs" / "llms.txt").read_text(encoding="utf-8")
        site = "https://andre-a-no.github.io/sequential-analysis/"
        urls = re.findall(re.escape(site) + r"([^)\s]*)", text)
        self.assertGreater(len(urls), 20)
        for url in urls:
            if url == "llms-full.txt":
                continue
            with self.subTest(url=url):
                path = url.rstrip("/")
                candidates = [ROOT / "docs" / "index.md"] if not path else \
                    [ROOT / "docs" / (path + ".md"), ROOT / "docs" / path / "index.md"]
                self.assertTrue(any(c.exists() for c in candidates), url)

    @unittest.skipIf(importlib.util.find_spec("yaml") is None, "needs PyYAML to read mkdocs.yml")
    @unittest.skipUnless(all((ROOT / f).exists() for f in ("README.md", "src", "tools/mkdocs_hooks.py")),
                         "the pages include the README, the hooks read the version")
    def test_llms_full_stands_on_its_own(self):
        import yaml

        sys.path.insert(0, str(ROOT / "tools"))
        try:
            import mkdocs_hooks
        finally:
            sys.path.pop(0)
        config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
        text = mkdocs_hooks.llms_full(config)
        for page in sorted((ROOT / "docs" / "guide").glob("*.md")):
            self.assertIn(config["site_url"] + mkdocs_hooks.page_url("guide/" + page.name), text)
        self.assertNotIn("--8<--", text)
        self.assertNotIn("\n::: ", text)
        self.assertIsNone(re.search(r"\]\((?!https?:|#|mailto:)", text), "a relative link is left")


if __name__ == "__main__":
    unittest.main()
