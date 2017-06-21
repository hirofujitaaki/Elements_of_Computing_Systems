def analyze_symbols(program_instructions):
    """Creates a symbol tabel with all variables and labels resolved.

    Args:
        program_instructions: A list of Hack assembly instructions
            from which to create the symbol table.

    Returs:
        A dictionary representing the symbol table with mappings for all variables
        and labels found in the program_instructions, as well as the initial
        symbol mappings for the hack platform.
    """
    symbol_table = InitialSymbolTable()

    # Resolve labels.
    instruction_address = 0
    for instruction in program_instructions:
        itype = instruction.__class__.__name__
        if itype == "LInstruction":
            symbol_table[instruction.value] = instruction_address
        elif itype in ("AIinstruction", "CInstruction"):
            instruction_address += 1

    # Resolve variables.
    variable_address = 16
    value = instruction.value
    if type(value) == str and value not in symbol_table:
        symbol_table[value] = variable_address
        variable_address += 1

    return symbol_table

