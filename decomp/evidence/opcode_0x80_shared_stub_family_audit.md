# Opcode `0x80` Shared Stub Family Audit

## Goal

Make the widened `0x800B66E4` family explicit so future naming work does not
mistake one shared `INITBTL.PRG` table target for direct user-facing proof of
dialog, room, music, or sound semantics.

## Static family membership

`decomp/evidence/inittbl_opcode_table.json` maps `30` opcode slots to the same
`INITBTL.PRG` handler address `0x800B66E4`:

- Named or semi-named members:
  `0x10` (`DialogShow`), `0x11` (`DialogText`), `0x22` (`ModelAnimate`),
  `0x44` (`SetEngineMode`), `0x54` (`BattleOver`), `0x69` (`LoadScene`),
  `0x6D` (`DisplayRoom`), `0x80` (`Opcode80SharedStub`), and
  `0x92` (`MusicPlay`)
- Placeholder-heavy remainder:
  `0x13`, `0x32`, `0x35`, `0x36`, `0x43`, `0x48`, `0x81`, `0x82`, `0x8F`,
  `0x93`, `0x94`, `0x95`, `0x96`, `0x97`, `0x98`, `0x9B`, `0x9C`, `0x9F`,
  `0xA9`, and `0xBB`

The current local `BATTLE.PRG` slice in
`decomp/evidence/battle_0x80_handler_slices.json` still shows the target as a
two-instruction return-zero stub:

```text
800b66e4 jr ra
800b66e8 clear v0
```

## Why the widened family matters

- The same stub now spans currently named dialog, model, engine-mode, room,
  battle-end, and music-looking opcode slots in this table.
- That means the `INITBTL.PRG` table hit is structural dispatch evidence, not
  standalone proof that any one member of the family has a direct user-facing
  meaning tied to `0x800B66E4`.
- For `0x80` specifically, the widened family removes the last remaining
  "maybe this one stub slot is secretly sound-special" intuition.
  A sound-only reading is now less plausible because the same slot also owns
  clearly non-audio neighborhoods in the same export.

## Retail runtime cross-check

The validated `MAP001` listener-control packet keeps the widened family from
being just a static-export curiosity:

- `decomp/evidence/opcode_0x80_runtime_automation_summary.json` records a
  handler-probe plan that groups
  `0x10`, `0x11`, `0x22`, `0x69`, `0x6A`, `0x6D`, `0x80`, `0x82`, `0x92`,
  `0xA9`, and `0xBB` under `0x800B66E4`
- The same checked retail run directly observes non-`0x80` members landing on
  that stub in the live copied runtime table:
  `0x10 x1`, `0x13 x5`, `0x44 x7`, and `0x80 x1`

That confirms the shared-family interpretation on retail runtime for more than
just the `0x80-0x82` trio.

## Safe campaign consequence

- Keep `0x80` on the structural label `Opcode80SharedStub`.
- Do not cite `0x800B66E4` table membership by itself as proof for
  `DialogShow`, `DialogText`, `ModelAnimate`, `SetEngineMode`, `BattleOver`,
  `LoadScene`, `DisplayRoom`, `MusicPlay`, or any placeholder member in this
  family.
- Treat this audit as a guardrail: shared-stub membership is a "do not
  overclaim" fact, not a family-wide rollback order.
- The next semantic pass for `0x80` should explain the surrounding
  audio-looking script sites through neighboring confirmed sound-family
  opcodes, prepared state, or other consumer paths, not by reviving the old
  `SoundEffects0` label.
