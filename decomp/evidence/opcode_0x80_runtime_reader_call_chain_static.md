# Opcode `0x80` Runtime Reader Call-Chain Notes

## Goal

Narrow the next `0x80` runtime trigger by tracing who actually calls the
recovered runtime-table reader `FUN_800BFBB8` instead of treating that reader
as an isolated breakpoint target.

## Evidence used

1. `decomp/evidence/battle_runtime_opcode_table_xrefs.json`
2. `decomp/evidence/battle_runtime_reader_xrefs.json`
3. `decomp/evidence/battle_runtime_reader_caller_xrefs.json`
4. `decomp/evidence/battle_runtime_reader_call_chain_slices.json`
5. `decomp/evidence/battle_runtime_reader_caller_slice.json`
6. `decomp/evidence/opcode_0x80_runtime_automation_summary.json`

## Static call-chain recovery

`battle_runtime_reader_xrefs.json` shows that `FUN_800BFBB8` is not called
from many unrelated places. The current local import recovers exactly two
direct call sites, both from `FUN_800BF850`:

```text
800bfa30 addiu a0,a0,0x4c38
800bfa34 jal 0x800bfbb8
800bfa38 _clear a1

800bfab0 addu a0,v0,s1
800bfab4 lw v0,0x0(a0)
800bfabc beq v0,zero,0x800bfad0
800bfac4 jal 0x800bfbb8
800bfac8 _nop
```

The wider caller slice makes that structure clearer:

- `FUN_800BF850` first checks `lh 0x4c22` and then calls
  `FUN_800BFBB8(a0 = 0x800F4C38, a1 = 0)`.
- It then seeds `s1 = 0x800F4C38`, starts `s0 = 1`, and loops while `s0 < 4`.
- For each iteration it reads a word from `0x800F4C38 + index * 4`; when that
  slot is nonzero it calls `FUN_800BFBB8` again with that slot-derived pointer.

That means the recovered reader already sits under a smaller local dispatch
family than the campaign previously assumed: one base pointer call plus up to
three additional pointer-table entries under `0x800F4C38`.

## One more hop upward

`battle_runtime_reader_caller_xrefs.json` narrows the next layer as well:
`FUN_800BF850` currently has one recovered direct caller at `0x8007A36C`.

The surrounding slice at `0x8007A340` shows a state-gated path rather than a
generic "every frame, always" trampoline:

```text
8007a35c bne v0,zero,0x8007a36c
8007a364 jal 0x8006e7f0
8007a36c jal 0x800bf850
8007a374 lw v1,0x196c(s8)
8007a37c beq v1,s6,0x8007a3bc
8007a384 beq v0,zero,0x8007a39c
8007a39c beq v1,v0,0x8007a3ac
```

The exact semantics of `0x196c(s8)` are still unrecovered locally, but the
important narrowing is already usable: the `0x800F4C28 -> FUN_800BFBB8` reader
path is gated under one concrete upstream `BATTLE.PRG` control-flow region
instead of being a free-floating gameplay breakpoint.

## Runtime consequence

The widened cold-boot bat-control rerun reused the preserved 12-step
`opcode_0x80_runtime_input_plan_bat_kill.json` route and added upstream probe
breakpoints for:

- `0x800BF850` (`reader caller`)
- `0x8007A36C` (`reader grandcaller`)

The refreshed `opcode_0x80_runtime_automation_summary.json` still recorded:

- `reader_hit_count = 0`
- `write_hit_count = 0`
- `candidate_hit_count = 0`
- `probe_hits = []`

So the negative-control result is now stronger than before: early live
gameplay plus the first bat exchange still do not reach the recovered reader,
its direct caller, or the one recovered upstream caller.

## Conclusion

- The next runtime pass should stop asking only "does early gameplay hit
  `0x800BFBB8`?"
- The sharper question is now "what battle-state or script transition reaches
  the `0x8007A36C -> 0x800BF850 -> FUN_800BFBB8` chain, or what later
  alternative reader path bypasses that recovered chain entirely?"
- Near-battle or target-cutscene savestates are still preferred, but if the
  next pass must stay cold-boot, breakpoint expansion should move outward from
  `0x8007A36C` and the `0x800F4C38` pointer family rather than repeating the
  same early-control/bat trigger assumption.
