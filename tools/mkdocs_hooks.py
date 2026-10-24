# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""MkDocs hooks: the package version, the translations of the guide, and llms-full.txt.

The user guide is translated into the languages listed under
`extra.translations` in mkdocs.yml, one folder per language
(docs/ru/guide/...). Each translated page names its language in its front
matter (overrides/partials/language.html then sets the page's language and
direction). The hooks give every guide page the list of its versions, for
the language selector and the hreflang links (overrides/), and point the
selector elsewhere to the guide of each language.

llms-full.txt (https://llmstxt.org) is the documentation as one Markdown
file, in the order of the navigation: the user guide, the which-method
page, the tutorials and the guides. The API reference, generated from the
docstrings, the changelog, the format specification and the speed tables
are left out; llms.txt links to them. Snippet includes are resolved,
front matter is dropped and links within the site become absolute URLs, so
that every part of the file stands on its own.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = "guide/"
LEFT_OUT = ("reference/", "changelog.md", "spec.md", "performance.md")
SNIPPET = re.compile(r'^--8<-- "([^":]+)(?::([\w-]+))?"\s*$', re.M)
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)
LINK = re.compile(r"\]\((?!https?:|#|mailto:)([^)\s#]+)(#[^)\s]*)?\)")
API = re.compile(r"^::: (\S+)\n(?:[ \t]+.*\n)*", re.M)  # mkdocstrings: generated on the site only


def version() -> str:
    text = (ROOT / "src" / "sequential_analysis" / "version.py").read_text(encoding="utf-8")
    return re.search(r'__version__ = "([^"]+)"', text).group(1)


def translations(config) -> list[dict]:
    return config["extra"].get("translations", [])


def on_config(config):
    config.extra["version"] = version()
    config.extra["alternate"] = [{"name": "English", "link": GUIDE, "lang": "en"}] + [
        {"name": t["name"], "link": f"{t['code']}/{GUIDE}", "lang": t["lang"]} for t in translations(config)]
    return config


def original(src_uri: str, config) -> str | None:
    """The English guide page that `src_uri` is or translates; None outside the guide."""
    for t in translations(config):
        prefix = f"{t['code']}/"
        if src_uri.startswith(prefix + GUIDE):
            return src_uri[len(prefix):]
    return src_uri if src_uri.startswith(GUIDE) else None


def on_page_context(context, page, config, nav):
    key = original(page.file.src_uri, config)
    if key is not None:
        versions = [{"name": "English", "link": page_url(key), "lang": "en"}]
        for t in translations(config):
            path = f"{t['code']}/{key}"
            if (Path(config["docs_dir"]) / path).exists():
                versions.append({"name": t["name"], "link": page_url(path), "lang": t["lang"]})
        if len(versions) > 1:
            page.meta["alternates"] = versions
    return context


def page_url(path: str) -> str:
    """The site-relative URL of a page: directory URLs, as MkDocs builds them."""
    if path == "index.md":
        return ""
    if path.endswith("/index.md"):
        return path[:-len("index.md")]
    return path[:-len(".md")] + "/"


def _snippet(match: re.Match) -> str:
    text = (ROOT / match.group(1)).read_text(encoding="utf-8")
    section = match.group(2)
    if section is None:
        return text
    start = text.index(f"<!-- --8<-- [start:{section}] -->")
    end = text.index(f"<!-- --8<-- [end:{section}] -->")
    return text[text.index("\n", start) + 1:end]


def page_text(path: str, site_url: str) -> str:
    """One page as stand-alone Markdown: snippets resolved, no front matter, absolute links."""
    text = FRONT_MATTER.sub("", (ROOT / "docs" / path).read_text(encoding="utf-8"))
    text = SNIPPET.sub(_snippet, text)
    text = API.sub(lambda m: f"The API of `{m.group(1)}` is generated from its docstrings on the site.\n", text)
    folder = posixpath.dirname(path)

    def absolute(match: re.Match) -> str:
        target = posixpath.normpath(posixpath.join(folder, match.group(1)))
        url = page_url(target) if target.endswith(".md") else target
        return f"]({site_url}{url}{match.group(2) or ''})"

    return LINK.sub(absolute, text).strip() + "\n"


def nav_pages(nav) -> list[str]:
    pages: list[str] = []
    for item in nav:
        value = next(iter(item.values())) if isinstance(item, dict) else item
        if isinstance(value, list):
            pages += nav_pages(value)
        elif isinstance(value, str) and value.endswith(".md"):
            pages.append(value)
    return pages


def llms_full(config) -> str:
    site_url = config["site_url"]
    parts = [f"# {config['site_name']} {version()}: full documentation\n\n> {config['site_description']}\n\n"
             f"Source: {config['repo_url']}. Documentation: {site_url}. The API reference is at "
             f"{site_url}reference/run/ and the following pages.\n"]
    for path in nav_pages(config["nav"]):
        if not path.startswith(LEFT_OUT) and path not in LEFT_OUT:
            parts.append(f"\n<!-- {site_url}{page_url(path)} -->\n\n" + page_text(path, site_url))
    return "".join(parts)


def on_post_build(config):
    Path(config["site_dir"], "llms-full.txt").write_text(llms_full(config), encoding="utf-8")
