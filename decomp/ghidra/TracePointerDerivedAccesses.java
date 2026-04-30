import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;

public class TracePointerDerivedAccesses extends GhidraScript {

    private static final Pattern OFFSET_PATTERN =
        Pattern.compile("^([+-]?0x[0-9a-fA-F]+)\\(([^)]+)\\)$");
    private static final Pattern LUI_PATTERN =
        Pattern.compile("^lui\\s+([^,]+),([+-]?0x[0-9a-fA-F]+)$", Pattern.CASE_INSENSITIVE);

    private static final Set<String> READ_MNEMONICS = new HashSet<>(Arrays.asList(
        "lb", "lbu", "lh", "lhu", "lw", "lwl", "lwr", "ll", "lwc2"
    ));
    private static final Set<String> WRITE_MNEMONICS = new HashSet<>(Arrays.asList(
        "sb", "sh", "sw", "swl", "swr", "sc", "swc2"
    ));
    private static final Set<String> PROPAGATE_BINARY_MNEMONICS = new HashSet<>(Arrays.asList(
        "addu", "addiu", "subu", "or", "ori"
    ));
    private static final Set<String> CALLER_SAVED_REGISTERS = new HashSet<>(Arrays.asList(
        "at", "v0", "v1",
        "a0", "a1", "a2", "a3",
        "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9",
        "ra"
    ));

    private static String jsonEscape(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String normalizeMnemonic(String mnemonic) {
        return mnemonic.trim().toLowerCase(Locale.ROOT).replaceFirst("^_+", "");
    }

    private static String normalizeRegister(String registerName) {
        return registerName.trim().toLowerCase(Locale.ROOT).replace("$", "");
    }

    private static long parseNumber(String value) {
        if (value.startsWith("-0x") || value.startsWith("-0X")) {
            return -Long.parseLong(value.substring(3), 16);
        }
        return Long.decode(value);
    }

    private static String[] splitInstruction(String text) {
        return text.trim().split("\\s+", 2);
    }

    private static String[] splitOperands(String operandText) {
        if (operandText == null || operandText.isBlank()) {
            return new String[0];
        }

        String[] raw = operandText.split(",");
        String[] normalized = new String[raw.length];
        for (int i = 0; i < raw.length; i++) {
            normalized[i] = raw[i].trim();
        }
        return normalized;
    }

    private static String classifyAccess(String mnemonic) {
        if (READ_MNEMONICS.contains(mnemonic)) {
            return "read";
        }
        if (WRITE_MNEMONICS.contains(mnemonic)) {
            return "write";
        }
        return "other";
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

    private static String formatJsonArray(List<String> values, int indentSpaces) {
        if (values.isEmpty()) {
            return "[]";
        }

        String indent = " ".repeat(indentSpaces);
        String innerIndent = indent + "  ";
        return "[\n" + innerIndent + String.join(",\n" + innerIndent, values) + "\n" + indent + "]";
    }

    private static String jsonStringArray(List<String> values) {
        List<String> escaped = new ArrayList<>();
        for (String value : values) {
            escaped.add("\"" + jsonEscape(value) + "\"");
        }
        return formatJsonArray(escaped, 10);
    }

    private static void clearCallerSaved(Set<String> taintedRegisters) {
        taintedRegisters.removeAll(CALLER_SAVED_REGISTERS);
    }

    private static void assignTaint(Set<String> taintedRegisters, String destination, boolean isTainted) {
        String normalizedDestination = normalizeRegister(destination);
        if (normalizedDestination.equals("zero")) {
            return;
        }

        if (isTainted) {
            taintedRegisters.add(normalizedDestination);
        } else {
            taintedRegisters.remove(normalizedDestination);
        }
    }

    private static List<String> sortedRegisters(Set<String> taintedRegisters) {
        List<String> registers = new ArrayList<>(taintedRegisters);
        registers.sort(String::compareTo);
        return registers;
    }

    private static String makeUseRow(
        String address,
        String text,
        String kind,
        String details
    ) {
        StringBuilder row = new StringBuilder();
        row.append("{\n");
        row.append("          \"address\": \"").append(address).append("\",\n");
        row.append("          \"text\": \"").append(jsonEscape(text)).append("\",\n");
        row.append("          \"kind\": \"").append(kind).append("\"");
        if (details != null && !details.isBlank()) {
            row.append(",\n").append(details).append("\n");
        } else {
            row.append("\n");
        }
        row.append("        }");
        return row.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 4) {
            throw new IllegalArgumentException(
                "usage: TracePointerDerivedAccesses.java <output_json> <target_addr> <seed_addr> <instruction_limit> [backward_window]");
        }

        if (currentProgram == null) {
            throw new IllegalStateException("No current program is open");
        }

        Path outputPath = Path.of(args[0]);
        long targetValue = Long.decode(args[1]);
        Address target = toAddr(targetValue);
        Address seed = toAddr(Long.decode(args[2]));
        int instructionLimit = Integer.decode(args[3]);
        int backwardWindow = args.length >= 5 ? Integer.decode(args[4]) : 6;
        long targetUpper = (targetValue >>> 16) & 0xffffL;
        long targetLower = targetValue & 0xffffL;

        disassemble(seed);

        Listing listing = currentProgram.getListing();
        Function function = getFunctionContaining(seed);
        Instruction instruction = listing.getInstructionAt(seed);
        List<String> useRows = new ArrayList<>();
        Set<String> taintedRegisters = new HashSet<>();
        String directReadAddress = null;
        String directReadText = null;
        String taintRootRegister = null;

        for (int steps = 0; steps < instructionLimit && instruction != null; steps++) {
            if (function != null && !function.getBody().contains(instruction.getAddress())) {
                break;
            }

            String text = instruction.toString().trim();
            String[] instructionParts = splitInstruction(text);
            String mnemonic = normalizeMnemonic(instructionParts[0]);
            String operandText = instructionParts.length >= 2 ? instructionParts[1] : "";
            String[] operands = splitOperands(operandText);

            if (operands.length >= 2) {
                Matcher offsetMatcher = OFFSET_PATTERN.matcher(operands[1]);
                if (offsetMatcher.matches()) {
                    long offset = parseNumber(offsetMatcher.group(1)) & 0xffffL;
                    String baseRegister = normalizeRegister(offsetMatcher.group(2));
                    String accessKind = classifyAccess(mnemonic);
                    String firstOperand = normalizeRegister(operands[0]);
                    boolean isDirectTargetRead = false;

                    if (offset == targetLower) {
                        Instruction matchingLui = findMatchingLui(
                            instruction,
                            baseRegister,
                            targetUpper,
                            backwardWindow
                        );
                        if (matchingLui != null && accessKind.equals("read")) {
                            taintedRegisters.add(firstOperand);
                            directReadAddress = instruction.getAddress().toString();
                            directReadText = text;
                            taintRootRegister = firstOperand;
                            isDirectTargetRead = true;
                        }
                    }

                    if (!isDirectTargetRead && taintedRegisters.contains(baseRegister) && !accessKind.equals("other")) {
                        String details =
                            "          \"access_kind\": \"" + accessKind + "\",\n" +
                            "          \"base_register\": \"" + jsonEscape(baseRegister) + "\",\n" +
                            "          \"tainted_registers_before\": " + jsonStringArray(sortedRegisters(taintedRegisters));
                        useRows.add(makeUseRow(
                            instruction.getAddress().toString(),
                            text,
                            "derived_" + accessKind,
                            details
                        ));

                        if (accessKind.equals("read")) {
                            assignTaint(taintedRegisters, firstOperand, false);
                        }
                    }
                }
            }

            if (mnemonic.equals("move") && operands.length == 2) {
                boolean sourceTainted = taintedRegisters.contains(normalizeRegister(operands[1]));
                assignTaint(taintedRegisters, operands[0], sourceTainted);
                if (sourceTainted) {
                    String details =
                        "          \"destination_register\": \"" + jsonEscape(normalizeRegister(operands[0])) + "\",\n" +
                        "          \"source_register\": \"" + jsonEscape(normalizeRegister(operands[1])) + "\",\n" +
                        "          \"tainted_registers_after\": " + jsonStringArray(sortedRegisters(taintedRegisters));
                    useRows.add(makeUseRow(
                        instruction.getAddress().toString(),
                        text,
                        "pointer_alias",
                        details
                    ));
                }
            } else if (PROPAGATE_BINARY_MNEMONICS.contains(mnemonic) && operands.length == 3) {
                boolean sourceTainted =
                    taintedRegisters.contains(normalizeRegister(operands[1])) ||
                    taintedRegisters.contains(normalizeRegister(operands[2]));
                assignTaint(taintedRegisters, operands[0], sourceTainted);
                if (sourceTainted) {
                    String details =
                        "          \"destination_register\": \"" + jsonEscape(normalizeRegister(operands[0])) + "\",\n" +
                        "          \"source_registers\": " + jsonStringArray(Arrays.asList(
                            normalizeRegister(operands[1]),
                            normalizeRegister(operands[2])
                        )) + ",\n" +
                        "          \"tainted_registers_after\": " + jsonStringArray(sortedRegisters(taintedRegisters));
                    useRows.add(makeUseRow(
                        instruction.getAddress().toString(),
                        text,
                        "pointer_arithmetic",
                        details
                    ));
                }
            } else if ((mnemonic.equals("lui") || mnemonic.equals("li")) && operands.length >= 1) {
                assignTaint(taintedRegisters, operands[0], false);
            }

            if (mnemonic.equals("jal") || mnemonic.equals("jalr")) {
                List<String> taintedArgs = new ArrayList<>();
                for (String argumentRegister : Arrays.asList("a0", "a1", "a2", "a3")) {
                    if (taintedRegisters.contains(argumentRegister)) {
                        taintedArgs.add(argumentRegister);
                    }
                }

                if (!taintedArgs.isEmpty()) {
                    String details =
                        "          \"tainted_argument_registers\": " + jsonStringArray(taintedArgs) + ",\n" +
                        "          \"tainted_registers_before\": " + jsonStringArray(sortedRegisters(taintedRegisters));
                    useRows.add(makeUseRow(
                        instruction.getAddress().toString(),
                        text,
                        "call_with_tainted_args",
                        details
                    ));
                }

                clearCallerSaved(taintedRegisters);
            }

            instruction = instruction.getNext();
        }

        String functionName = function == null ? null : function.getName();
        String functionEntry = function == null ? null : function.getEntryPoint().toString();

        StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"program_name\": \"").append(jsonEscape(currentProgram.getName())).append("\",\n");
        json.append("  \"target\": \"").append(target.toString()).append("\",\n");
        json.append("  \"seed_address\": \"").append(seed.toString()).append("\",\n");
        json.append("  \"instruction_limit\": ").append(instructionLimit).append(",\n");
        json.append("  \"backward_window\": ").append(backwardWindow).append(",\n");
        if (functionName == null) {
            json.append("  \"function_name\": null,\n");
            json.append("  \"function_entry\": null,\n");
        } else {
            json.append("  \"function_name\": \"").append(jsonEscape(functionName)).append("\",\n");
            json.append("  \"function_entry\": \"").append(jsonEscape(functionEntry)).append("\",\n");
        }
        if (directReadAddress == null) {
            json.append("  \"direct_read_address\": null,\n");
            json.append("  \"direct_read_text\": null,\n");
            json.append("  \"taint_root_register\": null,\n");
        } else {
            json.append("  \"direct_read_address\": \"").append(directReadAddress).append("\",\n");
            json.append("  \"direct_read_text\": \"").append(jsonEscape(directReadText)).append("\",\n");
            json.append("  \"taint_root_register\": \"").append(jsonEscape(taintRootRegister)).append("\",\n");
        }
        json.append("  \"derived_uses\": ");
        json.append(formatJsonArray(useRows, 2));
        json.append("\n");
        json.append("}\n");

        Path parent = outputPath.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        Files.write(outputPath, json.toString().getBytes(StandardCharsets.UTF_8));
        println("wrote pointer-derived access trace to " + outputPath);
    }
}
