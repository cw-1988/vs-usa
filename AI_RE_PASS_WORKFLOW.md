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
4. stages the AI's own intended changes
5. leaves the repo in a state where the user can review the summary and then
   just press commit

Do not end with only vague findings. Convert the pass into code or note changes
unless the evidence is too weak to justify a rename.

If a pass produces changes that belong in both this workspace and
`_refs/rood-reverse`, treat that as normal. Keep each repo's changes focused,
stage them in the repo they belong to, and report commit-ready messages for
each touched repo.

## Main Files

Start here:

- [`dump_mpd_script.py`](dump_mpd_script.py)
- [`ROOD_REVERSE_OPCODE_FINDINGS.md`](ROOD_REVERSE_OPCODE_FINDINGS.md)
- [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)
- [`decoded_scripts`](decoded_scripts)

Reference sources:

- [`_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c`](_refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/4A0A8.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.c)
- [`_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h`](_refs/rood-reverse/src/BATTLE/BATTLE.PRG/146C.h)
- [`_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c`](_refs/rood-reverse/src/GIM/SCREFF2.PRG/0.c)
- [`_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt`](_refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt)

Useful local tooling:

- [`tools/ghidra_12.0.4_PUBLIC`](tools/ghidra_12.0.4_PUBLIC)
- [`tools/pcsx-redux`](tools/pcsx-redux)

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

## Working Style

Before doing anything substantial:

1. Run `git status --short`.
2. Read the current findings note before renaming anything.
3. Avoid touching unrelated user changes.
4. Prefer one strong improvement over five speculative ones.

If the worktree is already dirty, do not revert it. Work around it.

## Choosing A Target

Pick a tractable target with a good chance of producing a useful artifact in
one pass.

Good target types:

- opcode naming or argument-layout improvements
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
rg -n "_opcodeFunctionTable|func_800BB450|func_800BD444|func_800BD6C4|func_800BDC9C" _refs/rood-reverse/src/BATTLE/INITBTL.PRG/12AC.c _refs/rood-reverse/config/BATTLE/BATTLE.PRG/symbol_addrs.txt
```

### Step 4. Trace the consumer path

Do not stop at "this handler writes field X".

Keep going until one of these happens:

- the field consumer clarifies the user-facing meaning
- the decomp becomes nonmatching and blocks certainty
- the script evidence is already strong enough for a conservative local rename

For non-opcode work, the equivalent rule still applies:

- do not stop at one parsed field or one string match
- follow the data until the user-facing meaning becomes clearer

### Step 5. Decide what kind of change is justified

Only choose one of these as the main result:

- `Confirmed rename`
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
- [`ROOD_REVERSE_OPCODE_FINDINGS.md`](ROOD_REVERSE_OPCODE_FINDINGS.md)
- [`GHIDRA_OPCODE_RE_WORKFLOW.md`](GHIDRA_OPCODE_RE_WORKFLOW.md)

Optional if truly useful:

- a short new note with tightly scoped findings
- comments or code changes in `_refs/rood-reverse` if that materially helps the
  next pass or captures an upstreamable RE result

Do not create a giant theory dump unless it directly helps the next pass.
Prefer changes that improve the decoder, the findings trail, or both.

## Verification

Before stopping, verify the result against real data.

Minimum verification:

1. Verify the relevant behavior against at least one strong source, and prefer
   two when practical.
2. Confirm the result is more informative or more accurate than before.
3. Re-read the wording in the findings note and make sure it does not claim
   more than the code proves.

Good verification examples:

- confirm `OpcodeEF` now shows structured fields instead of an opaque blob
- confirm a rename appears correctly in several decoded rooms
- confirm timing or signedness interpretation matches raw bytes
- confirm a runtime theory matches observed behavior in `PCSX-Redux`

## Finish Line

The end state should be "user only has to press commit".

That means:

1. The intended files are edited.
2. The diff is focused.
3. Verification is done.
4. The AI stages the changes it intentionally made in each touched repo.
5. The user is given a clear findings summary.
6. The user is given the exact commit message to use.

Do not run `git commit`.

If unrelated changes already exist in the worktree, stage only the files or
hunks that belong to this pass. Do not stage unrelated user work.

If both repos were changed, provide one commit message per repo and say clearly
which repo each message belongs to.

## Commit Strategy

Use conventional commits.

Good default shapes:

```text
feat(re): clarify opcode 0xEF decoder output
fix(re-notes): tighten evidence for screen effect opcodes
docs(re): capture new opcode findings for 0x7A
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

## Final Report Format

When the pass is complete, report:

1. what question you targeted
2. what evidence changed your confidence
3. which files were updated
4. how you verified it
5. a short summary of the findings in normal prose
6. the exact conventional commit message for each touched repo
7. confirmation that the intended changes are staged in each touched repo

## Avoid

Do not:

- fight headless Ghidra first
- rename multiple weak opcodes in one pass
- convert tentative notes into confident names without proof
- leave the repo with unexplained experimental edits
- end with only "next ideas" and no concrete artifact
- force every pass to be opcode-focused if the better win is elsewhere

## Short Version

Pick one solid RE question. Use the best available tools for that question:
repo scripts, `rg`, `_refs/rood-reverse`, `Ghidra`, or `PCSX-Redux`. Make the
smallest honest improvement that leaves the workspace better than before.
Verify it. Stage the intended changes. Stop in a commit-ready state without
actually committing.

## Kickoff Line

If the next AI needs a one-line mission, use this:

```text
Do one focused RE pass, use the right local tools for the question, turn the result into verified workspace improvements, stage the intended changes, summarize the findings, and stop right before git commit.
```
