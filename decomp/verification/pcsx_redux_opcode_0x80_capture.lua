local bit = require("bit")
local ffi = require("ffi")

local function parse_bool(value, default)
    if value == nil or value == "" then
        return default
    end
    value = string.lower(value)
    return value == "1" or value == "true" or value == "yes" or value == "on"
end

local function parse_int(value, default)
    if value == nil or value == "" then
        return default
    end
    local parsed = tonumber(value)
    if parsed ~= nil then
        return parsed
    end
    if string.sub(value, 1, 2) == "0x" or string.sub(value, 1, 2) == "0X" then
        return tonumber(string.sub(value, 3), 16)
    end
    error("unable to parse integer value: " .. tostring(value))
end

local function split_csv(raw)
    local items = {}
    for item in string.gmatch(raw or "", "[^,]+") do
        items[#items + 1] = item
    end
    return items
end

local function utc_now()
    return os.date("!%Y-%m-%dT%H:%M:%SZ")
end

local function hex32(value)
    return string.format("0x%08X", value % 0x100000000)
end

local function json_escape(text)
    text = tostring(text)
    text = text:gsub("\\", "\\\\")
    text = text:gsub("\"", "\\\"")
    text = text:gsub("\r", "\\r")
    text = text:gsub("\n", "\\n")
    text = text:gsub("\t", "\\t")
    return "\"" .. text .. "\""
end

local function is_array(value)
    if type(value) ~= "table" then
        return false
    end
    local count = 0
    for key in pairs(value) do
        if type(key) ~= "number" then
            return false
        end
        count = count + 1
    end
    for index = 1, count do
        if value[index] == nil then
            return false
        end
    end
    return true
end

local function json_encode(value)
    local value_type = type(value)
    if value_type == "nil" then
        return "null"
    end
    if value_type == "boolean" then
        return value and "true" or "false"
    end
    if value_type == "number" then
        return tostring(value)
    end
    if value_type == "string" then
        return json_escape(value)
    end
    if value_type ~= "table" then
        return json_escape(tostring(value))
    end

    if is_array(value) then
        local parts = {}
        for index = 1, #value do
            parts[#parts + 1] = json_encode(value[index])
        end
        return "[" .. table.concat(parts, ",") .. "]"
    end

    local parts = {}
    for key, item in pairs(value) do
        parts[#parts + 1] = json_escape(key) .. ":" .. json_encode(item)
    end
    table.sort(parts)
    return "{" .. table.concat(parts, ",") .. "}"
end

local config = {
    table_address = parse_int(os.getenv("VS_OPCODE_TABLE_ADDRESS"), 0x800F4C28),
    table_size = parse_int(os.getenv("VS_OPCODE_TABLE_SIZE"), 0x400),
    focus_opcodes = split_csv(os.getenv("VS_OPCODE_FOCUS_OPCODES") or "0x80,0x81,0x82"),
    reader_address = parse_int(os.getenv("VS_OPCODE_READER_ADDRESS"), 0x800BFBB8),
    stub_address = parse_int(os.getenv("VS_OPCODE_STUB_ADDRESS"), 0x800B66E4),
    candidate_address = parse_int(os.getenv("VS_OPCODE_CANDIDATE_ADDRESS"), 0x800BA2E0),
    after_init_path = os.getenv("VS_OPCODE_AFTER_INIT_PATH") or "decomp/evidence/opcode_0x80_runtime_after_init.bin",
    pre_dispatch_path = os.getenv("VS_OPCODE_PRE_DISPATCH_PATH") or "decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin",
    summary_path = os.getenv("VS_OPCODE_AUTOMATION_SUMMARY_PATH") or "decomp/evidence/opcode_0x80_runtime_automation_summary.json",
    idle_cycles = parse_int(os.getenv("VS_OPCODE_IDLE_CYCLES"), 200000),
    timeout_frames = parse_int(os.getenv("VS_OPCODE_TIMEOUT_FRAMES"), 1800),
    post_reader_frames = parse_int(os.getenv("VS_OPCODE_POST_READER_FRAMES"), 180),
    min_write_pc = parse_int(os.getenv("VS_OPCODE_MIN_WRITE_PC"), 0x80000000),
    quit_on_candidate_hit = parse_bool(os.getenv("VS_OPCODE_QUIT_ON_CANDIDATE_HIT"), true),
    save_state_path = os.getenv("VS_OPCODE_SAVE_STATE_PATH"),
}

local state = {
    started_utc = utc_now(),
    frame_count = 0,
    write_hit_count = 0,
    ignored_write_hit_count = 0,
    reader_hit_count = 0,
    candidate_hit_count = 0,
    write_breakpoint = {
        kind = "write",
        address_range = hex32(config.table_address) .. "-" .. hex32(config.table_address + config.table_size - 1),
    },
    exec_breakpoints = {
        reader = hex32(config.reader_address),
        stub = hex32(config.stub_address),
        candidate = hex32(config.candidate_address),
    },
    last_write_cycle = nil,
    saw_write = false,
    snapshots = {},
    candidate_hits = {},
    notes = {},
    quit_requested = false,
    exit_code = 0,
}

local function add_note(text)
    state.notes[#state.notes + 1] = {
        timestamp = utc_now(),
        text = text,
    }
end

local function current_pc_hex()
    return hex32(tonumber(PCSX.getRegisters().pc))
end

local function current_pc_value()
    return tonumber(PCSX.getRegisters().pc)
end

local function ram_offset(address)
    return bit.band(address, 0x1FFFFF)
end

local function read_u32_le(mem_ptr, offset)
    local b0 = tonumber(mem_ptr[offset + 0])
    local b1 = tonumber(mem_ptr[offset + 1])
    local b2 = tonumber(mem_ptr[offset + 2])
    local b3 = tonumber(mem_ptr[offset + 3])
    return b0 + b1 * 0x100 + b2 * 0x10000 + b3 * 0x1000000
end

local function capture_focus_handlers()
    local mem_ptr = PCSX.getMemPtr()
    local table_base = ram_offset(config.table_address)
    local handlers = {}
    for _, opcode_text in ipairs(config.focus_opcodes) do
        local opcode_value = parse_int(opcode_text, nil)
        if opcode_value ~= nil then
            local offset = table_base + opcode_value * 4
            handlers[opcode_text] = hex32(read_u32_le(mem_ptr, offset))
        end
    end
    return handlers
end

local function dump_snapshot(label, path, reason)
    if state.snapshots[label] ~= nil then
        return
    end

    local mem_ptr = PCSX.getMemPtr()
    local table_base = ram_offset(config.table_address)
    local payload = ffi.string(mem_ptr + table_base, config.table_size)
    local handle, err = io.open(path, "wb")
    if not handle then
        add_note("failed to write " .. label .. " snapshot: " .. tostring(err))
        return
    end
    handle:write(payload)
    handle:close()

    state.snapshots[label] = {
        path = path,
        timestamp = utc_now(),
        reason = reason,
        pc = current_pc_hex(),
        focus_handlers = capture_focus_handlers(),
    }
    add_note("captured " .. label .. " snapshot via " .. reason)
end

local function write_summary()
    local payload = {
        started_utc = state.started_utc,
        finished_utc = utc_now(),
        frame_count = state.frame_count,
        write_hit_count = state.write_hit_count,
        ignored_write_hit_count = state.ignored_write_hit_count,
        reader_hit_count = state.reader_hit_count,
        candidate_hit_count = state.candidate_hit_count,
        write_breakpoint = state.write_breakpoint,
        exec_breakpoints = state.exec_breakpoints,
        snapshots = state.snapshots,
        candidate_hits = state.candidate_hits,
        notes = state.notes,
        exit_code = state.exit_code,
    }

    local handle, err = io.open(config.summary_path, "wb")
    if not handle then
        return
    end
    handle:write(json_encode(payload))
    handle:write("\n")
    handle:close()
end

local function request_quit(code, reason)
    if state.quit_requested then
        return
    end
    state.quit_requested = true
    state.exit_code = code
    add_note(reason)
    write_summary()
    PCSX.quit(code)
end

local breakpoints = {}
local listeners = {}

breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
    config.table_address,
    "Write",
    config.table_size,
    "opcode table write",
    function(address, width, cause)
        local pc_value = current_pc_value()
        if pc_value < config.min_write_pc then
            state.ignored_write_hit_count = state.ignored_write_hit_count + 1
            if state.ignored_write_hit_count == 1 then
                add_note(
                    "ignoring pre-runtime opcode-table write at "
                        .. hex32(address)
                        .. " from pc "
                        .. hex32(pc_value)
                )
            end
            return
        end

        state.write_hit_count = state.write_hit_count + 1
        state.saw_write = true
        state.last_write_cycle = tonumber(PCSX.getCPUCycles())
        if state.write_hit_count == 1 then
            add_note(
                "first opcode-table write hit at "
                    .. hex32(address)
                    .. " from pc "
                    .. hex32(pc_value)
            )
        end
    end
)

breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
    config.reader_address,
    "Exec",
    4,
    "runtime opcode reader",
    function()
        state.reader_hit_count = state.reader_hit_count + 1
        if state.snapshots.after_init == nil then
            dump_snapshot("after_init", config.after_init_path, "reader_breakpoint_fallback")
        end
        if state.snapshots.pre_dispatch == nil then
            dump_snapshot("pre_dispatch", config.pre_dispatch_path, "reader_breakpoint")
            state.pre_dispatch_frame = state.frame_count
        end
        add_note("reader breakpoint hit at " .. current_pc_hex())
    end
)

local function add_candidate_breakpoint(address, label)
    breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
        address,
        "Exec",
        4,
        label,
        function()
            local key = hex32(address)
            local entry = state.candidate_hits[key] or {
                label = label,
                hit_count = 0,
                pcs = {},
            }
            entry.hit_count = entry.hit_count + 1
            entry.pcs[#entry.pcs + 1] = current_pc_hex()
            state.candidate_hits[key] = entry
            state.candidate_hit_count = state.candidate_hit_count + 1
            if state.snapshots.pre_dispatch == nil then
                dump_snapshot("pre_dispatch", config.pre_dispatch_path, "candidate_breakpoint")
                state.pre_dispatch_frame = state.frame_count
            end
            add_note("candidate handler breakpoint hit at " .. key)
            if config.quit_on_candidate_hit then
                request_quit(0, "candidate handler breakpoint hit")
                return false
            end
        end
    )
end

add_candidate_breakpoint(config.stub_address, "stub candidate")
if config.candidate_address ~= config.stub_address then
    add_candidate_breakpoint(config.candidate_address, "sound-family candidate")
end

listeners[#listeners + 1] = PCSX.Events.createEventListener("Quitting", function()
    write_summary()
end)

if config.save_state_path ~= nil and config.save_state_path ~= "" then
    local ok, err = pcall(function()
        PCSX.loadSaveState(config.save_state_path)
    end)
    if ok then
        add_note("loaded savestate " .. config.save_state_path)
    else
        add_note("failed to load savestate " .. config.save_state_path .. ": " .. tostring(err))
    end
end

function DrawImguiFrame()
    state.frame_count = state.frame_count + 1
    local cycles = tonumber(PCSX.getCPUCycles())

    if state.saw_write and state.snapshots.after_init == nil and state.last_write_cycle ~= nil then
        if cycles - state.last_write_cycle >= config.idle_cycles then
            dump_snapshot("after_init", config.after_init_path, "idle_after_write")
        end
    end

    if state.pre_dispatch_frame ~= nil and not state.quit_requested then
        if state.frame_count - state.pre_dispatch_frame >= config.post_reader_frames then
            request_quit(0, "post-reader grace period elapsed")
            return
        end
    end

    if state.frame_count >= config.timeout_frames and not state.quit_requested then
        if state.saw_write and state.snapshots.after_init == nil then
            dump_snapshot("after_init", config.after_init_path, "timeout_fallback")
        end
        request_quit(2, "timeout elapsed before capture finished")
    end
end

add_note("loaded automated opcode 0x80 runtime capture script")
