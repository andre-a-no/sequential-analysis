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
TEXT = re.compile(r"^```text\n(.*?)^```", re.S | re.M)
LINK = re.compile(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)")


def translations():
    """(folder, language) of each translation of the user guide, from mkdocs.yml."""
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    return re.findall(r"^    - \{code: ([\w-]+), lang: ([\w-]+),", nav, re.M)


def is_translation(page):
    parts = page.relative_to(ROOT / "docs").parts
    return len(parts) > 1 and parts[0] in {code for code, _ in translations()}


def check_translation(code, lang=None):
    """What is wrong with the translation of the user guide in docs/<code>/guide; empty if nothing.

    A translation keeps the original's code and outputs exactly, links to
    the same places (one level further up for pages outside the guide),
    names its language in its front matter and says, under its title,
    which English page it translates.
    """
    lang = lang or dict(translations())[code]
    problems = []
    for original in sorted((ROOT / "docs" / "guide").glob("*.md")):
        page = ROOT / "docs" / code / "guide" / original.name
        where = f"{code}/guide/{original.name}"
        if not page.exists():
            problems.append(f"{where}: missing")
            continue
        text, source = page.read_text(encoding="utf-8"), original.read_text(encoding="utf-8")
        match = FRONT_MATTER.match(text)
        if match is None:
            problems.append(f"{where}: no front matter")
            continue
        meta = dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)
        if not meta.get("description", "").strip():
            problems.append(f"{where}: no description")
        if meta.get("language") != lang:
            problems.append(f"{where}: front matter should say language: {lang}")
        if BLOCK.findall(text) != BLOCK.findall(source):
            problems.append(f"{where}: the Python blocks differ from the original's")
        if TEXT.findall(text) != TEXT.findall(source):
            problems.append(f"{where}: the output blocks differ from the original's")
        body = text[match.end():].lstrip("\n").splitlines()
        if not body or not body[0].startswith("# "):
            problems.append(f"{where}: the title should come first")
        elif not any(f"](../../guide/{original.name})" in line for line in body[1:4] if line.startswith(">")):
            problems.append(f"{where}: under the title, a quote should link to ../../guide/{original.name}")
        expected = sorted(("../" + t if t.startswith("../") else t) for t in LINK.findall(source))
        found = sorted(t for t in LINK.findall(text) if t != f"../../guide/{original.name}")
        if found != expected:
            problems.append(f"{where}: links differ from the original's: "
                            f"missing {sorted(set(expected) - set(found))}, extra {sorted(set(found) - set(expected))}")
        for target in set(found):
            if not (page.parent / target.split("#")[0]).resolve().exists():
                problems.append(f"{where}: link to a missing file {target}")
    return problems
OPTIONAL = {"sequential_analysis.plotting": "matplotlib"}  # a page using the module needs the optional dependency


def pages():
    return sorted((ROOT / "docs").rglob("*.md"))


@unittest.skipUnless((ROOT / "docs").is_dir() and (ROOT / "mkdocs.yml").exists(), "the documentation is not here")
class Documentation(unittest.TestCase):
    def test_every_python_block_runs(self):
        for page in pages():
            if is_translation(page):
                continue  # its code is the original's (test_translations_match_the_original)
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
            if not is_translation(page):  # the translations are reached through the language selector
                self.assertIn(str(page.relative_to(ROOT / "docs")), nav)

    def test_translations_match_the_original(self):
        for code, lang in translations():
            with self.subTest(language=code):
                self.assertEqual(check_translation(code, lang), [])

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
        for code, _ in translations():
            self.assertIn(f"{code}/guide/", urls)
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
