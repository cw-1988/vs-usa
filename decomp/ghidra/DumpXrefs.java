import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

public class DumpXrefs extends GhidraScript {

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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            throw new IllegalArgumentException(
                "usage: DumpXrefs.java <output_json> <target_addr> [before_count] [after_count]");
        }

        if (currentProgram == null) {
            throw new IllegalStateException("No current program is open");
        }

        Path outputPath = Path.of(args[0]);
        Address target = toAddr(Long.decode(args[1]));
        int beforeCount = args.length >= 3 ? Integer.decode(args[2]) : 3;
        int afterCount = args.length >= 4 ? Integer.decode(args[3]) : 6;

        ReferenceManager referenceManager = currentProgram.getReferenceManager();
        Listing listing = currentProgram.getListing();
        List<String> rows = new ArrayList<>();

        ReferenceIterator refs = referenceManager.getReferencesTo(target);
        while (refs.hasNext()) {
            Reference ref = refs.next();
            Address from = ref.getFromAddress();
            Instruction refInstruction = listing.getInstructionContaining(from);
            Function function = getFunctionContaining(from);
            String functionName = function == null ? null : function.getName();
            String functionEntry = function == null ? null : function.getEntryPoint().toString();

            List<String> instructionRows = new ArrayList<>();
            if (refInstruction != null) {
                Instruction cursor = rewind(refInstruction, beforeCount);
                int budget = beforeCount + afterCount + 1;
                for (int i = 0; i < budget && cursor != null; i++) {
                    instructionRows.add(
                        "          {\n" +
                        "            \"address\": \"" + cursor.getAddress().toString() + "\",\n" +
                        "            \"text\": \"" + jsonEscape(cursor.toString()) + "\"\n" +
                        "          }");
                    cursor = cursor.getNext();
                }
            }

            if (instructionRows.isEmpty()) {
                instructionRows = Collections.singletonList(
                    "          {\n" +
                    "            \"address\": \"" + from.toString() + "\",\n" +
                    "            \"text\": null\n" +
                    "          }");
            }

            StringBuilder row = new StringBuilder();
            row.append("    {\n");
            row.append("      \"from_address\": \"").append(from.toString()).append("\",\n");
            row.append("      \"reference_type\": \"").append(jsonEscape(ref.getReferenceType().toString()))
                .append("\",\n");
            if (functionName == null) {
                row.append("      \"function_name\": null,\n");
                row.append("      \"function_entry\": null,\n");
            } else {
                row.append("      \"function_name\": \"").append(jsonEscape(functionName)).append("\",\n");
                row.append("      \"function_entry\": \"").append(jsonEscape(functionEntry)).append("\",\n");
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
        json.append("  \"before_count\": ").append(beforeCount).append(",\n");
        json.append("  \"after_count\": ").append(afterCount).append(",\n");
        json.append("  \"xrefs\": [\n");
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
        println("wrote xref dump to " + outputPath);
    }
}
