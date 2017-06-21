def initial_symbol_table():
    """Returns a dictionary filled with the initial symbol table value."""
    symbol_table = {
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KDB": 24576
            }
    for i in range(16):
        symbol_table["R%d" % (i,)] = i
    return symbol_table


