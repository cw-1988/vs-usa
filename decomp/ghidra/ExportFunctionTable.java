import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class ExportFunctionTable extends GhidraScript {

	private static String jsonEscape(String value) {
		return value.replace("\\", "\\\\").replace("\"", "\\\"");
	}

	private static String hex32(long value) {
		return String.format("0x%08X", value & 0xffffffffL);
	}

	private static Long parseLongValue(String value) {
		return Long.decode(value);
	}

	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length < 3) {
			throw new IllegalArgumentException(
				"usage: ExportFunctionTable.java <output_json> <table_addr> <entry_count> [table_name] [pointer_size]");
		}

		if (currentProgram == null) {
			throw new IllegalStateException("No current program is open");
		}

		String outputJson = args[0];
		long tableAddrRaw = parseLongValue(args[1]);
		int entryCount = Integer.decode(args[2]);
		String tableName = args.length >= 4 ? args[3] : "function_table";
		int pointerSize = args.length >= 5 ? Integer.decode(args[4]) : 4;

		if (pointerSize != 4) {
			throw new IllegalArgumentException("Only 4-byte pointer tables are supported right now");
		}

		Memory memory = currentProgram.getMemory();
		FunctionManager functionManager = currentProgram.getFunctionManager();
		SymbolTable symbolTable = currentProgram.getSymbolTable();
		Address tableAddr = toAddr(tableAddrRaw);

		StringBuilder json = new StringBuilder();
		json.append("{\n");
		json.append("  \"program_name\": \"").append(jsonEscape(currentProgram.getName())).append("\",\n");
		json.append("  \"program_path\": \"")
			.append(jsonEscape(currentProgram.getDomainFile().getPathname()))
			.append("\",\n");
		json.append("  \"table_name\": \"").append(jsonEscape(tableName)).append("\",\n");
		json.append("  \"table_address\": \"").append(hex32(tableAddrRaw)).append("\",\n");
		json.append("  \"entry_count\": ").append(entryCount).append(",\n");
		json.append("  \"pointer_size\": ").append(pointerSize).append(",\n");
		json.append("  \"entries\": [\n");

		for (int index = 0; index < entryCount; index++) {
			Address entryAddr = tableAddr.add((long) index * pointerSize);
			long rawValue = memory.getInt(entryAddr) & 0xffffffffL;
			Address targetAddr = toAddr(rawValue);

			Function function = functionManager.getFunctionAt(targetAddr);
			if (function == null) {
				function = functionManager.getFunctionContaining(targetAddr);
			}

			String handlerName = null;
			String functionEntry = null;
			if (function != null) {
				handlerName = function.getName();
				functionEntry = function.getEntryPoint().toString();
			} else {
				Symbol symbol = symbolTable.getPrimarySymbol(targetAddr);
				if (symbol != null) {
					handlerName = symbol.getName();
					functionEntry = targetAddr.toString();
				}
			}

			json.append("    {\n");
			json.append("      \"index\": ").append(index).append(",\n");
			json.append("      \"opcode\": \"").append(String.format("0x%02X", index)).append("\",\n");
			json.append("      \"entry_address\": \"").append(entryAddr.toString()).append("\",\n");
			json.append("      \"handler_address\": \"").append(hex32(rawValue)).append("\",\n");
			if (handlerName == null) {
				json.append("      \"handler_name\": null,\n");
			} else {
				json.append("      \"handler_name\": \"").append(jsonEscape(handlerName)).append("\",\n");
			}
			if (functionEntry == null) {
				json.append("      \"function_entry\": null\n");
			} else {
				json.append("      \"function_entry\": \"").append(jsonEscape(functionEntry)).append("\"\n");
			}
			json.append(index == entryCount - 1 ? "    }\n" : "    },\n");
		}

		json.append("  ]\n");
		json.append("}\n");

		Path outputPath = Path.of(outputJson);
		Path parent = outputPath.getParent();
		if (parent != null) {
			Files.createDirectories(parent);
		}
		Files.write(outputPath, json.toString().getBytes(StandardCharsets.UTF_8));

		println("wrote " + entryCount + " entries to " + outputJson);
	}
}
