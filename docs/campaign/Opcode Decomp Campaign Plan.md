# Multi-Pass Opcode Decomp Campaign With Cross-Session Memory

## Summary

Create one master campaign memory file, `RE_CAMPAIGN_MEMORY.md`, as the cross-session source of truth for opcode/decomp work, then align the existing workflow docs so every future session starts from that ledger and updates it in a consistent way.

This campaign is **opcode-first**. The first objective is not “fully name every opcode,” but to finish the foundational passes that make later semantic passes cheap and safe: table ownership, runtime-copy/patch paths, handler coverage, shared-handler clustering, and contradiction tracking.

## Evidence Source Rule

For this campaign, keep the authority chain explicit:

- the original binary plus runtime behavior are the ground truth
- artifacts under `decomp/` are the local evidence authority
- [`../../_refs/rood-reverse`](../../_refs/rood-reverse) is hint-only and may suggest
  targets, addresses, or candidate meanings

That means:

- never treat `_refs/rood-reverse` files as stand-alone proof in
  `RE_CAMPAIGN_MEMORY.md`
- never let a proof packet rely mainly on helper-decompiled C when the claim
  can be converted into a local `Ghidra` export, local verification artifact,
  or runtime capture
- if a helper-repo idea matters, convert it into a local artifact first and
  cite the local artifact as evidence
- helper provenance can still be noted, but only after the local artifact
  exists

## Key Changes

### 1. Add one master cross-session memory file

Create `RE_CAMPAIGN_MEMORY.md` at repo root.

It should be the first repo-specific file read at the start of any substantial opcode/decomp session, alongside `DECOMPILATION_STRATEGY.md` and `CLI_DECOMPILATION_WORKFLOW.md`.

Use this fixed structure:

1. `Campaign Goal`
   - One paragraph stating the current campaign objective: build a verified opcode/handler map for the battle-script system before promoting meanings.

2. `Current Phase`
   - One line with the active pass number and name.
   - Example shape: `Current phase: Pass 2 - Handler coverage and classification`

3. `Status Legend`
   - Fixed statuses:
     - `unstarted`
     - `in_progress`
     - `covered`
     - `conflicted`
     - `runtime_needed`
     - `confirmed`

4. `Pass Plan`
   - Ordered list of passes with:
     - pass id
     - goal
     - expected outputs
     - exit condition
   - This is the stable campaign backbone.

5. `Priority Targets`
   - Flat table for active opcode targets.
   - Required columns:
     - `target`
     - `current_status`
     - `table_owner`
     - `handler_owner`
     - `best_current_name`
     - `blocking_question`
     - `next_pass`
     - `evidence_links`

6. `Known Conflicts`
   - One subsection per unresolved contradiction.
   - Required fields:
     - short conflict title
     - what static evidence says
     - what competing evidence says
     - what is still missing
     - whether runtime is justified yet

7. `Artifacts Index`
   - Flat list of key machine-readable exports and proof packets.
   - Group by:
     - table exports
     - handler slices
     - reconciliation reports
     - proof packets

8. `Session Handoff`
   - Very short section updated every pass.
   - Required fields:
     - `last completed step`
     - `next recommended step`
     - `do not forget`
   - This is the actual memory bridge for the next session.

9. `Completed Milestones`
   - Append-only short log of meaningful campaign completions.
   - Use date + milestone + links.

The file should stay compact. It is a campaign ledger, not a narrative diary.

### 2. Define the multi-pass campaign backbone

The master ledger should define these passes exactly:

1. `Pass 0 - Bootstrap and inventory`
   - Goal: identify all opcode-table owners, known initializers, copy sites, and likely patch points.
   - Outputs:
     - master list of tables
     - overlay ownership notes
     - first artifact index entries
   - Exit condition: every known battle-script table has an owner and initializer note.

2. `Pass 1 - Table export coverage`
   - Goal: export binary-derived entries for every known relevant opcode table.
   - Outputs:
     - JSON table exports under `decomp/evidence`
     - wrapper scripts under `decomp/ghidra`
   - Exit condition: all targeted tables have reproducible exports with correct base-address notes.

3. `Pass 2 - Handler coverage and classification`
   - Goal: map every exported opcode to a handler address and classify unique handlers.
   - Classifications:
     - `stub`
     - `real`
     - `shared`
     - `orphan_candidate`
     - `unknown_gap`
   - Outputs:
     - coverage report
     - shared-handler map
   - Exit condition: every opcode in scope has a handler mapping and provisional class.

4. `Pass 3 - Copy/patch reconciliation`
   - Goal: determine whether runtime tables are copied only once or patched later.
   - Outputs:
     - copy-site notes
     - patch-site notes
     - unresolved runtime-needed list
   - Exit condition: every conflict is labeled either `static_resolved` or `runtime_needed`.

5. `Pass 4 - Semantic proof packets`
   - Goal: produce focused proof packets only for the high-value or conflicted opcodes.
   - Outputs:
     - one markdown proof packet per disputed opcode family
     - linked binary exports and script examples
   - Exit condition: all priority targets have either `confirmed`, `tentative`, or `conflicted` status with explicit evidence.

6. `Pass 5 - Naming and decoder updates`
   - Goal: only after the earlier passes, promote safe names into `dump_mpd_script.py` and opcode notes.
   - Outputs:
     - decoder naming changes
     - conclusion-note updates
   - Exit condition: no name promotion lacks a proof-packet anchor.

7. `Pass 6 - Audit and maintenance`
   - Goal: keep the campaign from drifting.
   - Outputs:
     - contradiction audit
     - stale-artifact audit
     - missing-export audit
   - Exit condition: ledger and artifacts still agree.

### 3. Standardize how each future session uses the ledger

Update the existing workflow docs so every session follows this sequence:

1. Read:
   - `RE_CAMPAIGN_MEMORY.md`
   - `DECOMPILATION_STRATEGY.md`
   - `CLI_DECOMPILATION_WORKFLOW.md`

2. Pick work only from:
   - `Priority Targets`
   - or the `next recommended step` in `Session Handoff`

3. During the pass, produce one of:
   - export artifact
   - coverage artifact
   - proof packet
   - contradiction note
   - and make sure it is a local artifact under `decomp/`, not just a helper
     repo citation

4. Before ending the pass, update only these ledger sections:
   - `Current Phase`
   - `Priority Targets`
   - `Known Conflicts`
   - `Artifacts Index`
   - `Session Handoff`
   - optional `Completed Milestones`

5. Never let a session end with new evidence that exists only in terminal output.

### 4. Align the current docs around the ledger

Update these existing docs to reference the master memory file:

- `README.md`
  - add the new campaign ledger to the repo layout and explain that it is the cross-session memory entrypoint for opcode/decomp work

- `AI_RE_PASS_WORKFLOW.md`
  - require reading `RE_CAMPAIGN_MEMORY.md` before choosing a target
  - require updating the ledger before ending a pass
  - require choosing work from the campaign pass structure or priority-target list

- `CLI_DECOMPILATION_WORKFLOW.md`
  - frame exports and proof packets as artifacts that must be registered in the ledger
  - point conflict-state tracking to the ledger rather than scattered notes

- `DECOMPILATION_STRATEGY.md`
  - treat the ledger as the local campaign authority for in-progress state, while binary/runtime remain evidence authority

- `decomp/README.md`
  - explain that `decomp/` stores implementation artifacts while `RE_CAMPAIGN_MEMORY.md` stores campaign state and handoff memory

Also update those docs to repeat this rule:

- `_refs/rood-reverse` may guide investigation
- local `decomp/` artifacts, binary exports, and runtime captures must carry
  the evidentiary weight

### 5. Keep evidence and memory separate on purpose

Use this division consistently:

- `RE_CAMPAIGN_MEMORY.md`
  - campaign state
  - priorities
  - handoff memory
  - conflict summaries
  - artifact links

- `decomp/evidence/*`
  - raw exports
  - proof packets
  - coverage outputs
  - contradiction-specific evidence

- `_refs/rood-reverse/*`
  - helper corpus only
  - can supply leads and candidate names
  - should not be cited as final proof when a local artifact can be produced

- existing opcode docs
  - stable conclusions only
  - not the place for active campaign state

This prevents the “working memory” from being mixed into stable reference notes too early.

## Test Plan

1. Dry-run a new session using only the docs.
   - A fresh pass should be able to answer:
     - what is the current phase?
     - what target should I do next?
     - what artifacts already exist?
     - what conflicts are unresolved?
     - when is runtime justified?

2. Run one simulated handoff.
   - One session updates `Session Handoff`.
   - A second session should be able to resume without rereading the entire repo history.

3. Validate one real target, `0x80`.
   - Ledger should show:
     - current status
     - binary table owner
     - handler owner
     - open conflict
     - linked evidence files
     - next recommended pass
   - If that can be represented cleanly, the structure is working.

4. Check drift prevention.
   - Every artifact named in the ledger should exist.
   - Every `confirmed` target in the ledger should have an evidence link.
   - No `runtime_needed` target should lack a stated static contradiction.

## Assumptions

- Use **one master ledger**, not per-track ledgers.
- The campaign is **opcode/decomp-first**, not a whole-repo generic framework.
- Existing stable notes such as `OPCODE_BEHAVIOR_REFERENCE.md` remain in place; they are not replaced by the ledger.
- The ledger is intentionally markdown-first and human-maintained rather than generated.
- `PCSX-Redux` remains a late-stage tie-breaker, not part of every pass.
