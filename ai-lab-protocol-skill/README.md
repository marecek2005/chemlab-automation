# AI Lab Protocol Automation Skill (`protokol`)

A portable **AI Agent Skill** and Python automation pipeline for generating, validating, and typesetting university laboratory reports in physics, physical chemistry, analytical chemistry, and nano/micro-materials engineering.

## Design Philosophy

Standard LLM prompts often hallucinate measurements, drop error bars, or break academic formatting. This skill enforces a strict engineering workflow defined in [`SKILL.md`](SKILL.md):

1. **Data Grounding & Anti-Hallucination**: Distinguishes measured, prescribed, computed, and literature reference values; forbids fabricating missing readings or instrument accuracies.
2. **Deterministic Python Calculation & Plotting**: Reads raw experimental spreadsheets (`.xlsx`) via `scripts/read_xlsx.py` and renders plots/tables programmatically rather than via manual LLM estimation.
3. **Typography-Compliant DOCX Generation**: Builds clean Word documents using `scripts/docx_helpers.py` and `scripts/render_docx.py` with proper Czech/SI scientific formatting (non-breaking spaces before units, decimal commas, consistent significant figures, uncertainty propagation).
4. **Portability Validation**: `scripts/validate_package.py` verifies there are no hardcoded host-machine paths or broken external links before distribution across AI coding agents (Claude Code, Codex, Antigravity, Gemini CLI).

## Contents

- `SKILL.md`: Complete agent instruction specification and quality gates.
- `agents/openai.yaml`: Agent metadata descriptor.
- `references/`: Domain-specific guidelines for physical/analytical/materials chemistry (`obory.md`), scientific typography (`typografie.md`), technical rendering pipeline (`technicky-postup.md`), verification checklist (`overeni.md`), visual style (`vzor-a-styl.md`), and dependencies (`zavislosti.md`).
- `scripts/`:
  - `check_env.py`: Checks Python dependency availability (`python-docx`, `openpyxl`, `matplotlib`, `numpy`, `pillow`, `pypdf`).
  - `read_xlsx.py`: Structured Excel measurement extractor.
  - `docx_helpers.py`: Reusable `python-docx` builders for tables, captions, equations, and styles.
  - `render_docx.py`: High-level document renderer & visual QA helper.
  - `setup.py` & `validate_package.py`: Portable skill installation and sanity verification.

## Quick Verification

```bash
python scripts/check_env.py
```
