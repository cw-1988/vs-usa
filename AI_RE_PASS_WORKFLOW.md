# AI Reverse-Engineering Pass Workflow

This note is the execution brief for the next AI pass on the Vagrant Story
script reverse-engineering workspace.

The goal is to keep moving the reverse-engineering work forward in a useful,
evidence-backed way without making the workflow feel cramped or mechanical.
This file is meant to be general to the workspace, not just tied to one opcode
or one specific ongoing thread.

If a capable model choice is available, prefer `gpt-5.4` with high reasoning
effort for this pass.

## Mission

Complete one focused reverse-engineering pass that:

1. identifies one concrete RE improvement
2. updates the local tooling, notes, or supporting analysis to reflect that improvement
3. verifies the change against real game data, source references, runtime behavior, or decoded output
4. makes the AI's own conventional commit for each touched repo unless the
   local config explicitly disables commits
5. leaves the repo in a state where the user can review, undo, or amend the
   local commit(s) before anything is pushed

Do not end with only vague conclusions. Convert the pass into code or note changes
unless the evidence is too weak to justify a rename.

If a pass produces changes that belong in both this workspace and
`_refs/rood-reverse`, treat that as normal. Keep each repo's changes focused,
commit them in the repo they belong to when commits are enabled, and report the
exact message used for each touched repo.

## Main Files

Start here:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md)
- [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)
- [`decoded_scripts`](decoded_scripts)

Reference sources:

- [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)
- [`_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c`](_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c)
- [`_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt`](_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt)
- [`_refs/rood-reverse/BATTLE_SCREEN_EFFECT_OPCODE_CONCLUSIONS.md`](_refs/rood-reverse/BATTLE_SCREEN_EFFECT_OPCODE_CONCLUSIONS.md)

Useful local tooling:

- [`tools/ghidra_12.0.4_PUBLIC`](tools/ghidra_12.0.4_PUBLIC)
- [`tools/pcsx-redux`](tools/pcsx-redux)

## Local Config

Read [`AI_RE_PASS_WORKFLOW.config.toml`](AI_RE_PASS_WORKFLOW.config.toml) if it
exists. If it does not exist, fall back to
[`AI_RE_PASS_WORKFLOW.config.example.toml`](AI_RE_PASS_WORKFLOW.config.example.toml)
for the default behavior and expected keys.

Current supported setting:

- `commit_mode = "auto"`: make the conventional commit(s) yourself
- `commit_mode = "no-commit"`: stage the intended changes and stop before
  `git commit`

Never push as part of this workflow. Local commits are allowed and expected
when `commit_mode = "auto"`.

## Tooling

Choose tools based on the question instead of forcing one workflow every time.

### `rg`

Use `rg` first for:

- finding opcode names or placeholders in repo files
- pulling repeated decoded-script contexts
- locating handler names, globals, and symbols in `_refs/rood-reverse`

### `dump_mpd_script.py`

Use this when the question is about:

- script opcode meaning
- argument layout
- room event sequencing
- comparing repeated script patterns across maps

### `Ghidra`

Use Ghidra when:

- source references stop in nonmatching code
- you need xrefs to unnamed globals or fields
- you need to inspect data layout, call structure, or control flow directly
- the current question is really about executable behavior rather than script pattern alone

Prefer the GUI for exploratory work. Do not start with headless automation
unless there is a concrete reason.

### `PCSX-Redux`

Use PCSX-Redux when:

- static analysis is not enough
- a behavior needs runtime confirmation
- you want to watch a script effect, camera change, audio reaction, or room transition live
- you need to verify whether a guessed interpretation matches what the game actually does

### `_refs/rood-reverse`

Use the reference checkout as the first code-level anchor when it already
contains matched or partially named logic. It is often faster than dropping
straight into raw disassembly.

It is not always read-only. If the RE result justifies upstreamable decoder,
symbol, struct, comment, or matched-code improvements there, make those
changes in `_refs/rood-reverse` as part of the same pass instead of leaving the
finding stranded only in local notes.

That includes helper-function or internal-state renames, but only when the
code-level behavior is rock-hard and directly supported by matched or otherwise
clear implementation evidence. Do not use helper renames as a way to smuggle in
a speculative script-facing interpretation.

If a pass changes `_refs/rood-reverse`, add or update one short standalone
conclusions note in that repo too. Prefer a root-level `*_CONCLUSIONS.md` file named
for the subsystem, keep it tightly scoped to the current pass, and cite the
source files that justify the nested-repo edits so the evidence travels with
the upstreamable changes.

## Working Style

Before doing anything substantial:

1. Run `git status --short`.
2. If you are going to touch a repo that already has pre-existing changes, say
   this exact message to the user in all caps before stashing:
   `PRE-EXISTING LOCAL CHANGES DETECTED. I AM STASHING THEM BEFORE I START AND I WILL UNSTASH THEM AFTER I FINISH.`
3. In each dirty repo you plan to edit, stash the pre-existing changes before
   making your own edits and restore them after your work is complete.
4. Read the current conclusions note before renaming anything.
5. Avoid touching unrelated user changes.
6. Prefer one strong improvement over five speculative ones.

If the worktree is already dirty, do not revert it. Protect it with
stash/unstash flow instead.

## Choosing A Target

Pick a tractable target with a good chance of producing a useful artifact in
one pass.

Good target types:

- opcode naming or argument-layout improvements
- helper-function or internal-state naming improvements when behavior is
  unquestionably confirmed
- struct-field interpretation improvements
- runtime validation of a static RE theory
- decoder or tooling quality-of-life improvements that support RE work
- note cleanup that materially improves future passes

Good heuristics:

- prefer questions with multiple available evidence sources
- prefer one solid win over a broad but fuzzy sweep
- prefer work that can be validated before stopping

Do not rename an opcode just to eliminate a placeholder. Evidence matters more
than tidiness.

The same rule applies to helper functions and internals: only rename them when
the implementation meaning is genuinely locked in.

## Workflow

### Step 1. Pick one narrow question

Examples:

- Is `0xEF` better described as a waveform initializer, oscillation setup, or
  something even more specific?
- Is `0xE6` really `ScreenEffectOffsetTween`, or is there a better render-space
  name?
- Is there enough proof to promote one `Strong` finding to `Confirmed`?
- Is a still-unnamed field in `BATTLE.PRG` understandable enough to document?

Write the question down in your scratch notes before broad searching if that
helps keep the pass focused, but do not turn this into a paperwork exercise.

### Step 2. Pull the best evidence first

Start from the most informative source for the current question.

Examples:

- `decoded_scripts` for script opcode or cutscene sequencing questions
- `_refs/rood-reverse` for handler and consumer questions
- `Ghidra` for nonmatching code or unnamed globals
- `PCSX-Redux` for runtime confirmation
- `MAP*.MPD` or repo scripts for data-layout questions

Good patterns:

```powershell
rg -n "OpcodeEF|ScreenEffect|CameraRollTween|SetRoomAmbientSoundSuspended" decoded_scripts
rg -n "^[0-9A-F]{4}: EF " decoded_scripts -S
```

For opcode work, especially `0xEF`, compare multiple rooms and preserve:

- repeated control words
- stepped scalar changes
- timing values
- neighboring opcodes like `E1`, `E4`, `E5`, `E6`, `E7`, `ED`, `EA`, `EB`

### Step 3. Confirm the handler mapping

Use the dispatch table before inferring from source order.

```powershell
rg -n "_opcodeFunctionTable|vs_battle_script_setScreenEffectEnabled|vs_battle_script_setupAngleTween|func_800BD6C4|func_800BDC9C|func_800BB450|func_800BD444" _refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c _refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt
```

### Step 4. Trace the consumer path

Do not stop at "this handler writes field X".

Keep going until one of these happens:

- the field consumer clarifies the user-facing meaning
- the decomp becomes nonmatching and blocks certainty
- the script evidence is already strong enough for a conservative local rename
- the helper or internal behavior is clear enough to justify a code-level name
  even if the final script-facing label should stay more conservative

For non-opcode work, the equivalent rule still applies:

- do not stop at one parsed field or one string match
- follow the data until the user-facing meaning becomes clearer

### Step 5. Decide what kind of change is justified

Only choose one of these as the main result:

- `Confirmed rename`
- `Confirmed helper/internal rename`
- `Conservative local tooling rename`
- `Argument rendering improvement only`
- `Note-only evidence update`
- `Analysis or parser improvement`
- `Runtime-confirmed interpretation`

If the best honest result is "better structured arguments but no better final
name", that is still a valid pass.

## Good Outputs

A successful pass should update one or more of:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`ROOD_REVERSE_OPCODE_CONCLUSIONS.md`](ROOD_REVERSE_OPCODE_CONCLUSIONS.md)
- [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)

Optional if truly useful:

- a short new note with tightly scoped conclusions in this workspace or in
  `_refs/rood-reverse` when the pass changes the nested repo
- comments or code changes in `_refs/rood-reverse` if that materially helps the
  next pass or captures an upstreamable RE result
- helper or internal naming cleanup in `_refs/rood-reverse` when it is backed
  by directly readable code behavior rather than a guess about player-facing
  semantics

Do not create a giant theory dump unless it directly helps the next pass.
Prefer changes that improve the decoder, the conclusions trail, or both.

## Verification

Before stopping, verify the result against real data.

Minimum verification:

1. Verify the relevant behavior against at least one strong source, and prefer
   two when practical.
2. Confirm the result is more informative or more accurate than before.
3. Re-read the wording in the conclusions note and make sure it does not claim
   more than the code proves.

Good verification examples:

- confirm `OpcodeEF` now shows structured fields instead of an opaque blob
- confirm a rename appears correctly in several decoded rooms
- confirm helper or internal renames match the matched implementation and all
  local call sites
- confirm timing or signedness interpretation matches raw bytes
- confirm a runtime theory matches observed behavior in `PCSX-Redux`

## Finish Line

The end state should be either:

- a local conventional commit in each touched repo, ready for user review, or
- a staged-but-uncommitted result only when `commit_mode = "no-commit"`

That means:

1. The intended files are edited.
2. The diff is focused.
3. Verification is done.
4. The AI either makes the conventional commit itself or stages only when the
   config forbids commits.
5. Any stashed pre-existing user changes are restored before stopping.
6. The user is given a clear conclusions summary.
7. The user is given the exact conventional commit message used, or the exact
   message that would have been used when commits are disabled.

Run `git commit` when `commit_mode = "auto"`. Do not run `git push`.

If unrelated changes already exist in the worktree, stage only the files or
hunks that belong to this pass before committing. Do not stage unrelated user
work.

If both repos were changed, create one focused conventional commit per touched
repo and say clearly which message belongs to which repo.

## Commit Strategy

Use conventional commits.

Good default shapes:

```text
feat(re): clarify opcode 0xEF decoder output
fix(re-notes): tighten evidence for screen effect opcodes
docs(re): capture new opcode conclusions for 0x7A
```

Examples:

- `feat(re): improve opcode 0xEF argument rendering`
- `docs(re): add new evidence for opcode 0xEF waveform behavior`
- `fix(decoder): rename confirmed screen effect opcodes`

Pick the type honestly:

- `feat`: new decoder capability or new meaningful interpretation
- `fix`: corrected behavior, naming, or rendering
- `docs`: note-only or workflow-only improvements

Other acceptable scopes include:

- `re`
- `decoder`
- `notes`
- `tooling`

At the end of the pass, provide one actual commit message per touched repo, not
just a pattern.

When `commit_mode = "auto"`, do not stop after staging. Make the conventional
commit yourself. When `commit_mode = "no-commit"`, stop after staging and still
report the exact message that would have been used.

## Final Report Format

When the pass is complete, report:

1. what question you targeted
2. what evidence changed your confidence
3. which files were updated
4. how you verified it
5. a short summary of the conclusions in normal prose
6. the exact conventional commit message for each touched repo
7. the commit hash for each local commit, or explicit confirmation that commits
   were skipped because `commit_mode = "no-commit"`
8. confirmation that any temporary stash was restored

## Avoid

Do not:

- fight headless Ghidra first
- rename multiple weak opcodes in one pass
- rename helper functions or internals based only on adjacency or a hoped-for
  script meaning
- convert tentative notes into confident names without proof
- leave the repo with unexplained experimental edits
- end with only "next ideas" and no concrete artifact
- force every pass to be opcode-focused if the better win is elsewhere

## Short Version

Pick one solid RE question. Use the best available tools for that question:
repo scripts, `rg`, `_refs/rood-reverse`, `Ghidra`, or `PCSX-Redux`. Make the
smallest honest improvement that leaves the workspace better than before.
Verify it. Commit the intended changes locally unless the config disables that.
Stop without pushing.

## Kickoff Line

If the next AI needs a one-line mission, use this:

```text
Do one focused RE pass, use the right local tools for the question, turn the result into verified workspace improvements, make the local conventional commit unless config disables it, restore any temporary stash, summarize the conclusions, and stop without pushing.
```
