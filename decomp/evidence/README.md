# Decomp Evidence

Store machine-readable exported evidence here.

Examples:

- opcode table JSON exports
- function coverage reports
- contradiction reports
- small proof packets for disputed opcodes

For disputed opcode families, prefer this split:

- one summary proof packet that states inputs, produced artifacts, and current
  conclusion
- separate narrowly scoped support notes for copy paths, xref gaps, or nearby
  competing handlers

That keeps the summary packet durable without turning every support note into a
second copy of the whole argument.

Keep these artifacts small and text-based when possible.

Each proof packet should try to include:

- exact binary input
- relevant base address or table address
- produced export files
- short conclusion
- open conflicts, if any
