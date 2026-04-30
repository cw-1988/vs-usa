## Exploration Policy

Prefer `jcodemunch-mcp` for source-code exploration when symbol-aware lookup,
dependency analysis, or impact tracing will help.

For documentation-first work such as `.md` notes, evidence files, research
logs, and workflow docs, use direct file reads and search first. Do not force
`jcodemunch-mcp` to locate or read markdown files.

If a markdown file points to source code that needs inspection, switch to
`jcodemunch-mcp` for the code portion of the task.

Use the lightest tool that fits:

- symbol lookup: `search_symbols`
- string, comment, and config lookup: `search_text`
- repo and file layout: `get_repo_outline`, `get_file_tree`
- symbol and file reading: `get_file_outline`, `get_symbol_source`,
  `get_context_bundle`
- usage and impact: `find_references`, `find_importers`,
  `get_dependency_graph`, `get_blast_radius`

## Session Routing

1. Run `resolve_repo { "path": "." }` when the task includes code exploration.
2. Use `suggest_queries` only when the repo is unfamiliar and the task is
   code-heavy.
3. Use `plan_turn` only for code-focused tasks where ranked symbol or file
   suggestions are likely to help.
4. Skip `plan_turn` for markdown-only work, process questions, and tooling
   meta-discussion.

## Working Rules

- If `search_symbols` reports `negative_evidence`, treat that as "not found"
  instead of repeatedly re-searching with slight wording changes.
- If `_meta` includes `budget_warning`, stop exploring and work with the
  context already gathered.
- Use `get_session_context` to avoid rereading the same code context.
- After edits, call `register_edit` when auto-reindex hooks are unavailable.
- For bulk edits across 5 or more files, batch them in one `register_edit`
  call.
