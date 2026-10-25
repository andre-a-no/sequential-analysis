# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Novikov Laboratories LLC (Kazan, Tatarstan, Russian Federation)
# Commercial licenses for use outside the AGPL: see COMMERCIAL.md
"""Write docs/llms-api.txt: the API as an AI assistant needs it to write correct code.

Assistants that write code for a library they have seen little of tend to
invent its API. This file gives them the real one in a single read:
how a procedure is called, and for every public procedure its import, its
constructor, its guarantee, its input names and its output fields, then
the signatures of the other public functions. All of it is read from the
code; the input names and output fields from one run of each procedure in
the invariant cases (tests/helpers.py). The text before the procedures,
on how the library is used and which procedure answers which question,
is tools/llms_api_preamble.md. The site publishes the file next to
llms.txt.

    python tools/make_llms_api.py           # rewrite docs/llms-api.txt
    python -m unittest tests.test_docs      # checks that it is up to date
"""
from __future__ import annotations

import dataclasses
import enum
import importlib
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import sequential_analysis  # noqa: E402
import sequential_analysis.procedures as procedures  # noqa: E402
from sequential_analysis import Recorder, Run, run_sync  # noqa: E402
from sequential_analysis.core import GUARANTEES, Procedure  # noqa: E402
from sequential_analysis.procedures import CUSUM, EMA, Gaussian, SampleRatioMismatch  # noqa: E402

OUT = ROOT / "docs" / "llms-api.txt"
SITE = "https://andre-a-no.github.io/sequential-analysis/"

# the modules whose public functions and classes are listed after the procedures, in this order
MODULES = [
    ("sequential_analysis", "running procedures on streams, checkpoints, topologies"),
    ("sequential_analysis.sources", "observations from values, files, simulations and logs"),
    ("sequential_analysis.adapters", "observations from DataFrames, SQL and Kafka"),
    ("sequential_analysis.group_sequential", "group sequential designs"),
    ("sequential_analysis.design", "optimal sequential plans and their exact operating characteristics"),
    ("sequential_analysis.planning", "power and duration by simulation"),
    ("sequential_analysis.forecasting", "fitting forecasters on a history"),
    ("sequential_analysis.garch_fit", "fitting GARCH on a history"),
    ("sequential_analysis.events", "fitting and simulating Hawkes processes"),
    ("sequential_analysis.hmm_fit", "fitting hidden Markov models on a history"),
    ("sequential_analysis.smoothing", "offline smoothing"),
    ("sequential_analysis.plotting", "plots (needs matplotlib)"),
]

PREAMBLE = (ROOT / "tools" / "llms_api_preamble.md").read_text(encoding="utf-8")  # the hand-written part


def clean(text: str) -> str:
    return re.sub(r" at 0x[0-9a-fA-F]+", "", text)


def summary(obj) -> str:
    """The first paragraph of the object's own docstring, or of its module's."""
    own = obj.__dict__.get("__doc__") if inspect.isclass(obj) else obj.__doc__
    doc = inspect.cleandoc(own or sys.modules[obj.__module__].__doc__ or "")
    text = " ".join(doc.split("\n\n")[0].split())
    return re.sub(r"[;,]? see the module docstring\.?$", ".", text)


def guarantee(cls) -> str:
    """The `guarantee` of a procedure class; a property when it depends on the configuration."""
    value = inspect.getattr_static(cls, "guarantee")
    if isinstance(value, property):
        return "depends on the configuration: " + " ".join((value.__doc__ or "").split())
    return f"{value}."


def signature(obj) -> str:
    """The call signature; for a class, its __init__'s (Python 3.8 reads a Generic class's as (*args, **kwds))."""
    try:
        if inspect.isclass(obj):
            sig = inspect.signature(obj.__init__)
            sig = sig.replace(parameters=list(sig.parameters.values())[1:])
        else:
            sig = inspect.signature(obj)
        return clean(str(sig))
    except (TypeError, ValueError):
        return "(...)"


def observed():
    """Input names and output fields of the procedures run in the invariant cases, by class name."""
    from tests.helpers import cases

    seen: dict[str, tuple[list[str], list[str]]] = {}
    for _, make, topology, delivery, observations, seed in cases():
        procedure = make()
        name = type(procedure).__name__
        if name in seen or not isinstance(procedure, Procedure):
            continue
        recorder = Recorder()
        run = Run(procedure, topology=topology(), delivery=delivery(), consumers=[recorder], seed=seed)
        run_sync(run, observations)
        if recorder.outputs and dataclasses.is_dataclass(recorder.outputs[0]):
            seen[name] = (sorted(procedure.inputs()), output_fields(recorder.outputs[0]))
    # those the cases run only inside a composite (Chain, MultipleTests)
    for procedure, x in ((CUSUM(Gaussian(1.0), 0.0, 1.0, 5.0), {"x": 0.5}), (EMA(0.1), {"x": 0.5}),
                         (SampleRatioMismatch(), {"arm": 1})):
        if type(procedure).__name__ not in seen:
            _, out = procedure.step(procedure.initial_state(), x)
            seen[type(procedure).__name__] = (sorted(procedure.inputs()), output_fields(out))
    return seen


def output_fields(output) -> list[str]:
    return [f"{f.name}: {f.type}" for f in dataclasses.fields(output)]


def default_inputs(cls) -> list[str]:
    """Input names from the constructor's defaults (`input`, `arm_input`, ...)."""
    names = []
    for name, parameter in inspect.signature(cls.__init__).parameters.items():
        if (name == "input" or name.endswith("_input")) and isinstance(parameter.default, str):
            names.append(parameter.default)
    return names


def procedure_entries() -> list[str]:
    seen = observed()
    entries = []
    for name in sorted(n for n in procedures.__all__ if inspect.isclass(getattr(procedures, n))
                       and issubclass(getattr(procedures, n), Procedure)):
        cls = getattr(procedures, name)
        inputs, fields = seen.get(name, (default_inputs(cls), []))
        lines = [f"### {name}", "", f"`{name}{signature(cls)}`", "",
                 f"- Guarantee: {guarantee(cls)}", f"- {summary(cls)}"]
        if inputs:
            lines.append("- Inputs: " + ", ".join(f"`{i}`" for i in inputs) + ".")
        if fields:
            lines.append("- Output fields: " + ", ".join(f"`{f}`" for f in fields) + ".")
        entries.append("\n".join(lines))
    return entries


def module_entries() -> list[str]:
    building_blocks = [n for n in procedures.__all__ if not (
        inspect.isclass(getattr(procedures, n)) and issubclass(getattr(procedures, n), Procedure))
        and (inspect.isclass(getattr(procedures, n)) or inspect.isfunction(getattr(procedures, n)))]
    sections = ["## sequential_analysis.procedures: families, models and helpers\n\n"
                + "\n".join(item(n, getattr(procedures, n)) for n in building_blocks)]
    for module_name, purpose in MODULES:
        module = importlib.import_module(module_name)
        if module_name == "sequential_analysis":
            names = [n for n in sequential_analysis.__all__ if not n.startswith("_")]
        else:
            names = [n for n, o in vars(module).items() if not n.startswith("_")
                     and (inspect.isfunction(o) or inspect.isclass(o)) and o.__module__ == module_name]
        items = [item(n, getattr(module, n)) for n in names
                 if inspect.isclass(getattr(module, n)) or inspect.isfunction(getattr(module, n))]
        sections.append(f"## {module_name}: {purpose}\n\n" + "\n".join(items))
    return sections


def item(name: str, obj) -> str:
    if inspect.isclass(obj) and issubclass(obj, enum.Enum):
        return f"- `{name}`: an enumeration of " + ", ".join(f"`{m.name}`" for m in obj) + "."
    return f"- `{name}{signature(obj)}`: {summary(obj)}"


def render() -> str:
    guarantees = "\n".join(f"  - `{k}`: {v}" for k, v in GUARANTEES.items())
    parts = [PREAMBLE.format(version=sequential_analysis.__version__, site=SITE, guarantees=guarantees),
             "## Procedures (sequential_analysis.procedures)\n\n"
             "Import each with `from sequential_analysis.procedures import <Name>`.\n",
             *procedure_entries(), *module_entries()]
    return "\n\n".join(p.strip("\n") for p in parts) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
