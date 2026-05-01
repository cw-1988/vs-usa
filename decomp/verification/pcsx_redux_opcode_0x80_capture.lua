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

local function try_parse_int(value, default)
    local ok, parsed = pcall(parse_int, value, default)
    if ok then
        return parsed
    end
    return default
end

local function split_csv(raw)
    local items = {}
    for item in string.gmatch(raw or "", "[^,]+") do
        items[#items + 1] = item
    end
    return items
end

local function split_tab_fields(raw)
    local fields = {}
    local start_index = 1
    while true do
        local tab_index = string.find(raw, "\t", start_index, true)
        if tab_index == nil then
            fields[#fields + 1] = string.sub(raw, start_index)
            break
        end
        fields[#fields + 1] = string.sub(raw, start_index, tab_index - 1)
        start_index = tab_index + 1
    end
    return fields
end

local function utc_now()
    return os.date("!%Y-%m-%dT%H:%M:%SZ")
end

local function hex32(value)
    return string.format("0x%08X", value % 0x100000000)
end

local function hex8(value)
    return string.format("0x%02X", value % 0x100)
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
    handler_probe_opcodes = split_csv(os.getenv("VS_OPCODE_HANDLER_OPCODES") or ""),
    reader_address = parse_int(os.getenv("VS_OPCODE_READER_ADDRESS"), 0x800BFBB8),
    reader_caller_address = parse_int(os.getenv("VS_OPCODE_READER_CALLER_ADDRESS"), 0x800BF850),
    reader_grandcaller_address = parse_int(os.getenv("VS_OPCODE_READER_GRANDCALLER_ADDRESS"), 0x8007A36C),
    stub_address = parse_int(os.getenv("VS_OPCODE_STUB_ADDRESS"), 0x800B66E4),
    candidate_address = parse_int(os.getenv("VS_OPCODE_CANDIDATE_ADDRESS"), 0x800BA2E0),
    after_init_path = os.getenv("VS_OPCODE_AFTER_INIT_PATH") or "decomp/evidence/opcode_0x80_runtime_after_init.bin",
    pre_dispatch_path = os.getenv("VS_OPCODE_PRE_DISPATCH_PATH") or "decomp/evidence/opcode_0x80_runtime_pre_dispatch.bin",
    summary_path = os.getenv("VS_OPCODE_AUTOMATION_SUMMARY_PATH") or "decomp/evidence/opcode_0x80_runtime_automation_summary.json",
    idle_cycles = parse_int(os.getenv("VS_OPCODE_IDLE_CYCLES"), 200000),
    timeout_frames = parse_int(os.getenv("VS_OPCODE_TIMEOUT_FRAMES"), 1800),
    post_reader_frames = parse_int(os.getenv("VS_OPCODE_POST_READER_FRAMES"), 180),
    min_breakpoint_frame = parse_int(os.getenv("VS_OPCODE_MIN_BREAKPOINT_FRAME"), 0),
    min_write_pc = parse_int(os.getenv("VS_OPCODE_MIN_WRITE_PC"), 0x80000000),
    quit_on_candidate_hit = parse_bool(os.getenv("VS_OPCODE_QUIT_ON_CANDIDATE_HIT"), true),
    save_state_path = os.getenv("VS_OPCODE_SAVE_STATE_PATH"),
    save_state_source_path = os.getenv("VS_OPCODE_SAVE_STATE_SOURCE_PATH"),
    save_state_was_decompressed = parse_bool(os.getenv("VS_OPCODE_SAVE_STATE_WAS_DECOMPRESSED"), false),
    input_plan_path = os.getenv("VS_OPCODE_INPUT_PLAN_PATH"),
    input_plan_source_path = os.getenv("VS_OPCODE_INPUT_PLAN_SOURCE_PATH"),
    input_plan_description = os.getenv("VS_OPCODE_INPUT_PLAN_DESCRIPTION"),
    input_plan_pad_slot = parse_int(os.getenv("VS_OPCODE_INPUT_PLAN_PAD_SLOT"), 1),
    input_plan_pad_number = parse_int(os.getenv("VS_OPCODE_INPUT_PLAN_PAD_NUMBER"), 1),
    input_plan_analog_mode = parse_bool(os.getenv("VS_OPCODE_INPUT_PLAN_ANALOG_MODE"), false),
    input_plan_quit_when_finished = parse_bool(os.getenv("VS_OPCODE_INPUT_PLAN_QUIT_WHEN_FINISHED"), false),
    screenshot_dir = os.getenv("VS_OPCODE_SCREENSHOT_DIR") or "",
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
        pointer_slot = hex32(config.table_address),
        address_range = nil,
    },
    exec_breakpoints = {
        reader = hex32(config.reader_address),
        stub = hex32(config.stub_address),
        candidate = hex32(config.candidate_address),
    },
    probe_hits = {},
    last_write_cycle = nil,
    saw_write = false,
    snapshots = {},
    candidate_hits = {},
    dispatch_by_opcode = {},
    handler_probe_hits = {},
    handler_probe_plan = {},
    notes = {},
    quit_requested = false,
    exit_code = 0,
    save_state_load_count = 0,
    input_plan = nil,
    screen_captures = {},
    created_save_states = {},
    runtime_table_base = nil,
    table_write_breakpoint_installed = false,
    handler_probe_breakpoints_installed = false,
}

local function log_console(text)
    print("[opcode_0x80] " .. tostring(text))
end

local function add_note(text)
    state.notes[#state.notes + 1] = {
        timestamp = utc_now(),
        text = text,
    }
end

local function should_log_repeated_hit(hit_count)
    return hit_count <= 5 or hit_count % 25 == 0
end

local function log_trigger_hit(label, hit_count, detail)
    if should_log_repeated_hit(hit_count) then
        log_console(label .. " hit #" .. tostring(hit_count) .. ": " .. detail)
    end
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

local function read_u8(mem_ptr, offset)
    return tonumber(mem_ptr[offset])
end

local function read_u32_at_address(address)
    local mem_ptr = PCSX.getMemPtr()
    return read_u32_le(mem_ptr, ram_offset(address))
end

local function resolve_runtime_table_base()
    local pointer_value = read_u32_at_address(config.table_address)
    if pointer_value == nil or pointer_value == 0 then
        return nil
    end
    return pointer_value
end

local function get_runtime_table_base()
    if state.runtime_table_base ~= nil and state.runtime_table_base ~= 0 then
        return state.runtime_table_base
    end
    return resolve_runtime_table_base()
end

local function normalize_opcode_text(opcode_text)
    local opcode_value = parse_int(opcode_text, nil)
    if opcode_value == nil then
        return nil
    end
    return hex8(opcode_value), opcode_value
end

local function capture_focus_handlers()
    local runtime_table_base = get_runtime_table_base()
    if runtime_table_base == nil then
        return {}
    end

    local mem_ptr = PCSX.getMemPtr()
    local table_base = ram_offset(runtime_table_base)
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

local function capture_raw_bytes(address, count)
    local mem_ptr = PCSX.getMemPtr()
    local base = ram_offset(address)
    local parts = {}
    for index = 0, count - 1 do
        parts[#parts + 1] = string.format("%02X", read_u8(mem_ptr, base + index))
    end
    return table.concat(parts, " ")
end

local function capture_current_dispatch()
    local registers = PCSX.getRegisters()
    local context_ptr = tonumber(registers.GPR.n.a0)
    if context_ptr == nil or context_ptr == 0 then
        return nil
    end

    local mem_ptr = PCSX.getMemPtr()
    local context_offset = ram_offset(context_ptr)
    local script_ptr = read_u32_le(mem_ptr, context_offset)
    if script_ptr == nil or script_ptr == 0 then
        return nil
    end

    local script_offset = ram_offset(script_ptr)
    local opcode_value = read_u8(mem_ptr, script_offset)
    if opcode_value == nil then
        return nil
    end

    local runtime_table_base = get_runtime_table_base()
    if runtime_table_base == nil then
        return nil
    end

    local handler_offset = ram_offset(runtime_table_base) + opcode_value * 4
    local handler_value = read_u32_le(mem_ptr, handler_offset)

    return {
        opcode = hex8(opcode_value),
        handler_address = hex32(handler_value),
        context_ptr = hex32(context_ptr),
        script_ptr = hex32(script_ptr),
        reader_arg1 = hex32(tonumber(registers.GPR.n.a1)),
        pc = current_pc_hex(),
        raw_bytes = capture_raw_bytes(script_ptr, 5),
    }
end

local function build_handler_probe_targets()
    if #config.handler_probe_opcodes == 0 then
        return {}
    end

    local runtime_table_base = get_runtime_table_base()
    if runtime_table_base == nil then
        return {}
    end

    local mem_ptr = PCSX.getMemPtr()
    local table_base = ram_offset(runtime_table_base)
    local targets_by_address = {}

    for _, opcode_text in ipairs(config.handler_probe_opcodes) do
        local normalized_opcode, opcode_value = normalize_opcode_text(opcode_text)
        if normalized_opcode ~= nil then
            local handler_offset = table_base + opcode_value * 4
            local handler_value = read_u32_le(mem_ptr, handler_offset)
            local handler_address = hex32(handler_value)
            local target = targets_by_address[handler_address]
            if target == nil then
                target = {
                    address = handler_value,
                    address_hex = handler_address,
                    opcodes = {},
                }
                targets_by_address[handler_address] = target
            end
            target.opcodes[#target.opcodes + 1] = normalized_opcode
        end
    end

    local target_keys = {}
    for address_hex in pairs(targets_by_address) do
        target_keys[#target_keys + 1] = address_hex
    end
    table.sort(target_keys)

    local targets = {}
    for _, address_hex in ipairs(target_keys) do
        local target = targets_by_address[address_hex]
        table.sort(target.opcodes)
        targets[#targets + 1] = target
    end

    return targets
end

local function record_dispatch_observation(entry)
    if entry == nil or entry.opcode == nil then
        return
    end

    local aggregate = state.dispatch_by_opcode[entry.opcode]
    if aggregate == nil then
        aggregate = {
            opcode = entry.opcode,
            hit_count = 0,
            handler_counts = {},
            first_context_ptr = entry.context_ptr,
            first_script_ptr = entry.script_ptr,
            first_reader_arg1 = entry.reader_arg1,
            first_pc = entry.pc,
            sample_raw_bytes = entry.raw_bytes,
        }
        state.dispatch_by_opcode[entry.opcode] = aggregate
    end

    aggregate.hit_count = aggregate.hit_count + 1
    aggregate.last_context_ptr = entry.context_ptr
    aggregate.last_script_ptr = entry.script_ptr
    aggregate.last_reader_arg1 = entry.reader_arg1
    aggregate.last_pc = entry.pc
    aggregate.last_handler_address = entry.handler_address
    aggregate.handler_counts[entry.handler_address] = (aggregate.handler_counts[entry.handler_address] or 0) + 1

    if aggregate.hit_count == 1 then
        log_console(
            "reader dispatch observed "
                .. entry.opcode
                .. " -> "
                .. entry.handler_address
                .. " from script "
                .. entry.script_ptr
                .. " via context "
                .. entry.context_ptr
                .. " raw="
                .. entry.raw_bytes
        )
        add_note(
            "reader dispatch observed "
                .. entry.opcode
                .. " -> "
                .. entry.handler_address
                .. " from script "
                .. entry.script_ptr
                .. " via context "
                .. entry.context_ptr
                .. " raw="
                .. entry.raw_bytes
        )
    end
end

local function build_dispatch_summary()
    local opcode_keys = {}
    for opcode in pairs(state.dispatch_by_opcode) do
        opcode_keys[#opcode_keys + 1] = opcode
    end
    table.sort(opcode_keys)

    local summary = {}
    for _, opcode in ipairs(opcode_keys) do
        local aggregate = state.dispatch_by_opcode[opcode]
        summary[#summary + 1] = {
            opcode = aggregate.opcode,
            hit_count = aggregate.hit_count,
            last_handler_address = aggregate.last_handler_address,
            handler_counts = aggregate.handler_counts,
            first_context_ptr = aggregate.first_context_ptr,
            first_script_ptr = aggregate.first_script_ptr,
            first_reader_arg1 = aggregate.first_reader_arg1,
            first_pc = aggregate.first_pc,
            last_context_ptr = aggregate.last_context_ptr,
            last_script_ptr = aggregate.last_script_ptr,
            last_reader_arg1 = aggregate.last_reader_arg1,
            last_pc = aggregate.last_pc,
            sample_raw_bytes = aggregate.sample_raw_bytes,
        }
    end
    return summary
end

local function dump_snapshot(label, path, reason)
    if state.snapshots[label] ~= nil then
        return
    end

    local runtime_table_base = get_runtime_table_base()
    if runtime_table_base == nil then
        add_note("skipped " .. label .. " snapshot because runtime table base is unresolved")
        return
    end

    local mem_ptr = PCSX.getMemPtr()
    local table_base = ram_offset(runtime_table_base)
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
        runtime_table_base = hex32(runtime_table_base),
        focus_handlers = capture_focus_handlers(),
    }
    add_note("captured " .. label .. " snapshot via " .. reason)
end

local function screenshot_path(label)
    if config.screenshot_dir == nil or config.screenshot_dir == "" then
        return nil
    end
    return config.screenshot_dir .. "/" .. label .. ".ppm"
end

local function convert_16bpp_to_rgb24(slice)
    local raw = tostring(slice)
    local output = {}
    local output_index = 1
    for offset = 1, #raw, 2 do
        local lo = string.byte(raw, offset)
        local hi = string.byte(raw, offset + 1)
        local value = lo + hi * 0x100
        local red5 = bit.band(value, 0x1F)
        local green5 = bit.band(bit.rshift(value, 5), 0x1F)
        local blue5 = bit.band(bit.rshift(value, 10), 0x1F)
        output[output_index] = string.char(bit.bor(bit.lshift(red5, 3), bit.rshift(red5, 2)))
        output[output_index + 1] = string.char(bit.bor(bit.lshift(green5, 3), bit.rshift(green5, 2)))
        output[output_index + 2] = string.char(bit.bor(bit.lshift(blue5, 3), bit.rshift(blue5, 2)))
        output_index = output_index + 3
    end
    return table.concat(output)
end

local function capture_screen(label, reason)
    local path = screenshot_path(label)
    if path == nil then
        return
    end

    local ok, err = pcall(function()
        local screenshot = PCSX.GPU.takeScreenShot()
        local handle = Support.File.open(path, "TRUNCATE")
        handle:write(string.format("P6\n%d %d\n255\n", screenshot.width, screenshot.height))
        if screenshot.bpp == 1 then
            handle:writeMoveSlice(screenshot.data)
        else
            handle:write(convert_16bpp_to_rgb24(screenshot.data))
        end
        handle:close()

        state.screen_captures[#state.screen_captures + 1] = {
            label = label,
            path = path,
            timestamp = utc_now(),
            frame = state.frame_count,
            width = screenshot.width,
            height = screenshot.height,
            bpp = screenshot.bpp == 1 and 24 or 16,
            reason = reason,
        }
    end)

    if not ok then
        add_note("failed to capture screen " .. label .. ": " .. tostring(err))
    end
end

local request_quit

local function queue_safe(label, func)
    PCSX.nextTick(function()
        local ok, err = pcall(func)
        if not ok then
            add_note("queued action failed for " .. label .. ": " .. tostring(err))
        end
    end)
end

local function get_input_pad()
    local slots = PCSX.SIO0 and PCSX.SIO0.slots
    if slots == nil then
        return nil
    end
    local slot = slots[config.input_plan_pad_slot]
    if slot == nil or slot.pads == nil then
        return nil
    end
    return slot.pads[config.input_plan_pad_number]
end

local function clear_input_plan_overrides()
    local plan = state.input_plan
    if plan == nil or plan.active_buttons == nil then
        return
    end

    local pad = get_input_pad()
    if pad == nil then
        return
    end

    for button_value in pairs(plan.active_buttons) do
        pad.clearOverride(button_value)
    end
    plan.active_buttons = {}
end

local function create_save_state(path, note)
    local ok, err = pcall(function()
        local save_state_file = Support.File.open(path, "TRUNCATE")
        save_state_file:writeMoveSlice(PCSX.createSaveState())
        save_state_file:close()
    end)

    if not ok then
        add_note("failed to create savestate at " .. tostring(path) .. ": " .. tostring(err))
        return false
    end

    state.created_save_states[#state.created_save_states + 1] = {
        path = path,
        note = note,
        frame = state.frame_count,
        timestamp = utc_now(),
    }
    add_note("created savestate at " .. tostring(path))
    log_console("created savestate at " .. tostring(path))
    return true
end

local function reset_input_plan_progress()
    local plan = state.input_plan
    if plan == nil then
        return
    end

    clear_input_plan_overrides()
    plan.started_steps = 0
    plan.completed_steps = 0
    plan.finished_noted = false
    for _, step in ipairs(plan.steps) do
        step.started = false
        step.completed = false
    end
end

local function load_configured_save_state(trigger_reason)
    if config.save_state_path == nil or config.save_state_path == "" then
        return false
    end
    if state.save_state_load_requested then
        return false
    end

    state.save_state_load_requested = true

    local ok, err = pcall(function()
        local save_state_file = Support.File.open(config.save_state_path)
        PCSX.loadSaveState(save_state_file)
        save_state_file:close()
    end)

    if ok then
        local load_note = "loaded savestate " .. config.save_state_path
        if config.save_state_source_path ~= nil and config.save_state_source_path ~= "" then
            load_note = load_note .. " (source " .. config.save_state_source_path .. ")"
        end
        if config.save_state_was_decompressed then
            load_note = load_note .. " via decompressed gzip staging"
        end
        if trigger_reason ~= nil and trigger_reason ~= "" then
            load_note = load_note .. " after " .. trigger_reason
        end
        add_note(load_note)
        return true
    end

    state.save_state_load_requested = false
    add_note("failed to load savestate " .. config.save_state_path .. ": " .. tostring(err))
    return false
end

local function load_input_plan()
    if config.input_plan_path == nil or config.input_plan_path == "" then
        return nil
    end

    local handle, err = io.open(config.input_plan_path, "rb")
    if not handle then
        add_note("failed to open input plan: " .. tostring(err))
        return nil
    end

    local button_constants = PCSX.CONSTS and PCSX.CONSTS.PAD and PCSX.CONSTS.PAD.BUTTON
    local steps = {}
    local line_number = 0
    for raw_line in handle:lines() do
        line_number = line_number + 1
        if raw_line ~= "" then
            local fields = split_tab_fields(raw_line)
            if #fields < 3 then
                add_note("ignoring malformed input plan line " .. tostring(line_number))
            else
                local is_new_format = try_parse_int(fields[1], nil) == nil
                local kind = is_new_format and fields[1] or "buttons"
                local start_frame = try_parse_int(is_new_format and fields[2] or fields[1], nil)
                local duration_frames = try_parse_int(is_new_format and fields[3] or fields[2], nil)
                local payload = is_new_format and (fields[4] or "") or (fields[3] or "")
                local note = (is_new_format and fields[5] or fields[4]) or ("step " .. tostring(line_number))

                if kind == "buttons" then
                    local button_names = split_csv(payload)
                    local button_values = {}
                    local resolved_names = {}
                    local has_unknown_button = false

                    for _, button_name in ipairs(button_names) do
                        local normalized_name = string.upper(button_name)
                        local button_value = button_constants and button_constants[normalized_name] or nil
                        if button_value == nil then
                            add_note("input plan line " .. tostring(line_number) .. " references unknown button " .. normalized_name)
                            has_unknown_button = true
                        else
                            button_values[#button_values + 1] = button_value
                            resolved_names[#resolved_names + 1] = normalized_name
                        end
                    end

                    if not has_unknown_button and start_frame ~= nil and duration_frames ~= nil and duration_frames > 0 and #button_values > 0 then
                        steps[#steps + 1] = {
                            line_number = line_number,
                            kind = "buttons",
                            start_frame = start_frame,
                            duration_frames = duration_frames,
                            button_names = resolved_names,
                            button_values = button_values,
                            note = note,
                            started = false,
                            completed = false,
                        }
                    end
                elseif kind == "create_save_state" then
                    if start_frame ~= nil and duration_frames ~= nil and duration_frames > 0 and payload ~= "" then
                        steps[#steps + 1] = {
                            line_number = line_number,
                            kind = "create_save_state",
                            start_frame = start_frame,
                            duration_frames = duration_frames,
                            save_state_path = payload,
                            note = note,
                            started = false,
                            completed = false,
                        }
                    else
                        add_note("ignoring malformed create_save_state line " .. tostring(line_number))
                    end
                else
                    add_note("ignoring unsupported input plan step kind " .. tostring(kind) .. " on line " .. tostring(line_number))
                end
            end
        end
    end
    handle:close()

    if #steps == 0 then
        add_note("input plan did not yield any usable steps")
        return nil
    end

    add_note(
        "loaded input plan from "
            .. (config.input_plan_source_path ~= "" and config.input_plan_source_path or config.input_plan_path)
            .. " with "
            .. tostring(#steps)
            .. " step(s)"
    )

    return {
        prepared_path = config.input_plan_path,
        source_path = config.input_plan_source_path,
        description = config.input_plan_description,
        pad_slot = config.input_plan_pad_slot,
        pad_number = config.input_plan_pad_number,
        analog_mode = config.input_plan_analog_mode,
        quit_when_finished = config.input_plan_quit_when_finished,
        steps = steps,
        active_buttons = {},
        started_steps = 0,
        completed_steps = 0,
        initialized_pad = false,
        finished_noted = false,
    }
end

local function update_input_plan()
    local plan = state.input_plan
    if plan == nil then
        return
    end

    local pad = get_input_pad()
    if pad == nil then
        if not plan.pad_missing_noted then
            add_note(
                "input plan could not find pad slot "
                    .. tostring(plan.pad_slot)
                    .. " pad "
                    .. tostring(plan.pad_number)
            )
            plan.pad_missing_noted = true
        end
        return
    end

    if not plan.initialized_pad then
        pad.setAnalogMode(plan.analog_mode)
        plan.initialized_pad = true
    end

    local desired_buttons = {}
    for index, step in ipairs(plan.steps) do
        local end_frame = step.start_frame + step.duration_frames
        if state.frame_count >= step.start_frame and state.frame_count < end_frame then
            if not step.started then
                step.started = true
                plan.started_steps = plan.started_steps + 1
                local step_started_message = "input plan step " .. tostring(index) .. " started at frame " .. tostring(state.frame_count) .. ": " .. step.note
                if step.kind == "buttons" then
                    step_started_message = step_started_message .. " [" .. table.concat(step.button_names, "+") .. "]"
                elseif step.kind == "create_save_state" then
                    step_started_message = step_started_message .. " [save=" .. tostring(step.save_state_path) .. "]"
                    create_save_state(step.save_state_path, step.note)
                end
                add_note(step_started_message)
                log_console(step_started_message)
            end
            if step.kind == "buttons" then
                for button_index, button_value in ipairs(step.button_values) do
                    desired_buttons[button_value] = step.button_names[button_index]
                end
            end
        elseif state.frame_count >= end_frame and not step.completed then
            step.completed = true
            plan.completed_steps = plan.completed_steps + 1
            add_note("input plan step " .. tostring(index) .. " completed: " .. step.note)
            if step.kind == "buttons" then
                capture_screen(string.format("step-%02d-complete", index), "input_plan_step_complete")
            end
        end
    end

    for button_value in pairs(plan.active_buttons) do
        if desired_buttons[button_value] == nil then
            pad.clearOverride(button_value)
            plan.active_buttons[button_value] = nil
        end
    end

    for button_value, button_name in pairs(desired_buttons) do
        if plan.active_buttons[button_value] == nil then
            pad.setOverride(button_value)
            plan.active_buttons[button_value] = button_name
        end
    end

    if not plan.finished_noted and plan.completed_steps >= #plan.steps then
        add_note("input plan finished all scheduled steps by frame " .. tostring(state.frame_count))
        plan.finished_noted = true
        if plan.quit_when_finished and not state.quit_requested then
            request_quit(0, "input plan finished all scheduled steps")
            return
        end
    end
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
        probe_hits = state.probe_hits,
        snapshots = state.snapshots,
        candidate_hits = state.candidate_hits,
        dispatch_observations = build_dispatch_summary(),
        runtime_table_base = state.runtime_table_base and hex32(state.runtime_table_base) or nil,
        handler_probe_plan = state.handler_probe_plan,
        handler_probe_hits = state.handler_probe_hits,
        notes = state.notes,
        exit_code = state.exit_code,
        save_state = {
            requested_path = config.save_state_path,
            source_path = config.save_state_source_path,
            was_decompressed = config.save_state_was_decompressed,
            load_count = state.save_state_load_count,
        },
        input_plan = state.input_plan and {
            prepared_path = state.input_plan.prepared_path,
            source_path = state.input_plan.source_path,
            description = state.input_plan.description,
            pad_slot = state.input_plan.pad_slot,
            pad_number = state.input_plan.pad_number,
            analog_mode = state.input_plan.analog_mode,
            quit_when_finished = state.input_plan.quit_when_finished,
            step_count = #state.input_plan.steps,
            started_steps = state.input_plan.started_steps,
            completed_steps = state.input_plan.completed_steps,
            created_save_states = state.created_save_states,
        } or nil,
        screen_captures = state.screen_captures,
    }

    local handle, err = io.open(config.summary_path, "wb")
    if not handle then
        return
    end
    handle:write(json_encode(payload))
    handle:write("\n")
    handle:close()
end

request_quit = function(code, reason)
    if state.quit_requested then
        return
    end
    state.quit_requested = true
    state.exit_code = code
    clear_input_plan_overrides()
    add_note(reason)
    write_summary()
    PCSX.quit(code)
end

local breakpoints = {}
local listeners = {}

state.input_plan = load_input_plan()

breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
    config.reader_address,
    "Exec",
    4,
    "runtime opcode reader",
    function()
        if state.frame_count < config.min_breakpoint_frame then
            return
        end
        state.reader_hit_count = state.reader_hit_count + 1
        local pc_hex = current_pc_hex()
        queue_safe("reader breakpoint", function()
            local dispatch_entry = capture_current_dispatch()
            record_dispatch_observation(dispatch_entry)
            if state.snapshots.after_init == nil then
                dump_snapshot("after_init", config.after_init_path, "reader_breakpoint_fallback")
            end
            if state.snapshots.pre_dispatch == nil then
                dump_snapshot("pre_dispatch", config.pre_dispatch_path, "reader_breakpoint")
                state.pre_dispatch_frame = state.frame_count
            end
            if dispatch_entry ~= nil then
                log_trigger_hit(
                    "reader breakpoint",
                    state.reader_hit_count,
                    pc_hex
                        .. " for "
                        .. dispatch_entry.opcode
                        .. " -> "
                        .. dispatch_entry.handler_address
                )
                add_note(
                    "reader breakpoint hit at "
                        .. pc_hex
                        .. " for "
                        .. dispatch_entry.opcode
                        .. " -> "
                        .. dispatch_entry.handler_address
                )
            else
                log_trigger_hit("reader breakpoint", state.reader_hit_count, pc_hex)
                add_note("reader breakpoint hit at " .. pc_hex)
            end
        end)
    end
)

local function add_candidate_breakpoint(address, label)
    breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
        address,
        "Exec",
        4,
        label,
        function()
            if state.frame_count < config.min_breakpoint_frame then
                return
            end
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
            queue_safe("candidate breakpoint", function()
                log_trigger_hit(label, entry.hit_count, key)
                if state.snapshots.pre_dispatch == nil then
                    dump_snapshot("pre_dispatch", config.pre_dispatch_path, "candidate_breakpoint")
                    state.pre_dispatch_frame = state.frame_count
                end
                add_note("candidate handler breakpoint hit at " .. key)
                if config.quit_on_candidate_hit then
                    request_quit(0, "candidate handler breakpoint hit")
                end
            end)
            if config.quit_on_candidate_hit then
                return false
            end
        end
    )
end

local function add_probe_breakpoint(address, label)
    if address == nil or address == 0 then
        return
    end

    local key = hex32(address)
    state.exec_breakpoints[label] = key
    breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
        address,
        "Exec",
        4,
        label,
        function()
            if state.frame_count < config.min_breakpoint_frame then
                return
            end
            local entry = state.probe_hits[key] or {
                label = label,
                hit_count = 0,
                pcs = {},
            }
            entry.hit_count = entry.hit_count + 1
            entry.pcs[#entry.pcs + 1] = current_pc_hex()
            state.probe_hits[key] = entry
            queue_safe(label .. " breakpoint", function()
                log_trigger_hit(label, entry.hit_count, key)
                add_note(label .. " breakpoint hit at " .. key)
            end)
        end
    )
end

local function add_runtime_table_write_breakpoint(address)
    if address == nil or address == 0 then
        return
    end

    state.write_breakpoint.address_range = hex32(address) .. "-" .. hex32(address + config.table_size - 1)
    breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
        address,
        "Write",
        config.table_size,
        "opcode handler table write",
        function(hit_address)
            local pc_value = current_pc_value()
            if pc_value < config.min_write_pc then
                state.ignored_write_hit_count = state.ignored_write_hit_count + 1
                if state.ignored_write_hit_count == 1 then
                    local address_hex = hex32(hit_address)
                    local pc_hex = hex32(pc_value)
                    queue_safe("ignored write note", function()
                        log_console("ignoring pre-runtime opcode-table write at " .. address_hex .. " from pc " .. pc_hex)
                        add_note("ignoring pre-runtime opcode-table write at " .. address_hex .. " from pc " .. pc_hex)
                    end)
                end
                return
            end

            state.write_hit_count = state.write_hit_count + 1
            state.saw_write = true
            state.last_write_cycle = tonumber(PCSX.getCPUCycles())
            local address_hex = hex32(hit_address)
            local pc_hex = hex32(pc_value)
            queue_safe("write note", function()
                log_trigger_hit("opcode-table write", state.write_hit_count, address_hex .. " from pc " .. pc_hex)
                if state.write_hit_count == 1 then
                    add_note("first opcode-table write hit at " .. address_hex .. " from pc " .. pc_hex)
                end
            end)
        end
    )
    state.table_write_breakpoint_installed = true
    add_note("installed runtime table write breakpoint for " .. state.write_breakpoint.address_range)
end

local function add_handler_probe_breakpoint(target)
    if target == nil or target.address == nil or target.address == 0 then
        return
    end

    local address_hex = target.address_hex
    local label = "script handler probe " .. table.concat(target.opcodes, "/")
    breakpoints[#breakpoints + 1] = PCSX.addBreakpoint(
        target.address,
        "Exec",
        4,
        label,
        function()
            if state.frame_count < config.min_breakpoint_frame then
                return
            end

            local entry = state.handler_probe_hits[address_hex] or {
                label = label,
                opcodes = target.opcodes,
                hit_count = 0,
                pcs = {},
            }
            entry.hit_count = entry.hit_count + 1
            entry.pcs[#entry.pcs + 1] = current_pc_hex()
            state.handler_probe_hits[address_hex] = entry
            queue_safe(label .. " hit", function()
                log_trigger_hit(label, entry.hit_count, address_hex)
                add_note("script handler probe hit at " .. address_hex .. " for " .. table.concat(target.opcodes, ","))
            end)
        end
    )
end

local function ensure_runtime_table_instrumentation()
    local runtime_table_base = get_runtime_table_base()
    if runtime_table_base == nil or runtime_table_base == 0 then
        return
    end

    if state.runtime_table_base == nil then
        state.runtime_table_base = runtime_table_base
        add_note(
            "resolved runtime opcode table pointer slot "
                .. hex32(config.table_address)
                .. " -> "
                .. hex32(runtime_table_base)
        )
    end

    if not state.table_write_breakpoint_installed then
        add_runtime_table_write_breakpoint(runtime_table_base)
    end

    if not state.handler_probe_breakpoints_installed and #config.handler_probe_opcodes > 0 then
        local targets = build_handler_probe_targets()
        local plan = {}
        for _, target in ipairs(targets) do
            if target.address ~= 0 then
                add_handler_probe_breakpoint(target)
                plan[#plan + 1] = {
                    address = target.address_hex,
                    opcodes = target.opcodes,
                }
            end
        end
        state.handler_probe_plan = plan
        state.handler_probe_breakpoints_installed = true
        add_note("installed " .. tostring(#plan) .. " script handler probe breakpoint(s)")
    end
end

add_candidate_breakpoint(config.stub_address, "stub candidate")
if config.candidate_address ~= config.stub_address then
    add_candidate_breakpoint(config.candidate_address, "sound-family candidate")
end
if config.reader_caller_address ~= config.reader_address
    and config.reader_caller_address ~= config.stub_address
    and config.reader_caller_address ~= config.candidate_address then
    add_probe_breakpoint(config.reader_caller_address, "reader caller")
end
if config.reader_grandcaller_address ~= config.reader_address
    and config.reader_grandcaller_address ~= config.reader_caller_address
    and config.reader_grandcaller_address ~= config.stub_address
    and config.reader_grandcaller_address ~= config.candidate_address then
    add_probe_breakpoint(config.reader_grandcaller_address, "reader grandcaller")
end

listeners[#listeners + 1] = PCSX.Events.createEventListener("Quitting", function()
    queue_safe("quitting summary", function()
        clear_input_plan_overrides()
        write_summary()
    end)
end)

listeners[#listeners + 1] = PCSX.Events.createEventListener("ExecutionFlow::ShellReached", function()
    queue_safe("shell reached", function()
        if config.save_state_path ~= nil and config.save_state_path ~= "" and not state.save_state_load_requested then
            add_note("execution shell reached; loading deferred savestate")
            load_configured_save_state("ExecutionFlow::ShellReached")
        end
    end)
end)

listeners[#listeners + 1] = PCSX.Events.createEventListener("ExecutionFlow::SaveStateLoaded", function()
    state.save_state_load_count = state.save_state_load_count + 1
    add_note("savestate load event observed")
    PCSX.nextTick(function()
        state.frame_count = 0
        state.pre_dispatch_frame = nil
        reset_input_plan_progress()
        if state.snapshots.after_init == nil then
            dump_snapshot("after_init", config.after_init_path, "savestate_loaded")
        end
    end)
end)

if config.save_state_path ~= nil and config.save_state_path ~= "" then
    add_note("queued savestate load until ExecutionFlow::ShellReached")
end

function DrawImguiFrame()
    state.frame_count = state.frame_count + 1
    local cycles = tonumber(PCSX.getCPUCycles())

    ensure_runtime_table_instrumentation()
    update_input_plan()

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
        capture_screen("timeout", "timeout_before_capture_finished")
        request_quit(2, "timeout elapsed before capture finished")
    end
end

add_note("loaded automated opcode 0x80 runtime capture script")
