# External References

This folder is for local clones of outside repositories that help with reverse-engineering, decompilation, and rebuild work.

These repos are **not** required to commit changes to this workspace, and their contents stay ignored by the main repo unless we explicitly decide to vendor or submodule one later.

For `rood-reverse`, the recommended workflow is to keep it as an independent Git checkout under `_refs/`, not as a submodule. That keeps reverse-engineering edits, local commits, and pull requests easy to manage without making this repo track a moving nested dependency.

## Current reference repo

### `rood-reverse`

Upstream:

- <https://github.com/ser-pounce/rood-reverse>

Purpose:

- Vagrant Story PS1 decompilation project
- useful for matching script opcode handlers to engine code
- useful for checking naming, function boundaries, and subsystem behavior in `BATTLE.PRG`, `SLUS_010.40`, and related overlays
- useful as a build and tooling reference for broader PS1 reverse-engineering workflows

Suggested local setup:

```powershell
git clone https://github.com/ser-pounce/rood-reverse.git "_refs/rood-reverse"
```

Recommended Git remote layout for active RE work:

- `upstream` points at `ser-pounce/rood-reverse`
- `origin` points at your fork
- feature branches and PRs go through your fork, while upstream stays the source of truth for sync

If you already cloned directly from upstream, convert the checkout like this after creating your fork:

```powershell
git -C "_refs/rood-reverse" remote rename origin upstream
git -C "_refs/rood-reverse" remote add origin https://github.com/<your-user>/rood-reverse.git
git -C "_refs/rood-reverse" fetch --all --prune
```

Suggested day-to-day flow:

```powershell
git -C "_refs/rood-reverse" switch -c your-topic-branch
git -C "_refs/rood-reverse" add .
git -C "_refs/rood-reverse" commit -m "Describe the RE finding"
git -C "_refs/rood-reverse" push -u origin your-topic-branch
```

Syncing from upstream:

```powershell
git -C "_refs/rood-reverse" fetch upstream
git -C "_refs/rood-reverse" switch main
git -C "_refs/rood-reverse" merge upstream/main
```

## Why this folder exists

Keeping external repos under `_refs/` makes it easier to:

- compare our findings against active decomp work
- script against a known local checkout
- keep research dependencies separate from this repo's own source files

## Why not a submodule here

A submodule would make this parent repo pin a specific `rood-reverse` commit. That is useful for reproducibility, but it adds friction when the checkout is an actively changing RE workspace that we want to commit in directly and use for PRs.

For this repo, a normal clone under `_refs/` is the lower-friction option because it:

- keeps `rood-reverse` history and PR workflow independent
- avoids extra parent-repo commits every time the reference checkout moves
- lets us experiment locally without treating the checkout like a pinned dependency

## If we want stronger Git linkage later

There are three reasonable options:

1. Keep the current approach: document the repo here and clone it locally when needed.
2. Convert it to a Git submodule if we want to pin an exact upstream commit in this repo.
3. Vendor selected files directly only if we actually need local copies under version control.

For now, option 1 is still the best fit for `rood-reverse`.
