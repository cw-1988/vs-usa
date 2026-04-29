#!/usr/bin/env python3
from __future__ import annotations

import argparse
import struct
from pathlib import Path


OPCODES = {
    0x00: ("nop", 0x01),
    0x01: ("Opcode01", 0x0A),
    0x02: ("Opcode02", 0x03),
    0x03: ("Opcode03", 0x03),
    0x04: ("Opcode04", 0x04),
    0x05: ("Opcode05", 0x12),
    0x06: ("Opcode06", 0x0B),
    0x07: ("Opcode07", 0x0B),
    0x08: ("Opcode08", 0x26),
    0x09: ("Opcode09", 0x00),
    0x0A: ("Opcode0A", 0x01),
    0x0B: ("Opcode0B", 0x01),
    0x0C: ("Opcode0C", 0x01),
    0x0D: ("Opcode0D", 0x03),
    0x0E: ("Opcode0E", 0x03),
    0x0F: ("Opcode0F", 0x01),
    0x10: ("DialogShow", 0x0B),
    0x11: ("DialogText", 0x04),
    0x12: ("DialogHide", 0x02),
    0x13: ("Opcode13", 0x09),
    0x14: ("Opcode14", 0x02),
    0x15: ("Opcode15", 0x02),
    0x16: ("SplashScreenChoose", 0x04),
    0x17: ("SplashScreenLoad", 0x06),
    0x18: ("SplashScreenShow", 0x07),
    0x19: ("SplashScreenHide", 0x01),
    0x1A: ("SplashScreenFadeIn", 0x01),
    0x1B: ("Opcode1B", 0x04),
    0x1C: ("Opcode1C", 0x02),
    0x1D: ("Opcode1D", 0x02),
    0x1E: ("Opcode1E", 0x04),
    0x1F: ("Opcode1F", 0x05),
    0x20: ("ModelLoad", 0x09),
    0x21: ("Opcode21", 0x06),
    0x22: ("ModelAnimate", 0x06),
    0x23: ("ModelSetAnimations", 0x05),
    0x24: ("Opcode24", 0x07),
    0x25: ("Opcode25", 0x09),
    0x26: ("ModelPosition", 0x0C),
    0x27: ("Opcode27", 0x07),
    0x28: ("ModelMoveTo", 0x0A),
    0x29: ("ModelMoveTo2", 0x07),
    0x2A: ("Opcode2A", 0x07),
    0x2B: ("Opcode2B", 0x06),
    0x2C: ("Opcode2C", 0x06),
    0x2D: ("Opcode2D", 0x07),
    0x2E: ("ModelScale", 0x0A),
    0x2F: ("ModeFree", 0x03),
    0x30: ("ModelLoadAnimationsEx", 0x06),
    0x31: ("ModelTint", 0x06),
    0x32: ("Opcode32", 0x06),
    0x33: ("ModelRotate", 0x0B),
    0x34: ("Opcode34", 0x08),
    0x35: ("Opcode35", 0x07),
    0x36: ("Opcode36", 0x07),
    0x37: ("Opcode37", 0x05),
    0x38: ("ModelLookAt", 0x06),
    0x39: ("ModelLookAtPosition", 0x0A),
    0x3A: ("ModelLoadAnimations", 0x04),
    0x3B: ("WaitForFile", 0x01),
    0x3C: ("Opcode3C", 0x02),
    0x3D: ("Opcode3D", 0x02),
    0x3E: ("ModelIlluminate", 0x0A),
    0x3F: ("Opcode3F", 0x04),
    0x40: ("JumpFwdIfFlag", 0x06),
    0x41: ("Opcode41", 0x06),
    0x42: ("ModelControlViaScript", 0x03),
    0x43: ("Opcode43", 0x01),
    0x44: ("SetEngineMode", 0x02),
    0x45: ("Opcode45", 0x03),
    0x46: ("Opcode46", 0x03),
    0x47: ("Opcode47", 0x04),
    0x48: ("Opcode48", 0x01),
    0x49: ("Opcode49", 0x03),
    0x4A: ("Opcode4A", 0x04),
    0x4B: ("Opcode4B", 0x03),
    0x4C: ("Opcode4C", 0x03),
    0x4D: ("Opcode4D", 0x02),
    0x4E: ("Opcode4E", 0x01),
    0x4F: ("Opcode4F", 0x01),
    0x50: ("ModelControlViaBattleMode", 0x04),
    0x51: ("Opcode51", 0x04),
    0x52: ("Opcode52", 0x05),
    0x53: ("Opcode53", 0x03),
    0x54: ("BattleOver", 0x04),
    0x55: ("Opcode55", 0x02),
    0x56: ("Opcode56", 0x03),
    0x57: ("Opcode57", 0x04),
    0x58: ("SetHeadsUpDisplayMode", 0x02),
    0x59: ("Opcode59", 0x04),
    0x5A: ("Opcode5A", 0x07),
    0x5B: ("Opcode5B", 0x04),
    0x5C: ("Opcode5C", 0x07),
    0x5D: ("Opcode5D", 0x04),
    0x5E: ("Opcode5E", 0x03),
    0x5F: ("Opcode5F", 0x02),
    0x60: ("Opcode60", 0x03),
    0x61: ("Opcode61", 0x03),
    0x62: ("Opcode62", 0x02),
    0x63: ("Opcode63", 0x01),
    0x64: ("Opcode64", 0x02),
    0x65: ("Opcode65", 0x02),
    0x66: ("Opcode66", 0x03),
    0x67: ("Opcode67", 0x05),
    0x68: ("LoadRoom", 0x0A),
    0x69: ("LoadScene", 0x04),
    0x6A: ("Opcode6A", 0x04),
    0x6B: ("Opcode6B", 0x02),
    0x6C: ("Opcode6C", 0x04),
    0x6D: ("DisplayRoom", 0x02),
    0x6E: ("Opcode6E", 0x01),
    0x6F: ("Opcode6F", 0x02),
    0x70: ("ModelColor", 0x08),
    0x71: ("Opcode71", 0x04),
    0x72: ("Opcode72", 0x03),
    0x73: ("Opcode73", 0x02),
    0x74: ("LoadRoomSection10", 0x02),
    0x75: ("WaitForRoomSection10", 0x01),
    0x76: ("FreeRoomSection10", 0x01),
    0x77: ("Opcode77", 0x05),
    0x78: ("Opcode78", 0x02),
    0x79: ("RoomMechanismControl", 0x03),
    0x7A: ("Opcode7A", 0x02),
    0x7B: ("Opcode7B", 0x05),
    0x7C: ("SetFirstPersonView", 0x02),
    0x7D: ("Opcode7D", 0x03),
    0x7E: ("Opcode7E", 0x04),
    0x7F: ("Opcode7F", 0x01),
    0x80: ("SoundEffects0", 0x05),
    0x81: ("Opcode81", 0x04),
    0x82: ("Opcode82", 0x05),
    0x83: ("Opcode83", 0x01),
    0x84: ("Opcode84", 0x03),
    0x85: ("LoadSfxSlot", 0x03),
    0x86: ("FreeSfxSlot", 0x02),
    0x87: ("Opcode87", 0x02),
    0x88: ("SetCurrentSfx", 0x02),
    0x89: ("Opcode89", 0x01),
    0x8A: ("Opcode8A", 0x00),
    0x8B: ("Opcode8B", 0x00),
    0x8C: ("Opcode8C", 0x00),
    0x8D: ("Opcode8D", 0x00),
    0x8E: ("Opcode8E", 0x00),
    0x8F: ("Opcode8F", 0x05),
    0x90: ("LoadMusicSlot", 0x03),
    0x91: ("FreeMusic", 0x02),
    0x92: ("MusicPlay", 0x04),
    0x93: ("Opcode93", 0x03),
    0x94: ("Opcode94", 0x03),
    0x95: ("Opcode95", 0x03),
    0x96: ("Opcode96", 0x01),
    0x97: ("Opcode97", 0x02),
    0x98: ("Opcode98", 0x01),
    0x99: ("ClearMusicLoadSlot", 0x02),
    0x9A: ("Opcode9A", 0x03),
    0x9B: ("Opcode9B", 0x05),
    0x9C: ("Opcode9C", 0x05),
    0x9D: ("LoadSoundFile2", 0x02),
    0x9E: ("ProcessSoundQueue", 0x01),
    0x9F: ("Opcode9F", 0x02),
    0xA0: ("OpcodeA0", 0x05),
    0xA1: ("SplashScreenEffects", 0x02),
    0xA2: ("CameraZoomIn", 0x02),
    0xA3: ("OpcodeA3", 0x01),
    0xA4: ("OpcodeA4", 0x01),
    0xA5: ("OpcodeA5", 0x01),
    0xA6: ("OpcodeA6", 0x02),
    0xA7: ("OpcodeA7", 0x00),
    0xA8: ("OpcodeA8", 0x02),
    0xA9: ("OpcodeA9", 0x02),
    0xAA: ("OpcodeAA", 0x05),
    0xAB: ("OpcodeAB", 0x00),
    0xAC: ("OpcodeAC", 0x00),
    0xAD: ("OpcodeAD", 0x00),
    0xAE: ("OpcodeAE", 0x00),
    0xAF: ("OpcodeAF", 0x00),
    0xB0: ("OpcodeB0", 0x00),
    0xB1: ("OpcodeB1", 0x02),
    0xB2: ("OpcodeB2", 0x08),
    0xB3: ("OpcodeB3", 0x04),
    0xB4: ("OpcodeB4", 0x07),
    0xB5: ("OpcodeB5", 0x03),
    0xB6: ("OpcodeB6", 0x07),
    0xB7: ("OpcodeB7", 0x06),
    0xB8: ("OpcodeB8", 0x01),
    0xB9: ("OpcodeB9", 0x03),
    0xBA: ("OpcodeBA", 0x02),
    0xBB: ("OpcodeBB", 0x03),
    0xBC: ("OpcodeBC", 0x01),
    0xBD: ("OpcodeBD", 0x02),
    0xBE: ("OpcodeBE", 0x01),
    0xBF: ("OpcodeBF", 0x03),
    0xC0: ("CameraDirection", 0x07),
    0xC1: ("CameraSetAngle", 0x01),
    0xC2: ("CameraLookAt", 0x03),
    0xC3: ("OpcodeC3", 0x03),
    0xC4: ("ModelAnimateObject", 0x04),
    0xC5: ("OpcodeC5", 0x09),
    0xC6: ("OpcodeC6", 0x00),
    0xC7: ("OpcodeC7", 0x0A),
    0xC8: ("OpcodeC8", 0x0B),
    0xC9: ("OpcodeC9", 0x02),
    0xCA: ("OpcodeCA", 0x0A),
    0xCB: ("OpcodeCB", 0x03),
    0xCC: ("OpcodeCC", 0x00),
    0xCD: ("OpcodeCD", 0x00),
    0xCE: ("OpcodeCE", 0x00),
    0xCF: ("OpcodeCF", 0x00),
    0xD0: ("CameraPosition", 0x07),
    0xD1: ("SetCameraPosition", 0x01),
    0xD2: ("OpcodeD2", 0x03),
    0xD3: ("OpcodeD3", 0x03),
    0xD4: ("CameraHeight", 0x04),
    0xD5: ("OpcodeD5", 0x09),
    0xD6: ("OpcodeD6", 0x00),
    0xD7: ("OpcodeD7", 0x0A),
    0xD8: ("OpcodeD8", 0x0B),
    0xD9: ("OpcodeD9", 0x02),
    0xDA: ("OpcodeDA", 0x0A),
    0xDB: ("OpcodeDB", 0x03),
    0xDC: ("OpcodeDC", 0x00),
    0xDD: ("OpcodeDD", 0x00),
    0xDE: ("OpcodeDE", 0x02),
    0xDF: ("OpcodeDF", 0x02),
    0xE0: ("CameraWait", 0x02),
    0xE1: ("OpcodeE1", 0x02),
    0xE2: ("CameraAngleTweenA", 0x06),
    0xE3: ("CameraAngleTweenB", 0x06),
    0xE4: ("OpcodeE4", 0x05),
    0xE5: ("OpcodeE5", 0x06),
    0xE6: ("OpcodeE6", 0x05),
    0xE7: ("OpcodeE7", 0x02),
    0xE8: ("OpcodeE8", 0x03),
    0xE9: ("OpcodeE9", 0x03),
    0xEA: ("CameraZoom", 0x04),
    0xEB: ("OpcodeEB", 0x04),
    0xEC: ("CameraZoomScalar", 0x04),
    0xED: ("OpcodeED", 0x05),
    0xEE: ("OpcodeEE", 0x00),
    0xEF: ("OpcodeEF", 0x06),
    0xF0: ("Wait", 0x02),
    0xF1: ("OpcodeF1", 0x02),
    0xF2: ("OpcodeF2", 0x05),
    0xF3: ("OpcodeF3", 0x02),
    0xF4: ("ScriptCallSlotActive", 0x02),
    0xF5: ("ScriptCall", 0x04),
    0xF6: ("ScriptReturn", 0x02),
    0xF7: ("OpcodeF7", 0x03),
    0xF8: ("OpcodeF8", 0x01),
    0xF9: ("OpcodeF9", 0x01),
    0xFA: ("OpcodeFA", 0x01),
    0xFB: ("OpcodeFB", 0x01),
    0xFC: ("OpcodeFC", 0x01),
    0xFD: ("OpcodeFD", 0x01),
    0xFE: ("OpcodeFE", 0x01),
    0xFF: ("return", 0x01),
}

TBL_SINGLE = {
    **{i: str(i) for i in range(10)},
    **{0x0A + i: chr(ord("A") + i) for i in range(26)},
    **{0x24 + i: chr(ord("a") + i) for i in range(26)},
    0x40: "Ć",
    0x41: "Â",
    0x42: "Ä",
    0x43: "Ç",
    0x44: "È",
    0x45: "É",
    0x46: "Ê",
    0x47: "Ë",
    0x48: "Ì",
    0x49: "ő",
    0x4A: "Î",
    0x4B: "í",
    0x4C: "Ò",
    0x4D: "Ó",
    0x4E: "Ô",
    0x4F: "Ö",
    0x50: "Ù",
    0x51: "Ú",
    0x52: "Û",
    0x53: "Ü",
    0x54: "ß",
    0x55: "æ",
    0x56: "à",
    0x57: "á",
    0x58: "â",
    0x59: "ä",
    0x5A: "ç",
    0x5B: "è",
    0x5C: "é",
    0x5D: "ê",
    0x5E: "ë",
    0x5F: "ì",
    0x60: "í",
    0x61: "î",
    0x62: "ï",
    0x63: "ò",
    0x64: "ó",
    0x65: "ô",
    0x66: "ö",
    0x67: "ù",
    0x68: "ú",
    0x69: "û",
    0x6A: "ü",
    0x87: "‼",
    0x88: "≠",
    0x89: "≦",
    0x8A: "≧",
    0x8B: "÷",
    0x8C: "-",
    0x8D: "—",
    0x8E: "⋯",
    0x90: "!",
    0x91: '"',
    0x92: "#",
    0x93: "$",
    0x94: "%",
    0x95: "&",
    0x96: "'",
    0x97: "(",
    0x98: ")",
    0x99: "{",
    0x9A: "}",
    0x9B: "[",
    0x9C: "]",
    0x9D: ";",
    0x9E: ":",
    0x9F: ",",
    0xA0: ".",
    0xA1: "/",
    0xA2: "\\",
    0xA3: "<",
    0xA4: ">",
    0xA5: "?",
    0xA6: "_",
    0xA7: "-",
    0xA8: "+",
    0xA9: "*",
    0xAB: "{",
    0xAC: "}",
    0xAD: "♪",
}

TBL_DOUBLE = {
    (0xF8, 0x01): "«p1»",
    (0xF8, 0x02): "«p2»",
    (0xF8, 0x08): "«p8»",
    (0xF8, 0x0A): "«p10»",
    (0xFA, 0x06): " ",
}


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def s16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<h", data, offset)[0]


def decode_text(raw: bytes) -> str:
    out: list[str] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if b == 0xE7:
            break
        if b == 0xEB:
            i += 1
            continue
        if b == 0xE8:
            out.append("\\n")
            i += 1
            continue
        if i + 1 < len(raw) and (b, raw[i + 1]) in TBL_DOUBLE:
            out.append(TBL_DOUBLE[(b, raw[i + 1])])
            i += 2
            continue
        out.append(TBL_SINGLE.get(b, f"<{b:02X}>"))
        i += 1
    return "".join(out)


def parse_dialogs(section: bytes, ptr_dialog: int, dialog_limit: int) -> list[str]:
    count = u16(section, ptr_dialog)
    if count == 0:
        return []

    table_base = ptr_dialog
    first_text_rel = count * 2
    rel_offsets = [first_text_rel]
    for i in range(count - 1):
        rel_offsets.append(u16(section, table_base + 2 + i * 2))

    dialogs: list[str] = []
    for rel in rel_offsets:
        start = table_base + rel
        end = start
        while end < dialog_limit and section[end] != 0xE7:
            end += 1
        if end < dialog_limit:
            end += 1
        dialogs.append(decode_text(section[start:end]))
    return dialogs


def hex_bytes(blob: bytes) -> str:
    return " ".join(f"{b:02X}" for b in blob)


def fmt_default(args: bytes) -> str:
    return ", ".join(str(b) for b in args) if args else ""


def fmt_signed_pair(lo: int, hi: int) -> int:
    return struct.unpack("<h", bytes([lo, hi]))[0]


def format_opcode(op: int, args: bytes, dialogs: list[str]) -> str:
    if op == 0x10 and len(args) == 10:
        return (
            f"idDlg={args[0]}, style={args[1]}, x={args[2]}, y={args[4]}, "
            f"w={args[5]}, h={args[6]}, raw=[{fmt_default(args[7:])}]"
        )
    if op == 0x11 and len(args) == 3:
        text = dialogs[args[1]] if args[1] < len(dialogs) else "<missing>"
        return f"idDlg={args[0]}, idText={args[1]}, raw={args[2]} ; \"{text}\""
    if op == 0x12 and len(args) == 1:
        return f"idDlg={args[0]}"
    if op == 0x20 and len(args) == 8:
        return f"idChr={args[0]}, unk1={args[1]}, idSHP={args[2]}, raw=[{fmt_default(args[3:])}]"
    if op == 0x22 and len(args) == 5:
        return f"idChr={args[0]}, unk1={args[1]}, idAnim={args[2]}, raw=[{fmt_default(args[3:])}]"
    if op == 0x26 and len(args) == 11:
        px = fmt_signed_pair(args[2], args[3])
        py = fmt_signed_pair(args[4], args[5])
        pz = fmt_signed_pair(args[6], args[7])
        return f"idChr={args[0]}, unk1={args[1]}, pos=({px}, {py}, {pz}), rx={args[8]}, raw=[{fmt_default(args[9:])}]"
    if op == 0x28 and len(args) == 9:
        x = struct.unpack("<i", args[1:5])[0]
        y = struct.unpack("<i", args[5:9])[0]
        return f"idChr={args[0]}, x={x}, y={y}"
    if op == 0x33 and len(args) == 10:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x38 and len(args) == 5:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x40 and len(args) == 5:
        flag_id = (args[1] >> 2) | ((args[0] & 0x0F) << 6)
        compare_value = args[2]
        jump = struct.unpack("<H", args[3:5])[0]
        mode = {
            0x00: "<",
            0x10: ">",
            0x20: "==",
            0x30: "!=",
            0x40: ">=",
            0x50: "<=",
            0x60: "&",
        }.get(args[0] & 0xF0, f"mode=0x{args[0] & 0xF0:02X}")
        return f"flag={flag_id}, cmp={mode} {compare_value}, jump=+0x{jump:X}"
    if op == 0x3A and len(args) == 3:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x44 and len(args) == 1:
        return f"idMode={args[0]}"
    if op == 0x54:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x58 and len(args) == 1:
        return f"idMode={args[0]}"
    if op == 0x68 and len(args) == 9:
        return f"idZone={args[0]}, idRoom={args[1]}, raw=[{fmt_default(args[2:])}]"
    if op == 0x69:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x6D and len(args) == 1:
        return f"raw={args[0]}"
    if op == 0x79 and len(args) == 2:
        action = {
            0: "trigger",
            1: "toggle",
        }.get(args[0], f"action={args[0]}")
        return f"action={action}, idMechanism={args[1]}"
    if op in {0x80, 0x82, 0x8F, 0x9B, 0x9C, 0xA0, 0xAA, 0xB2, 0xB4, 0xB6, 0xC5, 0xD5, 0xE2, 0xE3, 0xE5, 0xEF, 0xF2}:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x90 and len(args) == 2:
        return f"slot={args[0]}, raw={args[1]}"
    if op == 0x92 and len(args) == 3:
        return f"raw=[{fmt_default(args)}]"
    if op == 0x99 and len(args) == 1:
        return f"slot={args[0]}"
    if op == 0x9D and len(args) == 1:
        return f"idFile={args[0]}"
    if op == 0xA2 and len(args) == 1:
        return f"raw={args[0]}"
    if op == 0xC0 and len(args) == 6:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xC2 and len(args) == 2:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xC4 and len(args) == 3:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xD0 and len(args) == 6:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xD4 and len(args) == 3:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xE0 and len(args) == 1:
        return f"raw={args[0]}"
    if op in {0xEA, 0xEB, 0xEC} and len(args) == 3:
        return f"raw=[{fmt_default(args)}]"
    if op == 0xF0 and len(args) == 1:
        return f"frames={args[0]}"
    return fmt_default(args)


def disassemble(mpd_path: Path) -> str:
    data = mpd_path.read_bytes()
    ptr_script, len_script = struct.unpack_from("<II", data, 0x10)
    section = data[ptr_script : ptr_script + len_script]
    if len(section) < 0x10:
        raise ValueError("Script section too short")

    section_len, ptr_dialog, ptr_unknown1, ptr_unknown2, unk1, unk2, unk3, unk4 = struct.unpack_from("<8H", section, 0)
    dialog_limit_candidates = [x for x in (ptr_unknown1, ptr_unknown2, len(section)) if x]
    dialog_limit = min(dialog_limit_candidates) if dialog_limit_candidates else len(section)
    dialogs = parse_dialogs(section, ptr_dialog, dialog_limit) if ptr_dialog else []

    lines = [
        f"# {mpd_path.name}",
        f"script_section_offset=0x{ptr_script:X}",
        f"script_section_length=0x{len_script:X} ({len_script})",
        "",
        "[script_header]",
        f"section_len=0x{section_len:X}",
        f"ptr_dialog_text=0x{ptr_dialog:X}",
        f"ptr_unknown1=0x{ptr_unknown1:X}",
        f"ptr_unknown2=0x{ptr_unknown2:X}",
        f"unknown_words=[0x{unk1:X}, 0x{unk2:X}, 0x{unk3:X}, 0x{unk4:X}]",
        "",
        "[opcodes]",
    ]

    offset = 0x10
    while offset < ptr_dialog:
        op = section[offset]
        name, size = OPCODES[op]
        raw = section[offset : offset + max(size, 1)]
        if size == 0:
            lines.append(f"{offset:04X}: {hex_bytes(raw[:1])}  {name}  ; size=0 in current docs, cannot advance safely")
            break
        args = section[offset + 1 : offset + size]
        rendered = format_opcode(op, args, dialogs)
        lines.append(f"{offset:04X}: {hex_bytes(raw):<35} {name}({rendered})")
        offset += size

    lines.append("")
    lines.append("[dialogs]")
    if not dialogs:
        lines.append("<none>")
    else:
        for idx, text in enumerate(dialogs):
            lines.append(f"{idx:02d}: {text}")

    return "\n".join(lines)


def collect_inputs(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.glob("MAP*.MPD"))
    raise FileNotFoundError(f"Input path not found: {path}")


def output_path_for(input_path: Path, source_root: Path, output_root: Path) -> Path:
    try:
        rel = input_path.relative_to(source_root)
        stem = rel.stem
    except ValueError:
        stem = input_path.stem
    return output_root / f"{stem}_script.txt"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Disassemble the ScriptSection of one MPD file or a directory of MAP*.MPD files."
    )
    parser.add_argument("mpd", type=Path, help="Path to MAPxxx.MPD or a directory containing MAP*.MPD")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write output to this file (single input) or directory (batch input)",
    )
    args = parser.parse_args()

    inputs = collect_inputs(args.mpd)
    if not inputs:
        raise FileNotFoundError(f"No MAP*.MPD files found in: {args.mpd}")

    batch_mode = len(inputs) > 1 or args.mpd.is_dir()
    if batch_mode:
        output_root = args.output if args.output else Path("decoded_scripts")
        output_root.mkdir(parents=True, exist_ok=True)
        written = 0
        skipped: list[tuple[Path, str]] = []
        for mpd_path in inputs:
            try:
                text = disassemble(mpd_path)
            except ValueError as exc:
                skipped.append((mpd_path, str(exc)))
                continue
            out_path = output_path_for(mpd_path, args.mpd if args.mpd.is_dir() else mpd_path.parent, output_root)
            out_path.write_text(text, encoding="utf-8")
            written += 1
        print(f"Wrote {written} decoded scripts to {output_root}")
        if skipped:
            print(f"Skipped {len(skipped)} files:")
            for mpd_path, reason in skipped:
                print(f"  {mpd_path.name}: {reason}")
        return

    text = disassemble(inputs[0])
    if args.output:
        if args.output.exists() and args.output.is_dir():
            out_path = output_path_for(inputs[0], inputs[0].parent, args.output)
            out_path.write_text(text, encoding="utf-8")
        else:
            args.output.write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
