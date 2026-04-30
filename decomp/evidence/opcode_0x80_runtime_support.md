# opcode 0x80 Runtime Observation Support Note

## Scope

- Generated from `Pass 3 - Copy/patch reconciliation` on `2026-04-30 20:30:10Z`.
- Observation source: `decomp/evidence/opcode_0x80_runtime_observation.json`
- Baseline export: `decomp/evidence/inittbl_opcode_table.json`
- Runtime table address: `0x800F4C28`
- Reconstructed baseline blob: `decomp/evidence/opcode_0x80_runtime_expected_table.bin` (size `1024` bytes, sha256 `bf98e99d441e94b8bf4d421b59c5994c74b254adbd7736bede778ae0d905b844`)

## Snapshot Comparison

- Missing snapshot file for `after_init`: `decomp/evidence/opcode_0x80_runtime_after_init.bin` (Immediately after the INITBTL copy into 0x800F4C28)
- Missing snapshot file for `pre_dispatch`: `decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin` (Late runtime state before any candidate 0x80-0x82 dispatch)

## Focus Opcode Summary

- No focus-opcode comparison rows were available.

## Planned Breakpoints

- `exec` breakpoint at `0x800BFBB8`: Recovered live runtime table reader
- `exec` breakpoint at `0x800B66E4`: Static stub target for 0x80-0x82
- `exec` breakpoint at `0x800BA2E0`: Competing sound-family candidate
- `write` breakpoint at `0x800F4C28-0x800F5027`: Detect post-init runtime rewrites of the copied table

## Breakpoint Hits

- No breakpoint hits were recorded in the observation JSON yet.

## Table Mutations

- No table mutation observations were recorded yet.

## Dispatch Observations

- No dispatch observations were recorded yet.

## Notes

- No extra runtime notes were recorded yet.

## Conclusion

Runtime observation packet is not finalized yet: no listed snapshot files were available for comparison.
