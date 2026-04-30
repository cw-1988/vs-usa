# Export a function pointer table from the current Ghidra program as JSON.
#
# Headless example:
#   analyzeHeadless <project_dir> <project_name> \
#     -import <binary> \
#     -scriptPath <script_dir> \
#     -postScript export_function_table.py <output_json> <table_addr> <entry_count> [table_name] [pointer_size]

import json
import os


def parse_int(value):
    return int(str(value), 0)


def to_hex(value):
    return "0x%08X" % (value & 0xFFFFFFFF)


def handler_name_for(symbol_table, function_manager, target_addr):
    function = function_manager.getFunctionAt(target_addr)
    if function is None:
        function = function_manager.getFunctionContaining(target_addr)
    if function is not None:
        return function.getName(), function.getEntryPoint().toString()

    symbol = symbol_table.getPrimarySymbol(target_addr)
    if symbol is not None:
        return symbol.getName(), target_addr.toString()

    return None, None


def main():
    args = getScriptArgs()
    if len(args) < 3:
        raise RuntimeError(
            "usage: export_function_table.py <output_json> <table_addr> <entry_count> [table_name] [pointer_size]"
        )

    output_json = args[0]
    table_addr_raw = parse_int(args[1])
    entry_count = parse_int(args[2])
    table_name = args[3] if len(args) >= 4 else "function_table"
    pointer_size = parse_int(args[4]) if len(args) >= 5 else 4

    if currentProgram is None:
        raise RuntimeError("No current program is open")

    memory = currentProgram.getMemory()
    function_manager = currentProgram.getFunctionManager()
    symbol_table = currentProgram.getSymbolTable()

    entries = []
    table_addr = toAddr(table_addr_raw)

    for index in range(entry_count):
        entry_addr = table_addr.add(index * pointer_size)
        if pointer_size != 4:
            raise RuntimeError("Only 4-byte pointer tables are supported right now")

        raw_value = memory.getInt(entry_addr) & 0xFFFFFFFF
        target_addr = toAddr(raw_value)
        handler_name, function_entry = handler_name_for(
            symbol_table, function_manager, target_addr
        )

        entries.append(
            {
                "index": index,
                "opcode": "0x%02X" % index,
                "entry_address": entry_addr.toString(),
                "handler_address": to_hex(raw_value),
                "handler_name": handler_name,
                "function_entry": function_entry,
            }
        )

    payload = {
        "program_name": currentProgram.getName(),
        "program_path": currentProgram.getDomainFile().getPathname(),
        "table_name": table_name,
        "table_address": to_hex(table_addr_raw),
        "entry_count": entry_count,
        "pointer_size": pointer_size,
        "entries": entries,
    }

    output_dir = os.path.dirname(output_json)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_json, "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)

    print("wrote %d entries to %s" % (entry_count, output_json))


main()
