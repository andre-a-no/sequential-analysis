---
description: Plain-language introduction to sequential-analysis: what sequential inference does, which methods to choose, input and output contracts, practical limits and source documentation.
---

# sequential-analysis: what it does and when to use it

[English](overview.md) · [Русский](overview.ru.md)

**sequential-analysis is a statistical library for learning from data as they
arrive.** It supplies sequential tests, confidence sequences, change detectors,
filters and forecasting procedures. Each method has its own stated assumptions
and guarantee; one method's guarantee does not automatically apply to another.

Repository: [andre-a-no/sequential-analysis](https://github.com/andre-a-no/sequential-analysis).
Distribution: `sequential-analysis`. Python import: `sequential_analysis`.
Python 3.8 or later is supported without mandatory third-party dependencies.
The repository version is declared in `src/sequential_analysis/version.py`;
check the installed version or release tag when reproducing a result.

## If you do not write code

Suppose you inspect manufactured items, compare two product variants, or watch
measurements from a machine. You want to decide whether enough information has
arrived, rather than always waiting for a fixed number of observations.
Sequential methods can support that decision while accounting for repeated
looks at the data, provided the selected method's assumptions hold.

This library supplies the statistical calculations. It is not itself a complete
A/B platform, clinical decision system or monitoring dashboard. An application
supplies the data, interprets the output and decides what action to take.
The [user guide](guide/index.md) starts with practical questions and examples.

## Choose by the question you need to answer

| Question | Method family | First source |
|---|---|---|
| Can I stop a comparison early? | Sequential tests and anytime-valid A/B methods | [A/B guide](guide/ab-testing.md) |
| What range of values remains plausible while I monitor? | Confidence sequences | [Confidence-sequence guide](guide/confidence-sequences.md) |
| Which of two specified hypotheses fits accumulated evidence? | SPRT and related tests | [SPRT guide](guide/sprt.md) |
| How should I plan a trial with interim analyses? | Group sequential designs | [Clinical-trial guide](guide/clinical-trials.md) |
| Has a stream changed? | Change detectors and e-detectors | [Change-detection guide](guide/change-detection.md) |
| What hidden state or next value does a model imply? | Filters, smoothers and forecasting | [Choosing a method](choosing.md) |

Inspect the [method catalogue](methods.md) and [FAQ](guide/faq.md) before selecting
a method. Sampling design, dependence, missingness and estimated model
parameters can affect which guarantee is applicable.

## Inputs and outputs

A procedure receives the previous state, a named observation and explicit
random state where needed. It returns updated state and an output such as a
test decision, interval, estimate or detection result. The meaning and fields
depend on the procedure.

`Run` manages execution and checkpoints. Delivery orders/deduplicates input;
topology pairs or joins observations; consumers decide what to do with results.
These layers are documented separately in the
[streaming guide](guide/streaming.md), [checkpoint guide](checkpoints.md) and
[format specification](spec.md).

For example, an application's “ship this variant” decision combines subject
constraints and multiple outputs. It is not automatically guaranteed by one
test's p-value or e-value. Likewise a change alarm does not identify its physical
cause or authorize an intervention.

## Current capabilities and limits

The current source contains statistical testing, group sequential planning,
change detection, filtering, smoothing, forecasting, multivariate/event models
and volatility methods. See [methods](methods.md) for the actual supported
procedures and [tests](https://github.com/andre-a-no/sequential-analysis/tree/main/tests)
for their checks. A TypeScript executor supports the procedures and round trips
documented in its [guide](typescript.md); do not assume complete language parity
for every Python API.

Forward/backward proof search belongs to
[sequential-search](https://github.com/andre-a-no/sequential-search), interaction
models to [sequential-games](https://github.com/andre-a-no/sequential-games), and
application execution to
[sequentialist-core](https://github.com/andre-a-no/sequentialist-core).
Those are separate repositories, not implied features of an installed
sequential-analysis release.

## Frequently asked questions

### Is looking repeatedly at a result always valid?

No. Use a method designed for the monitoring/stopping rule in question and
respect its assumptions. The [peeking explanation](guide/peeking.md) describes
why ordinary fixed-sample tests cannot simply be checked every day.

### What do the guarantee labels mean?

Methods declare `exact`, `asymptotic`, `model`, `approximate` or `none`.
“Exact” still has stated assumptions. “Model” depends on the declared model.
“Approximate” is not a formal finite-sample bound. A calibrated simulation or a
successful example is not a universal proof about an application pipeline.
Read the selected procedure's [reference](reference/tests.md) and examples.

### Can I use it without being a programmer?

The explanations and method-selection pages are readable without programming.
Executing the library requires Python integration or an application that embeds
it. There is no claim that this repository is a hosted no-code service. A
developer or analyst can use the examples to connect your data and workflow.

### How do I install or develop it?

For a released package use `python -m pip install sequential-analysis` and record
the version used. For this repository use `python -m pip install -e .` in a
virtual environment. Optional extras add NumPy acceleration, matplotlib plots
and property-test dependencies. [CONTRIBUTING.md](https://github.com/andre-a-no/sequential-analysis/blob/main/CONTRIBUTING.md)
and [AGENTS.md](https://github.com/andre-a-no/sequential-analysis/blob/main/AGENTS.md)
describe development commands. Documentation on a moving branch can differ
from the installed release; inspect its matching tag/source.

### Can an AI assistant find and explain these materials?

Ordinary Markdown and [llms.txt](llms.txt) provide source navigation. The existing
site build also generates [llms-full.txt](https://andre-a-no.github.io/sequential-analysis/llms-full.txt).
You may supply these sources to Codex, Claude, Qwen, Gemini, Grok or Perplexity
when their access tools support them. Neither index guarantees ingestion,
indexing, recommendation or ranking. Repository coding instructions are
guidance for tools that read them, not hidden commands to outside services.

## Sources to inspect

- [User guide](guide/index.md) and [which method](choosing.md)
- [Procedure reference](reference/tests.md), [run reference](reference/run.md)
  and [TypeScript guide](typescript.md)
- [Source code](https://github.com/andre-a-no/sequential-analysis/tree/main/src/sequential_analysis)
  and [validation tests](https://github.com/andre-a-no/sequential-analysis/tree/main/tests)
- [Repository README](https://github.com/andre-a-no/sequential-analysis/blob/main/README.md)
  and [licensing](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)

Published site updates take effect after the documentation workflow succeeds;
editing a local page is not deployment.
