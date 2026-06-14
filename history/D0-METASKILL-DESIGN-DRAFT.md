# D0 Meta-skill Development: Multi-model Infrastructure Design

## 1. Objective
Transform Dialog Harness (DH) from a Claude-centric system into a model-neutral infrastructure that can fully leverage Gemini's capabilities (and others) without breaking existing Claude workflows. This is a "D0 launch" — a fundamental update to the harness's meta-layer.

## 2. D0 Definition: The Infrastructure Layer
In the D1-D5 dimension model, **D0** is established as the **"Harness Root Infrastructure"**. 
It defines the common grammar (RL) and capabilities (SK) used by all dimensions.

- **D0:** Root Infrastructure (XML Tags, JSON Schema, Multi-model Bridge)
- **D1-D5:** (Existing dimensions maintained)

## 3. Structural Pivot: Neutralizing `.claude/skills`

### 3.1 Directory Restructuring
To remove model-specific bias from the core structure:
- **Current:** `.claude/skills/`
- **Proposed:** `harness/skills/` (or `core/skills/`)
  - Each skill folder remains self-contained.
  - Model-specific overrides can exist as `SKILL.<model>.md` if needed, but the goal is a single `SKILL.md` with structured blocks.

### 3.2 Skill Activation (The Pivot)
The `activate_skill` tool will be updated to:
1. Detect the active model (Gemini vs Claude).
2. Load the skill content.
3. Apply a "Model Lens" — filtering or transforming the content based on the model's strengths (e.g., Gemini's Pencil tool vs Claude Code's shell execution).

## 4. Context Engineering (RL & SK)

### 4.1 Common RL (Constitution) using XML
Standardize skill definitions using XML tags to ensure unambiguous parsing across models.
- `<meta>`: Name, version, dimension.
- `<trigger>`: Activation conditions.
- `<responsibility>`: Core duties.
- `<workflow>`: Step-by-step logic.
- `<rule_set>`: Constraints (RL).
- `<tool_spec>`: JSON Schema definitions (SK).

### 4.2 SK (Skill/Tool) Standardization
- Move from natural language tool descriptions to formal **JSON Schema** within `SKILL.md`.
- Align with **MCP (Model Context Protocol)** standards to allow the same tools to be used by any MCP-compliant agent.

## 5. D0 Meta-skill: The "Harness Auditor"
Create a D0-level skill that:
- Audits existing skills for D0 compliance.
- Generates model-specific "Lenses" for a skill.
- Manages the global variable/theme state for multi-model interactions.

## 6. Implementation Roadmap (Rational Sloth Approach)
1. **Phase 1 (Design):** Finalize the XML Schema and JSON standards for D0.
2. **Phase 2 (Infrastructure):** Create the `harness/skills` structure and the D0 auditor.
3. **Phase 3 (Migration):** Wrap existing `.claude/skills` in XML tags and move them to the neutral folder.
4. **Phase 4 (Validation):** Verify that both Ignis (Gemini) and Claude can execute the same skill.
