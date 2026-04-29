from __future__ import annotations

import argparse
import csv
import re
import struct
from collections import defaultdict, deque
from pathlib import Path


ROOM_SECTION_COUNT = 24
SECTION_B_INDEX = 10
SECTION_F_INDEX = 14
MAX_SCENE_ID = 31
DECODED_HEADER_RE = re.compile(
    r"# (MAP\d+)\.MPD\s*\n#\s*(.*?)\s*/\s*(.*?)\s*\(zone=(\d+), room=(\d+), map=MAP\d+\)",
    re.S,
)


def load_decoded_room_index(
    decoded_root: Path,
) -> tuple[dict[str, dict[str, int | str]], dict[tuple[int, int], dict[str, int | str]]]:
    by_map: dict[str, dict[str, int | str]] = {}
    by_zone_room: dict[tuple[int, int], dict[str, int | str]] = {}

    for path in sorted(decoded_root.rglob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = DECODED_HEADER_RE.search(text)
        if match is None:
            continue

        map_id = match.group(1)
        area_name = match.group(2).strip()
        room_name = match.group(3).strip()
        zone_id = int(match.group(4))
        room_id = int(match.group(5))
        record: dict[str, int | str] = {
            "map_id": map_id,
            "area_name": area_name,
            "room_name": room_name,
            "zone_id": zone_id,
            "room_id": room_id,
            "decoded_path": str(path),
        }
        by_map[map_id] = record
        by_zone_room[(zone_id, room_id)] = record

    return by_map, by_zone_room


def read_room_section_lengths(mpd_path: Path) -> tuple[bytes, tuple[int, ...], int]:
    data = mpd_path.read_bytes()
    room_section_offset = struct.unpack_from("<I", data, 0)[0]
    lengths = struct.unpack_from(f"<{ROOM_SECTION_COUNT}I", data, room_section_offset)
    return data, lengths, room_section_offset


def parse_scene_id(mpd_path: Path) -> int | None:
    data, lengths, room_section_offset = read_room_section_lengths(mpd_path)
    section_b_len = lengths[SECTION_B_INDEX]
    if section_b_len < 0x52:
        return None

    section_b_offset = room_section_offset + 0x60 + sum(lengths[:SECTION_B_INDEX])
    return struct.unpack_from("<h", data, section_b_offset + 0x50)[0]


def parse_section_f_room_count(mpd_path: Path) -> int:
    data, lengths, room_section_offset = read_room_section_lengths(mpd_path)
    section_f_len = lengths[SECTION_F_INDEX]
    if section_f_len < 4:
        return 0

    section_f_offset = room_section_offset + 0x60 + sum(lengths[:SECTION_F_INDEX])
    return struct.unpack_from("<I", data, section_f_offset)[0]


def parse_scene_connecting_maps(scene_path: Path) -> set[int]:
    data = scene_path.read_bytes()
    room_count = struct.unpack_from("<I", data, 0)[0]
    room_lengths: list[int] = []

    for index in range(room_count):
        record_offset = 4 + index * 12
        _, room_len, _, _ = struct.unpack_from("<IiHH", data, record_offset)
        room_lengths.append(room_len)

    offset = 4 + room_count * 12
    outgoing_scenes: set[int] = set()

    for room_len in room_lengths:
        room_start = offset

        vertex_count = struct.unpack_from("<I", data, offset)[0]
        offset += 4 + vertex_count * 8

        triangle_count = struct.unpack_from("<I", data, offset)[0]
        offset += 4 + triangle_count * 4

        quad_count = struct.unpack_from("<I", data, offset)[0]
        offset += 4 + quad_count * 4

        line_count_1 = struct.unpack_from("<I", data, offset)[0]
        offset += 4 + line_count_1 * 4

        line_count_2 = struct.unpack_from("<I", data, offset)[0]
        offset += 4 + line_count_2 * 4

        marker_count = struct.unpack_from("<I", data, offset)[0]
        offset += 4

        for _ in range(marker_count):
            vertex_index, target_scene_id, flags, door_id = struct.unpack_from(
                "<BBBB", data, offset
            )
            del vertex_index, door_id
            if flags & 0x04:
                outgoing_scenes.add(target_scene_id)
            offset += 4

        if offset - room_start != room_len:
            raise ValueError(
                f"{scene_path.name}: parsed room payload length 0x{offset - room_start:X} "
                f"does not match table length 0x{room_len:X}"
            )

    return outgoing_scenes


def build_scene_graph(scene_dir: Path) -> dict[int, set[int]]:
    adjacency: dict[int, set[int]] = defaultdict(set)

    for scene_path in sorted(scene_dir.glob("SCEN*.ARM")):
        scene_id = int(scene_path.stem[4:])
        for target_scene_id in sorted(parse_scene_connecting_maps(scene_path)):
            # Scene 0 behaves like a special placeholder bucket, not a real playable area.
            if not (1 <= target_scene_id <= MAX_SCENE_ID):
                continue
            adjacency[scene_id].add(target_scene_id)
            adjacency[target_scene_id].add(scene_id)

    return {scene_id: set(neighbors) for scene_id, neighbors in adjacency.items()}


def build_world_data(
    map_dir: Path,
    decoded_root: Path,
    scene_dir: Path,
) -> tuple[
    dict[int, set[int]],
    dict[str, int | None],
    dict[str, int],
    dict[str, dict[str, int | str]],
]:
    by_map, _ = load_decoded_room_index(decoded_root)
    scene_graph = build_scene_graph(scene_dir)
    map_scene_ids: dict[str, int | None] = {}
    section_f_sizes: dict[str, int] = {}

    for mpd_path in sorted(map_dir.glob("MAP*.MPD")):
        map_id = mpd_path.stem
        map_scene_ids[map_id] = parse_scene_id(mpd_path)
        section_f_sizes[map_id] = parse_section_f_room_count(mpd_path)

    return scene_graph, map_scene_ids, section_f_sizes, by_map


def reachable_scenes_from(start_map: str, map_scene_ids: dict[str, int | None], scene_graph: dict[int, set[int]]) -> set[int]:
    start_scene_id = map_scene_ids.get(start_map)
    if start_scene_id is None or not (1 <= start_scene_id <= MAX_SCENE_ID):
        return set()

    seen = {start_scene_id}
    queue: deque[int] = deque([start_scene_id])

    while queue:
        current_scene_id = queue.popleft()
        for neighbor_scene_id in sorted(scene_graph.get(current_scene_id, ())):
            if neighbor_scene_id in seen:
                continue
            seen.add(neighbor_scene_id)
            queue.append(neighbor_scene_id)

    return seen


def reachable_maps_from(
    reachable_scene_ids: set[int],
    map_scene_ids: dict[str, int | None],
    section_f_sizes: dict[str, int],
    by_map: dict[str, dict[str, int | str]],
) -> set[str]:
    reachable_maps: set[str] = set()

    for map_id, scene_id in map_scene_ids.items():
        area_name = str(by_map.get(map_id, {}).get("area_name", ""))
        is_cutscene_only = section_f_sizes.get(map_id, 0) == 0 and area_name != "Debug"
        if is_cutscene_only:
            continue
        if scene_id in reachable_scene_ids:
            reachable_maps.add(map_id)

    return reachable_maps


def load_room_rows(tsv_path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with tsv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def reorder_columns(fieldnames: list[str], room_type_column: str) -> list[str]:
    ordered: list[str] = []
    preferred = [
        "MapId",
        "ZoneId",
        "RoomId",
        "AreaId",
        room_type_column,
        "AreaName",
        "RoomName",
    ]
    for name in preferred:
        if name in fieldnames and name not in ordered:
            ordered.append(name)
    for name in fieldnames:
        if name not in ordered:
            ordered.append(name)
    return ordered


def update_room_names_tsv(
    tsv_path: Path,
    by_map: dict[str, dict[str, int | str]],
    section_f_sizes: dict[str, int],
    reachable_maps: set[str],
    room_type_column: str,
) -> None:
    rows, fieldnames = load_room_rows(tsv_path)
    fieldnames = [
        name
        for name in fieldnames
        if name not in {"CutsceneOnly", "ConnectedToMAP009", room_type_column}
    ]
    fieldnames.append(room_type_column)

    for row in rows:
        map_id = row["MapId"]
        area_name = row.get("AreaName", "")
        section_f_size = section_f_sizes.get(map_id, 0)
        is_cutscene_only = section_f_size == 0 and area_name != "Debug"
        if area_name == "Debug":
            row[room_type_column] = "Debug"
        elif is_cutscene_only:
            row[room_type_column] = "Cutscene"
        elif map_id in reachable_maps:
            row[room_type_column] = "Playable"
        else:
            row[room_type_column] = "Unknown"

        row.pop("CutsceneOnly", None)
        row.pop("ConnectedToMAP009", None)

    ordered_columns = reorder_columns(fieldnames, room_type_column)
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ordered_columns,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def print_summary(
    start_map: str,
    by_map: dict[str, dict[str, int | str]],
    map_scene_ids: dict[str, int | None],
    section_f_sizes: dict[str, int],
    reachable_scene_ids: set[int],
    reachable_maps: set[str],
) -> None:
    start_label = start_map
    if start_map in by_map:
        start_label = f"{start_map} ({by_map[start_map]['room_name']})"

    start_scene_id = map_scene_ids.get(start_map)
    known_maps = set(by_map)
    cutscene_maps = sorted(
        map_id
        for map_id in known_maps
        if section_f_sizes.get(map_id, 0) == 0 and by_map.get(map_id, {}).get("area_name") != "Debug"
    )
    debug_maps = sorted(
        map_id
        for map_id in known_maps
        if by_map.get(map_id, {}).get("area_name") == "Debug"
    )
    unknown_maps = sorted(
        map_id
        for map_id in known_maps
        if map_id not in reachable_maps
        and map_id not in cutscene_maps
        and map_id not in debug_maps
    )

    print(f"Start map: {start_label}")
    print(f"Start scene: {start_scene_id}")
    print(f"Known decoded maps: {len(known_maps)}")
    print(f"Reachable playable scenes: {len(reachable_scene_ids)}")
    print(f"Playable maps: {len(reachable_maps)}")
    print(f"Cutscene maps: {len(cutscene_maps)}")
    print(f"Debug maps: {len(debug_maps)}")
    print(f"Unknown maps: {len(unknown_maps)}")

    if unknown_maps:
        print("\nUnknown maps:")
        for map_id in unknown_maps:
            area_name = str(by_map.get(map_id, {}).get("area_name", "Unknown"))
            room_name = str(by_map.get(map_id, {}).get("room_name", "Unknown"))
            scene_id = map_scene_ids.get(map_id)
            print(f"- {map_id}\tscene={scene_id}\t{area_name}\t{room_name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify room types from MPD sectionF data and debug labels, then compute "
            "playable-world reachability from a start map using SCEN connecting-map links."
        )
    )
    parser.add_argument(
        "--map-dir",
        type=Path,
        default=Path("Game Data/MAP"),
        help="Directory containing MAP*.MPD files.",
    )
    parser.add_argument(
        "--scene-dir",
        type=Path,
        default=Path("Game Data/SMALL"),
        help="Directory containing SCEN*.ARM files.",
    )
    parser.add_argument(
        "--decoded-root",
        type=Path,
        default=Path("decoded_scripts"),
        help="Directory containing decoded MAP script text files.",
    )
    parser.add_argument(
        "--start-map",
        default="MAP009",
        help="Map ID to use as the reachability root. Default: MAP009.",
    )
    parser.add_argument(
        "--room-names",
        type=Path,
        default=Path("room_names.tsv"),
        help="Path to room_names.tsv.",
    )
    parser.add_argument(
        "--room-type-column",
        default="RoomType",
        help="Column name to use when writing room type back to the TSV.",
    )
    parser.add_argument(
        "--update-tsv",
        action="store_true",
        help="Rewrite room_names.tsv with a RoomType column.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene_graph, map_scene_ids, section_f_sizes, by_map = build_world_data(
        args.map_dir,
        args.decoded_root,
        args.scene_dir,
    )
    reachable_scene_ids = reachable_scenes_from(args.start_map, map_scene_ids, scene_graph)
    reachable_maps = reachable_maps_from(
        reachable_scene_ids,
        map_scene_ids,
        section_f_sizes,
        by_map,
    )
    print_summary(
        args.start_map,
        by_map,
        map_scene_ids,
        section_f_sizes,
        reachable_scene_ids,
        reachable_maps,
    )

    if args.update_tsv:
        update_room_names_tsv(
            args.room_names,
            by_map,
            section_f_sizes,
            reachable_maps,
            args.room_type_column,
        )
        print(f"\nUpdated TSV: {args.room_names}")


if __name__ == "__main__":
    main()
