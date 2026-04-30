import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

public class DumpAddressAccesses extends GhidraScript {

    private static final Pattern OFFSET_PATTERN =
        Pattern.compile(".*?([+-]?0x[0-9a-fA-F]+)\\(([^)]+)\\)");
    private static final Pattern LUI_PATTERN =
        Pattern.compile("^lui\\s+([^,]+),([+-]?0x[0-9a-fA-F]+)$", Pattern.CASE_INSENSITIVE);

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static Instruction rewind(Instruction cursor, int steps) {
        Instruction current = cursor;
        for (int i = 0; i < steps && current != null && current.getPrevious() != null; i++) {
            current = current.getPrevious();
        }
        return current;
    }

    private static long parseNumber(String value) {
        if (value.startsWith("-0x") || value.startsWith("-0X")) {
            return -Long.parseLong(value.substring(3), 16);
        }
        return Long.decode(value);
    }

    private static String normalizeRegister(String registerName) {
        return registerName.trim().toLowerCase(Locale.ROOT);
    }

    private static String classifyAccess(String mnemonic) {
        String normalized = mnemonic.toLowerCase(Locale.ROOT).replaceFirst("^_+", "");
        switch (normalized) {
            case "lb":
            case "lbu":
            case "lh":
            case "lhu":
            case "lw":
            case "lwl":
            case "lwr":
            case "ll":
            case "lwc2":
                return "read";
            case "sb":
            case "sh":
            case "sw":
            case "swl":
            case "swr":
            case "sc":
            case "swc2":
                return "write";
            default:
                return "other";
        }
    }

    private static Instruction findMatchingLui(
        Instruction instruction,
        String registerName,
        long targetUpper,
        int backwardWindow
    ) {
        String wantedRegister = normalizeRegister(registerName);
        Instruction cursor = instruction.getPrevious();
        for (int i = 0; i < backwardWindow && cursor != null; i++) {
            Matcher luiMatcher = LUI_PATTERN.matcher(cursor.toString().trim());
            if (luiMatcher.matches()) {
                String candidateRegister = normalizeRegister(luiMatcher.group(1));
                if (!candidateRegister.equals(wantedRegister)) {
                    cursor = cursor.getPrevious();
                    continue;
                }

                long candidateUpper = parseNumber(luiMatcher.group(2)) & 0xffffL;
                if (candidateUpper == targetUpper) {
                    return cursor;
                }
            }
            cursor = cursor.getPrevious();
        }
        return null;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException(
                "usage: DumpAddressAccesses.java <output_json> <target_addr> [backward_window] [before_count] [after_count] [seed_addr ...]");
        }

        if (currentProgram == null) {
            throw new IllegalStateException("No current program is open");
        }

        Path outputPath = Path.of(args[0]);
        long targetValue = Long.decode(args[1]);
        Address target = toAddr(targetValue);
        int backwardWindow = args.length >= 3 ? Integer.decode(args[2]) : 6;
        int beforeCount = args.length >= 4 ? Integer.decode(args[3]) : 4;
        int afterCount = args.length >= 5 ? Integer.decode(args[4]) : 8;
        long targetUpper = (targetValue >>> 16) & 0xffffL;
        long targetLower = targetValue & 0xffffL;

        for (int i = 5; i < args.length; i++) {
            disassemble(toAddr(Long.decode(args[i])));
        }

        Listing listing = currentProgram.getListing();
        InstructionIterator instructions = listing.getInstructions(true);
        List<String> rows = new ArrayList<>();

        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            String text = instruction.toString().trim();
            Matcher offsetMatcher = OFFSET_PATTERN.matcher(text);
            if (!offsetMatcher.matches()) {
                continue;
            }

            long offset = parseNumber(offsetMatcher.group(1)) & 0xffffL;
            if (offset != targetLower) {
                continue;
            }

            String registerName = offsetMatcher.group(2);
            Instruction matchingLui =
                findMatchingLui(instruction, registerName, targetUpper, backwardWindow);
            if (matchingLui == null) {
                continue;
            }

            Function function = getFunctionContaining(instruction.getAddress());
            String functionName = function == null ? null : function.getName();
            String functionEntry = function == null ? null : function.getEntryPoint().toString();

            List<String> instructionRows = new ArrayList<>();
            Instruction cursor = rewind(instruction, beforeCount);
            int budget = beforeCount + afterCount + 1;
            for (int i = 0; i < budget && cursor != null; i++) {
                instructionRows.add(
                    "          {\n" +
                    "            \"address\": \"" + cursor.getAddress().toString() + "\",\n" +
                    "            \"text\": \"" + jsonEscape(cursor.toString()) + "\"\n" +
                    "          }");
                cursor = cursor.getNext();
            }

            if (instructionRows.isEmpty()) {
                instructionRows = Collections.singletonList(
                    "          {\n" +
                    "            \"address\": \"" + instruction.getAddress().toString() + "\",\n" +
                    "            \"text\": null\n" +
                    "          }");
            }

            StringBuilder row = new StringBuilder();
            row.append("    {\n");
            row.append("      \"instruction_address\": \"")
                .append(instruction.getAddress().toString())
                .append("\",\n");
            row.append("      \"instruction_text\": \"")
                .append(jsonEscape(text))
                .append("\",\n");
            row.append("      \"access_kind\": \"")
                .append(classifyAccess(instruction.getMnemonicString()))
                .append("\",\n");
            row.append("      \"base_register\": \"")
                .append(jsonEscape(normalizeRegister(registerName)))
                .append("\",\n");
            row.append("      \"matching_lui_address\": \"")
                .append(matchingLui.getAddress().toString())
                .append("\",\n");
            row.append("      \"matching_lui_text\": \"")
                .append(jsonEscape(matchingLui.toString()))
                .append("\",\n");
            if (functionName == null) {
                row.append("      \"function_name\": null,\n");
                row.append("      \"function_entry\": null,\n");
            } else {
                row.append("      \"function_name\": \"")
                    .append(jsonEscape(functionName))
                    .append("\",\n");
                row.append("      \"function_entry\": \"")
                    .append(jsonEscape(functionEntry))
                    .append("\",\n");
            }
            row.append("      \"instructions\": [\n");
            row.append(String.join(",\n", instructionRows));
            row.append("\n");
            row.append("      ]\n");
            row.append("    }");
            rows.add(row.toString());
        }

        StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"program_name\": \"").append(jsonEscape(currentProgram.getName())).append("\",\n");
        json.append("  \"target\": \"").append(target.toString()).append("\",\n");
        json.append("  \"backward_window\": ").append(backwardWindow).append(",\n");
        json.append("  \"before_count\": ").append(beforeCount).append(",\n");
        json.append("  \"after_count\": ").append(afterCount).append(",\n");
        json.append("  \"matches\": [\n");
        json.append(String.join(",\n", rows));
        if (!rows.isEmpty()) {
            json.append("\n");
        }
        json.append("  ]\n");
        json.append("}\n");

        Path parent = outputPath.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        Files.write(outputPath, json.toString().getBytes(StandardCharsets.UTF_8));
        println("wrote address access dump to " + outputPath);
    }
}
