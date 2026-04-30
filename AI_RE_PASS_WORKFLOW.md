# AI Reverse-Engineering Pass Workflow

This is the execution brief for the next AI pass on the Vagrant Story USA RE
workspace.

The goal is simple: make one evidence-backed improvement, verify it, leave the
workspace cleaner than before, and stop without pushing.

If a capable model choice is available, prefer `gpt-5.4` with high reasoning
effort.

## Mission

Complete one focused pass that:

1. picks one narrow RE question
2. turns it into a concrete improvement in code, notes, or tooling
3. verifies the result against real data, source, or runtime behavior
4. makes the local conventional commit unless config disables commits

It is fine for the result to be a tighter note, a safer name, or a confidence
hold instead of a flashy rename. Accuracy matters more than novelty.

## Code Exploration Policy

Use `jcodemunch-mcp` first for repo exploration.

- start with `resolve_repo { "path": "." }`
- if needed, call `index_folder { "path": "." }`
- open with
  `plan_turn { "repo": "<resolved repo id>", "query": "<pass question>", "model": "<active model id>" }`
- use `get_file_outline` before opening files
- use `search_symbols` for handlers, helpers, globals, and structs
- use `search_text` for strings, configs, decoded output, and repeated context
- use `find_references`, `check_references`, and `get_context_bundle` to trace
  consumer paths
- only use direct file reads when you are about to edit a specific file

## Main Lanes

Pick the lane that best matches the question.

- Script and opcode work:
  [`dump_mpd_script.py`](dump_mpd_script.py),
  [`decoded_scripts`](decoded_scripts),
  [`OPCODE_BEHAVIOR_REFERENCE.md`](OPCODE_BEHAVIOR_REFERENCE.md),
  [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md),
  [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)
- Room and scene work:
  [`analyze_room_graph.py`](analyze_room_graph.py),
  [`ROOM_CONNECTION_FINDINGS.md`](ROOM_CONNECTION_FINDINGS.md),
  [`room_names.tsv`](room_names.tsv)
- Broad engine and format work:
  [`README.md`](README.md),
  [`VAGRANT_STORY_MODDING_OVERVIEW.md`](VAGRANT_STORY_MODDING_OVERVIEW.md),
  [`_refs/rood-reverse`](_refs/rood-reverse)

Useful reference anchors inside `_refs/rood-reverse`:

- `src/` for matched code
- `config/**/symbol_addrs.txt` and `splat.yaml` for lookup anchors
- `assets/**/*.yaml` for strings and menu-side confirmation

## Local Tools

- `dump_mpd_script.py`: opcode meaning, argument layout, event sequencing,
  repeated room patterns
- `analyze_room_graph.py`: room types, `sceneId`, `sectionF`, reachability,
  TSV refreshes
- `Ghidra`: nonmatching code, xrefs, data layout, control flow
- `PCSX-Redux`: runtime confirmation when static evidence is not enough

Common commands:

```powershell
python dump_mpd_script.py "Game Data/MAP"
python analyze_room_graph.py
python analyze_room_graph.py --update-tsv
```

## Local Config

Read [`AI_RE_PASS_WORKFLOW.config.toml`](AI_RE_PASS_WORKFLOW.config.toml) if it
exists. Otherwise use
[`AI_RE_PASS_WORKFLOW.config.example.toml`](AI_RE_PASS_WORKFLOW.config.example.toml).

Supported setting:

- `commit_mode = "auto"`: make the local commit yourself
- `commit_mode = "no-commit"`: stage the intended changes and stop before
  `git commit`

Never push.

## Working Style

Before substantial work:

1. check repo state in each repo you might edit
2. if a repo is dirty and you need to edit it, warn the user before stashing
3. stash pre-existing changes in repos you will edit, then restore them at the
   end
4. read the current conclusions note before renaming anything
5. avoid unrelated edits
6. prefer one strong improvement over several weak ones

If both this workspace and `_refs/rood-reverse` need updates, keep each repo's
changes focused and report the exact commit message used for each one.

## Good Targets

- opcode naming or argument rendering improvements
- helper or internal renames backed by direct code proof
- struct or data-layout interpretation improvements
- room, scene, or reachability classification improvements
- menu, sound, or overlay behavior clarified through code plus assets
- runtime validation of a static theory
- decoder, parser, or note improvements that unblock future passes

Do not rename something just to eliminate a placeholder.

## Workflow

### 1. Pick one narrow question

Examples:

- does a current opcode name overclaim its meaning?
- can one raw parameter blob be rendered more usefully?
- is one `Strong` result actually `Confirmed`, or should it stay `Strong`?
- does one scene or room field deserve a clearer explanation?
- is one helper understandable enough to justify a conservative rename?

### 2. Pull the best evidence first

Use the most informative source for the question:

- `decoded_scripts` for usage patterns
- `_refs/rood-reverse` for handlers and consumers
- `Ghidra` for gaps in matched code
- `PCSX-Redux` for runtime proof
- `MAP*.MPD` and `SCEN*.ARM` for layout questions

For opcode work, preserve repeated context, timing values, stepped scalars, and
neighboring setup or cleanup opcodes.

For room and scene work, preserve exact `sceneId` sources, marker flag checks,
cross-zone examples, and special cases such as scene `0`.

### 3. Confirm the direct anchor

Do not infer from proximity if a stronger anchor exists.

- for opcodes, prefer the dispatch table and symbol-address anchors
- for room and scene work, prefer exact parser anchors such as
  `sectionB + 0x50`, `sectionF`, and `SCEN*.ARM` marker flags
- for menu or sound work, cross-check matched source, config lookup anchors,
  and asset yaml names

### 4. Trace the consumer path

Do not stop at "this writes field X." Keep following until the user-facing
meaning becomes clear, the proof runs out, or a broader claim would overstate
the evidence.

If code, strings, assets, and config disagree, document the disagreement
instead of hiding it.

### 5. Make the smallest honest update

Valid results include:

- confirmed rename
- confirmed helper or internal rename
- confidence held or downgraded with a clearer note
- argument rendering improvement
- room or scene classification improvement
- parser or analysis improvement
- runtime-confirmed interpretation

## Good Outputs

A good pass usually updates one or more of:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`OPCODE_BEHAVIOR_REFERENCE.md`](OPCODE_BEHAVIOR_REFERENCE.md)
- [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md)
- [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)
- [`analyze_room_graph.py`](analyze_room_graph.py)
- [`ROOM_CONNECTION_FINDINGS.md`](ROOM_CONNECTION_FINDINGS.md)
- [`room_names.tsv`](room_names.tsv)
- [`README.md`](README.md)
- [`VAGRANT_STORY_MODDING_OVERVIEW.md`](VAGRANT_STORY_MODDING_OVERVIEW.md)

## Verification

Before stopping:

1. verify against at least one strong source, preferably two
2. confirm the new result is more accurate or more informative than before
3. reread the final wording and make sure it does not claim too much

Examples:

- decoded output now renders a structure instead of a blob
- a rename fits several real rooms
- a helper rename matches implementation and local call sites
- timing or signedness matches raw bytes
- runtime behavior matches the theory
- room-graph counts or exclusions still make sense after a graph change

## Finish Line

The pass is done when:

1. the intended files are updated
2. the diff is focused
3. verification is done
4. the AI commits locally when `commit_mode = "auto"`, or stages only when
   `commit_mode = "no-commit"`
5. any temporary stash is restored
6. the user gets a short conclusions summary plus the exact commit message for
   each touched repo

Use conventional commits. Good shapes:

```text
feat(re): improve opcode 0x7A argument rendering
fix(tooling): refine room graph classification
docs(re): tighten evidence for menu sound behavior
```

## Final Report

At the end, report:

1. the question you targeted
2. what evidence mattered most
3. what still blocks any remaining confidence bump
4. which files changed
5. how you verified it
6. the short conclusions summary
7. the exact commit message for each touched repo
8. the commit hash for each local commit, or explicit confirmation that commits
   were skipped because `commit_mode = "no-commit"`
9. whether any stash was restored

## Avoid

Do not:

- fight headless Ghidra first
- rename multiple weak opcodes in one pass
- rename helpers based only on adjacency or vibes
- treat a confidence bump as the default success condition
- convert tentative notes into confident names without proof
- leave unexplained experimental edits behind
- end with only future ideas and no concrete artifact

## Kickoff Line

```text
Do one focused RE pass, use the right local tools for the question, make the smallest honest verified improvement you can justify, commit locally unless config disables it, restore any temporary stash, summarize the result, and stop without pushing.
```
