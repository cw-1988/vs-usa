from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_RELATIVE_PATH = "decomp/verification/upgrade_md_json.py"
SCHEMA_VERSION = "mdjson.v8"

BARE_URL_RE = re.compile(r"(?<!\()https?://[^\s>]+")
FILE_REF_RE = re.compile(r"file_:(?P<target>[^\n,;]+?\.md(?:\.json)?(?:#[^\s,;]+)?)(?P<suffix>[:.)]?)")
BACKTICK_MD_PATH_RE = re.compile(r"`(?P<target>[^`\n]+?\.md(?:#[^`\s]+)?)`")
BARE_MD_PATH_RE = re.compile(r"(?<![\w/])(?P<target>(?:\.\./|\./)?[A-Za-z0-9_./-]+\.md(?:#[^\s,;:.)]+)?)(?!\.json)")
LIST_MARKER_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>(?:[-*+])|(?:\d+\.))\s+(?P<text>.+)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})(?P<lang>[^\s`]*)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")

EXCLUDED_PREFIXES = (
    ".codex_tmp/",
    "tools/",
    "_refs/rood-reverse/",
)

GENERATED_KEYS = {
    "schema_version",
    "generated_from",
    "generated_at",
    "source_sha256",
    "raw_markdown",
    "markdown_with_json_links",
    "plain_text",
    "lines",
    "line_count",
    "headings",
    "blocks",
    "links",
    "references",
    "document",
    "body",
    "toc",
    "anchors",
    "sections",
}

REDUNDANT_METADATA_KEYS = {
    "policy_points",
    "objective",
    "overview",
    "abstract",
    "active_snapshot",
    "markdown",
}

SUMMARY_SOURCE_KEYS = (
    "summary",
    "overview",
    "abstract",
    "objective",
    "active_snapshot",
)

EMBEDDED_MARKDOWN_KEYS = (
    "raw_markdown",
    "markdown_with_json_links",
)

TRAILING_FILE_REF_DELIMITERS = ":.)"


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def is_external_target(target: str) -> bool:
    lower = target.lower()
    return lower.startswith(("http://", "https://", "mailto:", "ftp://"))


def json_pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def json_pointer(tokens: list[str]) -> str:
    return "#/" + "/".join(json_pointer_escape(token) for token in tokens)


def resolve_local_target(markdown_path: Path, target: str) -> dict:
    anchor = None
    clean_target = target.strip()
    if clean_target.startswith("<") and clean_target.endswith(">"):
        clean_target = clean_target[1:-1].strip()

    if "#" in clean_target:
        base, anchor = clean_target.split("#", 1)
    else:
        base = clean_target

    if not base:
        return {
            "is_local": False,
            "target_json": clean_target,
            "anchor": anchor,
            "resolved_path": None,
            "target_exists": False,
        }

    resolved = (markdown_path.parent / unquote(base)).resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return {
            "is_local": False,
            "target_json": clean_target,
            "anchor": anchor,
            "resolved_path": None,
            "target_exists": False,
        }

    target_json = f"{relative}.json" if relative.endswith(".md") else relative
    target_json_with_anchor = f"{target_json}#{anchor}" if anchor else target_json
    target_path = REPO_ROOT / target_json
    source_exists = resolved.exists()
    target_exists = target_path.exists() if target_json != relative else source_exists

    return {
        "is_local": True,
        "target_json": target_json_with_anchor,
        "anchor": anchor,
        "resolved_path": relative,
        "target_exists": target_exists,
    }


def should_rewrite_to_json_target(target: str) -> bool:
    clean_target = target.strip()
    if clean_target.startswith("#"):
        return True
    if clean_target.startswith("<") and clean_target.endswith(">"):
        clean_target = clean_target[1:-1].strip()
    base = clean_target.split("#", 1)[0]
    return base.endswith(".md") or base.endswith(".md.json")


def strip_trailing_file_ref_delimiters(target: str) -> tuple[str, str]:
    suffix = ""
    while target and target[-1] in TRAILING_FILE_REF_DELIMITERS:
        suffix = target[-1] + suffix
        target = target[:-1]
    return target, suffix


def rewrite_plain_text_markdown_target(markdown_path: Path, target: str) -> str:
    resolution = resolve_local_target(markdown_path, target)
    if resolution["is_local"] and resolution["target_exists"] and should_rewrite_to_json_target(target):
        return resolution["target_json"]

    clean_target = target.strip()
    anchor = None
    if "#" in clean_target:
        clean_target, anchor = clean_target.split("#", 1)

    if "/" not in clean_target and "\\" not in clean_target and not clean_target.startswith("."):
        root_target_json = (
            f"{clean_target}.json"
            if clean_target.endswith(".md") and not clean_target.endswith(".md.json")
            else clean_target
        )
        root_target_path = REPO_ROOT / root_target_json
        if root_target_path.exists():
            rewritten = root_target_json
            if anchor:
                rewritten = f"{rewritten}#{anchor}"
            return rewritten

    if any(sep in clean_target for sep in ("/", "\\")) and not clean_target.startswith("."):
        repo_relative_target = clean_target
        repo_target_json = (
            f"{repo_relative_target}.json"
            if repo_relative_target.endswith(".md") and not repo_relative_target.endswith(".md.json")
            else repo_relative_target
        )
        repo_target_path = REPO_ROOT / repo_target_json
        if repo_target_path.exists():
            rewritten = repo_target_json
            if anchor:
                rewritten = f"{rewritten}#{anchor}"
            return rewritten

    if any(sep in clean_target for sep in ("/", "\\")) or clean_target.startswith("."):
        return target

    json_name = f"{clean_target}.json" if clean_target.endswith(".md") else clean_target
    matches = [
        path
        for path in sorted(REPO_ROOT.rglob(json_name))
        if not any(repo_relative(path).startswith(prefix) for prefix in EXCLUDED_PREFIXES)
    ]
    if len(matches) != 1:
        return target

    match = matches[0]
    logical_path = match.with_name(match.name[:-5]) if match.name.endswith(".md.json") else match
    rewritten = f"{repo_relative(logical_path)}.json"
    if anchor:
        rewritten = f"{rewritten}#{anchor}"
    return rewritten


def rewrite_plain_text_markdown_mentions(markdown_path: Path, text: str) -> str:
    def replace_backticked(match: re.Match[str]) -> str:
        target = match.group("target")
        rewritten = rewrite_plain_text_markdown_target(markdown_path, target)
        if rewritten == target:
            return match.group(0)
        return f"`{rewritten}`"

    def replace_bare(match: re.Match[str]) -> str:
        target = match.group("target")
        rewritten = rewrite_plain_text_markdown_target(markdown_path, target)
        if rewritten == target:
            return match.group(0)
        return rewritten

    text = BACKTICK_MD_PATH_RE.sub(replace_backticked, text)
    return BARE_MD_PATH_RE.sub(replace_bare, text)


def iter_markdown_links(text: str) -> Iterable[dict]:
    index = 0
    length = len(text)
    while index < length:
        label_start = text.find("[", index)
        if label_start == -1:
            break

        is_image = label_start > 0 and text[label_start - 1] == "!"
        label_end = text.find("]", label_start + 1)
        if label_end == -1 or label_end + 1 >= length or text[label_end + 1] != "(":
            index = label_start + 1
            continue

        target_start = label_end + 2
        depth = 1
        cursor = target_start
        while cursor < length and depth > 0:
            char = text[cursor]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            cursor += 1

        if depth != 0:
            index = label_start + 1
            continue

        full_start = label_start - 1 if is_image else label_start
        yield {
            "is_image": is_image,
            "label": text[label_start + 1 : label_end],
            "target": text[target_start : cursor - 1],
            "start": full_start,
            "end": cursor,
            "full_text": text[full_start:cursor],
        }
        index = cursor


def replace_local_markdown_links(
    markdown_path: Path,
    raw_markdown: str,
    current_heading_pointers: dict[str, str],
    pointer_cache: dict[str, dict],
) -> str:
    pieces: list[str] = []
    cursor = 0
    for match in iter_markdown_links(raw_markdown):
        pieces.append(raw_markdown[cursor : match["start"]])
        target = match["target"]
        if is_external_target(target):
            pieces.append(match["full_text"])
        elif should_rewrite_to_json_target(target):
            converted = rewrite_json_pointer_target(markdown_path, target, current_heading_pointers, pointer_cache)
            prefix = "!" if match["is_image"] else ""
            pieces.append(f"{prefix}[{match['label']}]({converted})")
        else:
            pieces.append(match["full_text"])
        cursor = match["end"]
    pieces.append(raw_markdown[cursor:])
    updated = "".join(pieces)

    def replace_file_ref(match: re.Match[str]) -> str:
        target = match.group("target")
        suffix = match.group("suffix") or ""
        rewritten = rewrite_plain_text_markdown_target(markdown_path, target)
        if rewritten != target:
            return f"file_:{rewritten}{suffix}"
        return match.group(0)

    updated = FILE_REF_RE.sub(replace_file_ref, updated)
    return rewrite_plain_text_markdown_mentions(markdown_path, updated)


def strip_markdown(text: str) -> str:
    rebuilt: list[str] = []
    cursor = 0
    for match in iter_markdown_links(text):
        rebuilt.append(text[cursor : match["start"]])
        rebuilt.append(match["label"])
        cursor = match["end"]
    rebuilt.append(text[cursor:])
    text = "".join(rebuilt)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = text.replace("|", " ")
    return text.strip()


def summarize_inline_text(text: str) -> str:
    summary = " ".join(part.strip() for part in text.splitlines() if part.strip())
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary


def split_rows(lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip().strip("|")
        rows.append([cell.strip() for cell in stripped.split("|")])
    return rows


def dedent_list_item_lines(lines: list[str], content_offset: int) -> list[str]:
    dedented = [lines[0].rstrip()]
    for line in lines[1:]:
        if not line.strip():
            dedented.append("")
            continue
        if len(line) > content_offset:
            dedented.append(line[content_offset:].rstrip())
        else:
            dedented.append(line.lstrip().rstrip())

    while dedented and not dedented[-1].strip():
        dedented.pop()
    return dedented


def parse_blocks(lines: list[str]) -> list[dict]:
    blocks: list[dict] = []
    index = 0
    total = len(lines)

    while index < total:
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            blocks.append(
                {
                    "kind": "heading",
                    "level": len(heading_match.group(1)),
                    "text": heading_match.group(2).strip(),
                    "start_line": index + 1,
                    "end_line": index + 1,
                }
            )
            index += 1
            continue

        fence_match = FENCE_RE.match(line)
        if fence_match:
            fence = fence_match.group("fence")
            language = fence_match.group("lang") or None
            start = index
            index += 1
            code_lines: list[str] = []
            while index < total and not lines[index].startswith(fence):
                code_lines.append(lines[index])
                index += 1
            if index < total:
                index += 1
            blocks.append(
                {
                    "kind": "code",
                    "language": language,
                    "text": "\n".join(code_lines),
                    "start_line": start + 1,
                    "end_line": index,
                }
            )
            continue

        if stripped.startswith("|") and index + 1 < total and TABLE_SEPARATOR_RE.match(lines[index + 1]):
            start = index
            table_lines = [line]
            index += 1
            while index < total and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            blocks.append(
                {
                    "kind": "table",
                    "rows": split_rows(table_lines),
                    "start_line": start + 1,
                    "end_line": index,
                }
            )
            continue

        list_match = LIST_MARKER_RE.match(line)
        if list_match:
            start = index
            ordered = list_match.group("marker").endswith(".")
            items: list[list[dict]] = []
            while index < total:
                candidate = lines[index]
                candidate_match = LIST_MARKER_RE.match(candidate)
                if not candidate_match:
                    break

                indent = len(candidate_match.group("indent"))
                content_offset = candidate.find(candidate_match.group("text"))
                item_lines = [candidate_match.group("text").rstrip()]
                index += 1
                while index < total:
                    follow = lines[index]
                    if not follow.strip():
                        lookahead = index + 1
                        while lookahead < total and not lines[lookahead].strip():
                            lookahead += 1
                        if lookahead >= total:
                            index = lookahead
                            break
                        follow = lines[lookahead]
                        follow_indent = len(follow) - len(follow.lstrip(" "))
                        follow_match = LIST_MARKER_RE.match(follow)
                        if follow_match and follow_indent <= indent:
                            index = lookahead
                            break
                        if follow_indent <= indent:
                            index = lookahead
                            break
                        item_lines.append("")
                        index = lookahead
                        continue
                    follow_match = LIST_MARKER_RE.match(follow)
                    follow_indent = len(follow) - len(follow.lstrip(" "))
                    if follow_match and follow_indent <= indent:
                        break
                    if follow_indent <= indent:
                        break
                    item_lines.append(follow.rstrip())
                    index += 1
                item_blocks = parse_blocks(dedent_list_item_lines(item_lines, content_offset))
                items.append(item_blocks)
                while index < total and not lines[index].strip():
                    index += 1
            blocks.append(
                {
                    "kind": "olist" if ordered else "ulist",
                    "items": items,
                    "start_line": start + 1,
                    "end_line": index,
                }
            )
            continue

        start = index
        paragraph_lines = [line.rstrip()]
        index += 1
        while index < total:
            candidate = lines[index]
            if not candidate.strip():
                break
            if HEADING_RE.match(candidate) or FENCE_RE.match(candidate):
                break
            if candidate.strip().startswith("|") and index + 1 < total and TABLE_SEPARATOR_RE.match(lines[index + 1]):
                break
            if LIST_MARKER_RE.match(candidate):
                break
            paragraph_lines.append(candidate.rstrip())
            index += 1

        blocks.append(
            {
                "kind": "paragraph",
                "text": "\n".join(paragraph_lines).strip(),
                "start_line": start + 1,
                "end_line": index,
            }
        )

    return blocks


def slugify_heading(text: str, slug_counts: dict[str, int]) -> str:
    base = strip_markdown(text).lower()
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"\s+", "-", base).strip("-")
    if not base:
        base = "section"
    count = slug_counts.get(base, 0)
    slug_counts[base] = count + 1
    return base if count == 0 else f"{base}-{count + 1}"


def normalize_content_block(block: dict) -> dict:
    if block["kind"] == "paragraph":
        return {"paragraph": block["text"]}
    if block["kind"] == "code":
        normalized = {"code": block["text"]}
        if block.get("language"):
            normalized["language"] = block["language"]
        return normalized
    if block["kind"] in {"ulist", "olist"}:
        list_key = "olit" if block["kind"] == "olist" else "ulist"
        return {list_key: [normalize_list_item(item) for item in block["items"]]}
    if block["kind"] == "table":
        return {"table": block["rows"]}
    return block


def normalize_list_item(item: object) -> object:
    if isinstance(item, list):
        normalized_blocks = normalize_content_blocks(item)
        if len(normalized_blocks) == 1:
            only_block = normalized_blocks[0]
            if "paragraph" in only_block:
                return only_block["paragraph"]
            return only_block
        return {"content": normalized_blocks}
    if isinstance(item, dict):
        return normalize_content_block(item)
    return item


def collapse_paragraph_runs(blocks: list[dict]) -> list[dict]:
    collapsed: list[dict] = []
    paragraph_run: list[dict] = []

    def flush_paragraph_run() -> None:
        nonlocal paragraph_run
        if len(paragraph_run) >= 2:
            collapsed.append({"ulist": [block["paragraph"] for block in paragraph_run]})
        else:
            collapsed.extend(paragraph_run)
        paragraph_run = []

    for block in blocks:
        if "paragraph" in block and not block["paragraph"].endswith(":"):
            paragraph_run.append(block)
            continue
        flush_paragraph_run()
        collapsed.append(block)

    flush_paragraph_run()
    return collapsed


def is_list_block(block: dict) -> bool:
    return isinstance(block, dict) and ("ulist" in block or "olit" in block)


def get_list_key(block: dict) -> str | None:
    if "ulist" in block:
        return "ulist"
    if "olit" in block:
        return "olit"
    return None


def get_attachable_key(block: dict) -> str | None:
    for key in ("ulist", "olit", "code", "table"):
        if key in block:
            return key
    return None


def merge_bridge_blocks(blocks: list[dict]) -> list[dict]:
    merged: list[dict] = []
    index = 0

    while index < len(blocks):
        current = blocks[index]
        if (
            isinstance(current, dict)
            and "paragraph" in current
            and current["paragraph"].endswith(":")
            and index + 1 < len(blocks)
            and isinstance(blocks[index + 1], dict)
        ):
            follower = blocks[index + 1]
            attachable_key = get_attachable_key(follower)
            if attachable_key is not None:
                if merged and is_list_block(merged[-1]) and attachable_key in {"ulist", "olit"}:
                    list_key = get_list_key(merged[-1])
                    if list_key is not None:
                        merged[-1][list_key].append(current["paragraph"])
                        merged[-1][list_key].append(follower)
                        index += 2
                        continue

                combined = {"paragraph": current["paragraph"], attachable_key: follower[attachable_key]}
                if "language" in follower:
                    combined["language"] = follower["language"]
                merged.append(combined)
                index += 2
                continue

        merged.append(current)
        index += 1

    return merged


def normalize_content_blocks(blocks: list[dict]) -> list[dict]:
    normalized = [normalize_content_block(block) for block in blocks]
    normalized = collapse_paragraph_runs(normalized)
    return merge_bridge_blocks(normalized)


def first_text_value(value: object) -> str | None:
    if isinstance(value, str):
        summary = summarize_inline_text(value)
        return summary or None
    if isinstance(value, dict):
        if "paragraph" in value:
            return first_text_value(value["paragraph"])
        if "code" in value:
            return first_text_value(value["code"])
        for list_key in ("ulist", "olit"):
            if list_key in value and value[list_key]:
                for item in value[list_key]:
                    summary = first_text_value(item)
                    if summary:
                        return summary
        if "content" in value:
            return first_text_value(value["content"])
        if "table" in value and value["table"]:
            for row in value["table"]:
                summary = first_text_value(row)
                if summary:
                    return summary
        if "heading" in value:
            return first_text_value(value["heading"])
    if isinstance(value, list):
        for item in value:
            summary = first_text_value(item)
            if summary:
                return summary
    return None


def infer_summary(existing_content: dict, body: dict) -> str | None:
    for key in SUMMARY_SOURCE_KEYS:
        value = existing_content.get(key)
        if isinstance(value, str):
            summary = summarize_inline_text(value)
            if summary:
                return summary
    summary = first_text_value(body.get("content", []))
    if summary:
        return summary
    for section in body.get("sections", {}).values():
        summary = first_text_value(section.get("content", []))
        if summary:
            return summary
    return None


def build_document_tree(blocks: list[dict], line_count: int) -> tuple[dict, str | None, dict[str, str]]:
    root = {
        "content": [],
        "sections": {},
    }
    stack = [{"node": root, "level": 0, "pointer_tokens": ["body"]}]
    slug_counts: dict[str, int] = {}
    document_title: str | None = None
    heading_pointers: dict[str, str] = {}

    for block in blocks:
        if block["kind"] == "heading":
            level = block["level"]
            slug = slugify_heading(block["text"], slug_counts)
            if level == 1 and document_title is None:
                document_title = block["text"]
                heading_pointers[slug] = json_pointer(["body"])
                stack = [{"node": root, "level": 0, "pointer_tokens": ["body"]}]
                continue

            while len(stack) > 1 and stack[-1]["level"] >= level:
                stack.pop()
            parent = stack[-1]
            section = {
                "heading": block["text"],
                "content": [],
                "sections": {},
                "level": level,
            }
            parent["node"]["sections"][slug] = section
            pointer_tokens = [*parent["pointer_tokens"], "sections", slug]
            heading_pointers[slug] = json_pointer(pointer_tokens)
            stack.append({"node": section, "level": level, "pointer_tokens": pointer_tokens})
            continue

        stack[-1]["node"]["content"].append(block)

    def compact_section(section: dict) -> dict:
        compact = {
            "heading": section["heading"],
        }
        if section["content"]:
            compact["content"] = normalize_content_blocks(section["content"])
        if section["sections"]:
            compact["sections"] = {
                slug: compact_section(child) for slug, child in section["sections"].items()
            }
        return compact

    document = {}
    if root["content"]:
        document["content"] = normalize_content_blocks(root["content"])
    if root["sections"]:
        document["sections"] = {
            slug: compact_section(section) for slug, section in root["sections"].items()
        }
    return document, document_title, heading_pointers


def load_markdown_pointer_map(markdown_path: Path, pointer_cache: dict[str, dict]) -> dict[str, str]:
    cache_key = repo_relative(markdown_path)
    cached = pointer_cache.get(cache_key)
    if cached is not None:
        return cached

    raw_markdown = markdown_path.read_text(encoding="utf-8")
    blocks = parse_blocks(raw_markdown.splitlines())
    _, _, heading_pointers = build_document_tree(blocks, len(raw_markdown.splitlines()))
    pointer_cache[cache_key] = heading_pointers
    return heading_pointers


def rewrite_json_pointer_target(
    markdown_path: Path,
    target: str,
    current_heading_pointers: dict[str, str],
    pointer_cache: dict[str, dict],
) -> str:
    clean_target = target.strip()
    if clean_target.startswith("<") and clean_target.endswith(">"):
        clean_target = clean_target[1:-1].strip()

    if "#" in clean_target:
        base, anchor = clean_target.split("#", 1)
    else:
        base, anchor = clean_target, None

    if not base:
        if not anchor:
            return target
        return current_heading_pointers.get(anchor, target)

    resolved = (markdown_path.parent / unquote(base)).resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return target

    if not relative.endswith(".md"):
        return target

    target_json = f"{relative}.json"
    if not anchor:
        return f"{target_json}#/body"

    if not resolved.exists():
        return f"{target_json}#{anchor}"

    heading_pointers = load_markdown_pointer_map(resolved, pointer_cache)
    pointer = heading_pointers.get(anchor)
    if pointer is None:
        return f"{target_json}#{anchor}"
    return f"{target_json}{pointer}"


def rewrite_block_links(
    body: dict,
    markdown_path: Path,
    current_heading_pointers: dict[str, str],
    pointer_cache: dict[str, dict],
) -> dict:
    def rewrite_text(text: str) -> str:
        return replace_local_markdown_links(markdown_path, text, current_heading_pointers, pointer_cache)

    def rewrite_value(value: object) -> object:
        if isinstance(value, str):
            return rewrite_text(value)
        if isinstance(value, list):
            return [rewrite_value(item) for item in value]
        if isinstance(value, dict):
            return rewrite_content_block(value)
        return value

    def rewrite_content_block(block: dict) -> dict:
        updated = dict(block)
        if "paragraph" in updated:
            updated["paragraph"] = rewrite_text(updated["paragraph"])
        if "table" in updated:
            updated["table"] = [[rewrite_text(cell) for cell in row] for row in updated["table"]]
        if "content" in updated:
            updated["content"] = [rewrite_content_block(item) for item in updated["content"]]
        for list_key in ("ulist", "olit"):
            if list_key in updated:
                updated[list_key] = [rewrite_value(item) for item in updated[list_key]]
        return updated

    def rewrite_section(section: dict) -> dict:
        updated = {
            "heading": section["heading"],
        }
        if section.get("content"):
            updated["content"] = [rewrite_content_block(block) for block in section["content"]]
        if section.get("sections"):
            updated["sections"] = {
                slug: rewrite_section(child) for slug, child in section["sections"].items()
            }
        return updated

    updated_body: dict = {}
    if body.get("content"):
        updated_body["content"] = [rewrite_content_block(block) for block in body["content"]]
    if body.get("sections"):
        updated_body["sections"] = {
            slug: rewrite_section(section) for slug, section in body["sections"].items()
        }
    return updated_body


def rewrite_document_links(
    value: object,
    markdown_path: Path,
    current_heading_pointers: dict[str, str],
    pointer_cache: dict[str, dict],
) -> object:
    if isinstance(value, str):
        return replace_local_markdown_links(markdown_path, value, current_heading_pointers, pointer_cache)
    if isinstance(value, list):
        return [
            rewrite_document_links(item, markdown_path, current_heading_pointers, pointer_cache)
            for item in value
        ]
    if isinstance(value, dict):
        return {
            key: rewrite_document_links(item, markdown_path, current_heading_pointers, pointer_cache)
            for key, item in value.items()
        }
    return value


def infer_title(content: dict, blocks: list[dict], markdown_path: Path, document_title: str | None) -> None:
    if content.get("title"):
        return
    if document_title:
        content["title"] = document_title
        return
    for block in blocks:
        if block["kind"] == "heading" and block["level"] == 1:
            content["title"] = block["text"]
            return
    content["title"] = markdown_path.stem


def read_existing_json(json_path: Path) -> tuple[dict, str | None]:
    if not json_path.exists():
        return {}, None
    before = json_path.read_text(encoding="utf-8")
    return json.loads(before), before


def load_markdown_source(markdown_path: Path, json_path: Path, existing_content: dict) -> str:
    if markdown_path.exists():
        return markdown_path.read_text(encoding="utf-8")
    for key in EMBEDDED_MARKDOWN_KEYS:
        embedded = existing_content.get(key)
        if isinstance(embedded, str) and embedded.strip():
            return embedded
    raise FileNotFoundError(
        f"missing source markdown for {repo_relative(json_path)}; no {markdown_path.name} file or embedded markdown found"
    )


def upgrade_document(markdown_path: Path, json_path: Path, include_raw_markdown: bool) -> bool:
    existing, before = read_existing_json(json_path)

    existing_content = existing.get("content", {})
    content = dict(existing_content)
    raw_markdown = load_markdown_source(markdown_path, json_path, existing_content)
    lines = raw_markdown.splitlines()
    blocks = parse_blocks(lines)
    body, document_title, heading_pointers = build_document_tree(blocks, len(lines))
    pointer_cache: dict[str, dict] = {repo_relative(markdown_path): heading_pointers}
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    for key in GENERATED_KEYS:
        content.pop(key, None)
    for key in REDUNDANT_METADATA_KEYS:
        content.pop(key, None)

    infer_title(content, blocks, markdown_path, document_title)

    content["body"] = body
    content = rewrite_document_links(content, markdown_path, heading_pointers, pointer_cache)
    content["source_markdown_path"] = repo_relative(markdown_path)
    content["schema_version"] = SCHEMA_VERSION
    content["source_sha256"] = hashlib.sha256(raw_markdown.encode("utf-8")).hexdigest()
    summary = infer_summary(existing_content, content["body"])
    if summary:
        summary = replace_local_markdown_links(markdown_path, summary, heading_pointers, pointer_cache)
        content["summary"] = summary
    else:
        content.pop("summary", None)

    if include_raw_markdown:
        content["generated_from"] = SCRIPT_RELATIVE_PATH
        content["generated_at"] = existing_content.get("generated_at", now)
        content["raw_markdown"] = raw_markdown
        content["markdown_with_json_links"] = replace_local_markdown_links(
            markdown_path,
            raw_markdown,
            heading_pointers,
            pointer_cache,
        )

    upgraded = {"content": content}
    rendered = json.dumps(upgraded, indent=2, ensure_ascii=False) + "\n"
    if before == rendered:
        return False

    if include_raw_markdown:
        content["generated_at"] = now
    upgraded = {"content": content}
    rendered = json.dumps(upgraded, indent=2, ensure_ascii=False) + "\n"
    if before == rendered:
        return False

    json_path.write_text(rendered, encoding="utf-8")
    return True


def iter_target_markdown_paths(paths: Iterable[str]) -> list[Path]:
    markdown_paths: list[Path] = []

    def append_markdown_path(path: Path) -> None:
        rel = repo_relative(path)
        if any(rel.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
            return
        markdown_paths.append(path)

    def logical_markdown_path(path: Path) -> Path | None:
        name = path.name
        if name.endswith(".md.json"):
            return path.with_name(name[:-5])
        if name.endswith(".md"):
            return path
        return None

    for raw in paths:
        candidate = (REPO_ROOT / raw).resolve()
        if candidate.exists() and candidate.is_dir():
            for path in sorted(candidate.rglob("*")):
                logical_path = logical_markdown_path(path)
                if logical_path is None:
                    continue
                append_markdown_path(logical_path)
            continue

        logical_path = logical_markdown_path(candidate)
        if logical_path is None and raw.endswith(".md"):
            logical_path = candidate
        if logical_path is not None:
            append_markdown_path(logical_path)

    unique_paths: dict[str, Path] = {}
    for path in markdown_paths:
        unique_paths[repo_relative(path)] = path
    return [unique_paths[key] for key in sorted(unique_paths)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upgrade local .md.json packets to a compact hierarchical markdown schema."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Markdown files, .md.json files, or directories to process. Defaults to the tracked local docs set.",
    )
    parser.add_argument(
        "--include-raw-markdown",
        dest="include_raw_markdown",
        action="store_true",
        help="Embed the source markdown strings for exact reconstruction. This is now the default.",
    )
    parser.add_argument(
        "--no-include-raw-markdown",
        dest="include_raw_markdown",
        action="store_false",
        help="Do not embed source markdown. This makes md.json packets non-self-contained.",
    )
    parser.set_defaults(include_raw_markdown=True)
    args = parser.parse_args()

    default_paths = [
        "AGENTS.md",
        "README.md",
        "RE_CAMPAIGN_MEMORY.md",
        "_refs/README.md",
        "decomp",
        "docs",
    ]

    targets = iter_target_markdown_paths(args.paths or default_paths)
    changed = 0
    for markdown_path in targets:
        json_path = markdown_path.with_name(f"{markdown_path.name}.json")
        if upgrade_document(markdown_path, json_path, include_raw_markdown=args.include_raw_markdown):
            changed += 1
            print(f"updated {repo_relative(json_path)}")

    print(f"processed {len(targets)} markdown files, updated {changed} md.json files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
