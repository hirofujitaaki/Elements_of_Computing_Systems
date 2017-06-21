# Usage: python assembler.py file.asm
# require some adjustment for python3


import os
import re
import sys


_RE_SYMBOL = r"[a-zA-Z_\$\.:][a-zA-Z0-9\$\.:]*"


def remove_trailing_comment(line):
    """Removes the trailing comment from a line if one exists."""
    try:
        return line[:line.index("//")]
    except ValueError:
        return line


class AInstruction():
    """Responsible for parsing and binary encoding of Addressing Instructions."""

    _RE_AINSTRUCTION = re.compile(r"^@(\d*|" + _RE_SYMBOL + ")$")

    def __init__(self, value):
        self.value = value

    def to_binary(self):
        """Returns the binary encoding of the AInstruction instance."""
        return "0" + self._to_binary15(self.value)

    def _to_binary15(self, number):
        """Returns a 15-bit binary represention of number."""
        result = ""
        for i in range(15):
            result = str(number % 2) + result
            number = number / 2
        return result

    @staticmethod
    def parse(line):
        """Tries to parse a line of Hack assembly into an addressing Instruction.

        Args:
            line: The line of Hack assembly to parse

        Returs:
            On success an instance of AInstruction, on failure = False.
        """
        match = re.match(
                AInstruction._RE_AINSTRUCTION, remove_trailing_comment(line).strip())
        if match:
            return AInstruction._parseValue(match.group(1))
        else:
            return False

    @staticmethod
    def _parseValue(value):
        if value.isdigit():
            int_value = int(value)
            return AInstruction(int_value) if 0 <= int_value < (1 << 15) else False
        else:
            return AInstruction(value)


class CInstruction():
    """Responsible for parsing and binary encoding of Compute Instruction."""

    _RE_DEST = r"(?:(M|D|MD|A|AM|AD|AMD)=)?"
    _RE_JUMP = r"(?:;(JGT|JEQ|JGE|JLT|JNE|JLE|JMP))?"
    _RE_COMP = (
            r"(0|1|-1|D|A|!D|!A|-D|-A|D\+1|A\+1|D-1|A-1|D\+A|D-A|A-D|D&A|D\|A|"
            r"M|!M|-M|M\+1|M-1|D\+M|D-M|M-D|D&M|D\|M)")
    _RE_CINSTRUCTION = re.compile(r"^%s%s%s$" % (_RE_DEST, _RE_COMP, _RE_JUMP))

    _COMP_TABLE = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101"
            }

    _DEST_TABLE = {
            "": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
            }

    _JUMP_TABLE = {
            "": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
            }

    def __init__(self, dest, comp, jump):
        self.dest = dest
        self.comp = comp
        self.jump = jump

    def to_binary(self):
        """Returns the binary encoding of the CInstruction instance."""
        return "111%s%s%s" % (
                CInstruction._COMP_TABLE[self.comp],
                CInstruction._DEST_TABLE[self.dest],
                CInstruction._JUMP_TABLE[self.jump]
                )

    @staticmethod
    def parse(line):
        """Tries to parse a line of Hack assembly into a Compute Instruction.

        Args:
            line: The line of Hack assembly to parse.

        Returns:
            On success an instance of CInstruction, on failure - False.
        """
        match = re.match(
                CInstruction._RE_CINSTRUCTION, remove_trailing_comment(line).strip())
        if match:
            return CInstruction._parseMatch(match)
        else:
            return False

    @staticmethod
    def _parseMatch(match):
        dest = match.group(1) if match.group(1) else ""
        comp = match.group(2)
        jump = match.group(3) if match.group(3) else ""
        return CInstruction(dest, comp, jump)


class LInstruction():
    """Responsible for parsing and storing Hack assembly labels."""

    _RE_LINSTRUCTION = re.compile(r"^\((" + _RE_SYMBOL + ")\)$")

    def __init__(self, value):
        self.value = value

    @staticmethod
    def parse(line):
        """Tries to parse a line of Hack assembly into a Label.

        Args:
            line: The line of Hack assembly to parse
        Returns:
            On success an instance of LInstruction, on failure - False.
        """
        match = re.match(
                LInstruction._RE_LINSTRUCTION, remove_trailing_comment(line).strip())
        if match:
            return LInstruction(match.group(1))
        else:
            return False


class EmptyInstruction():
    """Represents a no oprand/operator line of Hack assembly - empty line of comment."""

    @staticmethod
    def parse(line):
        """Tries to parse a line of Hack assembly into a Label.

        Args:
            line: The line of Hack assembly to parse.

        Returns:
            On success an instance of EmptyInstruction, on failure - False.
        """
        stripped_line = remove_trailing_comment(line).strip()
        if stripped_line == "":
            return EmptyInstruction()
        else:
            return False


class ErrorInstruction():
    """Represents an invalid instruction Hack assembly instruction."""

    def __init__(self, line):
        self.line = line

    @staticmethod
    def parse(line):
        """Always succeeds in creating an ErrorInstruction instance."""
        return ErrorInstruction(line)


class AssemblerError(Exception):
    """Represents an error specific to the assembly process."""

    def __init__(self, error_message):
        self.error_message = error_message


# This list specifies the order in which the assembler will try to parse
# instructions in a line of Hack assembly.
_INSTRUCTIONS = [
        AInstruction,
        CInstruction,
        LInstruction,
        EmptyInstruction,
        ErrorInstruction]


def parseInstruction(line):
    """Given a line of Hack assembly, match it with the correct instruction type.

    The order in which the various instruction types are tried is determined by
    the _INSTRUCTIONS table.

    Args:
        line: The line of Hack assembly that is to be parsed.

    Returs:
        An instance of one of the instruction types. In case none of the valid
        instruction are matched an instanceof ErrorInstruction is returned.
    """
    for instruction in _INSTRUCTIONS:
        result = instruction.parse(line)
        if result:
            return result


def parse(program_lines):
    """Transforms a list of program lines into a list of parsed Instructions.

    Args:
        program_lines: A list of strings representing the list of lines
            in a Hack assembly program.

    Returns:
         A list of parsed program Instructions. There is one instructions for
         each line in the Hack assembly program.

    Raises:
        AssemblerError: At least one of of the instructions is an ErrorInstruction.
    """
    program_instructions = map(parse_instruction, program_lines)
    errors = []
    line_number = 1
    for instruction in program_instructions:
        if instruction.__class__.__name__ == "ErrorInstruction":
            errors.append("Error at line %d: %s" % (line_number, instruction.line))
        line_number += 1
    if len(errors) > 0:
        raise AssemblerError(os.linesep.join(errors))
    return program_instructions


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
    symbol_table = initial_symbol_table()

    # Resolve labels.
    instruction_address = 0
    for instruction in program_instructions:
        itype = instruction.__class__.__name__
        if itype == "LInstruction":
            symbol_table[instruction.value] = instruction_address
        elif itype in ("AInstruction", "CInstruction"):
            instruction_address += 1

    # Resolve variables.
    variable_address = 16
    value = instruction.value
    if type(value) == str and value not in symbol_table:
        symbol_table[value] = variable_address
        variable_address += 1

    return symbol_table

def strip_symbols(program_instructions):
    """Removes all symbolic references from the program_instructions.

    This function not only removes all symbolic references, but also
    removes all instruction types except AInstruction and CInstruction.
    No actual removals are done on the input parameter, instead a new
    list of instructions is returned.

    Args:
        program_instructions: A list of Hack assembly instructions.

    Return:
        A new list of Hack assembly instructions with all symbolic references
        substitued with thier numerical equivalents, and all none AInstruction
        and CInstruction instances removed.
    """
    stripped_instructions = []
    symbol_table = analyze_symbols(program_instructions)
    for instruction in program_instructions:
        itype = instruction.__class__.__name__
        if itype == "AInstruction":
            if type(instruction.value == str:
                    stripped_instructions.append(
                        AInstruction(symbol_table[instruction.value]))
            else:
                stripped_instructions.append(instructions)
        elif itype == "CInstruction":
            stripped_instructions.append(instruction)
    return stripped_instructions


def translate_to_binary(program_instructions):
    """ Transforms a list of instructions into a list of their binary codes.

    Args:
        program_instructions: A list of Hack assembly instructions.

    Returns:
        A list of the binary machine codes for the given instructions.
    """
    return map(lambda i: i.ToBinary(), program_instructions)


def assemble(program_lines):
    """Transforms the lines of a program into a list of binary instructions.

    Args:
        program_lines: A list of strings representing the lines of a Hack program.

    Returns:
        A list of binary instructions for the assembled rogram.
    """
    return translate_to_binary(strip_symbols(parse(program_lines)))




def main():
    if len(sys.argv) != 2:
        print("Please specify exactly one argument, the program name.")
        return

    asm_file = sys.argv[1]
    if not asm_file.endswith(".asm"):
        print("The file must end with: .asm")
        return

    try:
        with open(asm_file, "r") as asm_program:
            binary_lines = assemble(asm_program.readlines())
            with open(asm_file[:-4] + ".hack", "w") as hack_program:
                hack_program.write(os.linesep.join(binary_lines))
        except AssemblerError as error:
            print error.error_message
        except IOError as error:
            print error


if __name__ == "__main__":
    main()