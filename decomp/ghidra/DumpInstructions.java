import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;

public class DumpInstructions extends GhidraScript {

	private static String jsonEscape(String value) {
		return value.replace("\\", "\\\\").replace("\"", "\\\"");
	}

	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length < 3) {
			throw new IllegalArgumentException(
				"usage: DumpInstructions.java <output_json> <address> [<address> ...] <instruction_count>");
		}

		if (currentProgram == null) {
			throw new IllegalStateException("No current program is open");
		}

		Path outputPath = Path.of(args[0]);
		int instructionCount = Integer.decode(args[args.length - 1]);
		Listing listing = currentProgram.getListing();

		StringBuilder json = new StringBuilder();
		json.append("{\n");
		json.append("  \"program_name\": \"").append(jsonEscape(currentProgram.getName())).append("\",\n");
		json.append("  \"instruction_count\": ").append(instructionCount).append(",\n");
		json.append("  \"slices\": [\n");

		for (int sliceIndex = 1; sliceIndex < args.length - 1; sliceIndex++) {
			String rawAddress = args[sliceIndex].trim();
			Address start = toAddr(Long.decode(rawAddress));
			disassemble(start);

			json.append("    {\n");
			json.append("      \"start\": \"").append(start.toString()).append("\",\n");
			json.append("      \"instructions\": [\n");

			Instruction instruction = listing.getInstructionAt(start);
			List<String> rows = new ArrayList<>();
			for (int i = 0; i < instructionCount && instruction != null; i++) {
				rows.add(
					"        {\n" +
					"          \"address\": \"" + instruction.getAddress().toString() + "\",\n" +
					"          \"text\": \"" + jsonEscape(instruction.toString()) + "\"\n" +
					"        }");
				instruction = instruction.getNext();
			}

			if (rows.isEmpty()) {
				rows.add(
					"        {\n" +
					"          \"address\": \"" + start.toString() + "\",\n" +
					"          \"text\": null\n" +
					"        }");
			}

			json.append(String.join(",\n", rows));
			json.append("\n");
			json.append("      ]\n");
			json.append(sliceIndex == args.length - 2 ? "    }\n" : "    },\n");
		}

		json.append("  ]\n");
		json.append("}\n");

		Path parent = outputPath.getParent();
		if (parent != null) {
			Files.createDirectories(parent);
		}
		Files.write(outputPath, json.toString().getBytes(StandardCharsets.UTF_8));
		println("wrote instruction dump to " + outputPath);
	}
}
