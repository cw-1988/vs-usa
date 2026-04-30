# Verification Scripts

This folder holds local scripts that compare:

- binary-derived exports
- local decoder tables
- local notes
- helper decomp findings

These scripts should make contradictions visible before we need runtime.

They can also do lighter-weight raw binary sweeps when a full `Ghidra` import
would be premature, such as checking whether any packaged file still contains a
specific absolute MIPS address-access pattern.

## What To Catch Early

Good verification scripts should flag:

- binary exports produced with the wrong import base or wrong overlay
- local names that no longer match binary-derived table entries
- dispatch-table stubs that have nearby orphan candidates with stronger-looking
  behavior
- notes that claim `Confirmed` without a binary or runtime anchor

If a script cannot settle the question, it should still narrow the runtime ask.
The goal is not always to avoid `PCSX-Redux`; it is to arrive there with one
clear contradiction instead of a vague hunch.
