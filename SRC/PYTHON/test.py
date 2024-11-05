import tkinter as tk
from tkinter import messagebox

# Sample OPTAB (simplified)
OPTAB = {
    'LDA': 0x00, 'ADD': 0x18, 'SUB': 0x1C, 'STA': 0x0C, 'JSUB': 0x48, 'J': 0x3C, 'LDX': 0x04, 'MUL': 0x20
    # Add more opcodes as needed
}

def is_valid(symbol, line_number, lines):
    """
    Validate symbol for Pass 1.
    """
    if len(symbol) > 6:
        messagebox.showerror("Error", f"Symbol is too long at line {line_number + 1}")
        return False
    if not symbol.isalnum():
        messagebox.showerror("Error", f"Symbol contains invalid characters at line {line_number + 1}")
        return False
    if (symbol == 'START' and line_number != 0) or (symbol != 'START' and line_number == 0):
        messagebox.showerror("Error", f"START must be the first line (line {line_number + 1})")
        return False
    if (symbol == 'END' and line_number != len(lines) - 1) or (symbol != 'END' and line_number == len(lines) - 1):
        messagebox.showerror("Error", f"END must be the last line (line {line_number + 1})")
        return False
    return True

def pass1(lines):
    """
    Perform Pass 1 to generate Symbol Table (SYMTAB) and calculate Program Length.
    """
    starting = 0
    locctr = 0
    proglen = 0
    symbol_table = {}
    output = []

    lines = lines.split('\n')
    for i, line in enumerate(lines):
        parts = line.split()  # Decompose line (simplified version)
        if len(parts) < 2:
            continue  # Skip empty lines or malformed lines

        label, opcode, *operand = parts

        # Validate the symbol for Pass 1
        if not is_valid(label, i, lines):
            return None, None, None  # Early exit on invalid input

        if opcode == 'START':
            starting = int(operand[0], 16) if operand else 0
            locctr = starting
            output.append(f"START at {hex(starting)}")
            continue

        if opcode == 'END':
            proglen = locctr - starting
            output.append(f"Program Length: {hex(proglen)}")
            continue

        # Update the symbol table for labels
        if label and label != 'START' and label != 'END':
            if label in symbol_table:
                messagebox.showerror("Error", f"Duplicate Symbol: {label} (line {i + 1})")
                return None, None, None
            symbol_table[label] = hex(locctr)

        # Handle instructions and directives
        if opcode in OPTAB:
            locctr += 3  # Each instruction is 3 bytes
        elif opcode == 'WORD':
            locctr += 3  # Word takes 3 bytes
        elif opcode == 'RESW':
            locctr += int(operand[0]) * 3  # Reserved word takes 3 bytes per word
        elif opcode == 'RESB':
            locctr += int(operand[0])  # Reserved byte
        elif opcode == 'BYTE':
            if operand[0] == 'C':
                locctr += len(operand[1]) - 3  # 'C' string literal length
            elif operand[0] == 'X':
                locctr += (len(operand[1]) - 3) // 2  # 'X' hex string length

        output.append(f"{hex(locctr)}\t{line}")

    return symbol_table, proglen, output

def pass2(lines, symbol_table, proglen):
    """
    Perform Pass 2 to generate object code based on the symbol table and OPTAB.
    """
    output = []
    locctr = 0
    current_line = ""

    for line in lines.split('\n'):
        parts = line.split()
        if len(parts) < 2:
            continue  # Skip empty lines or malformed lines

        label, opcode, *operand = parts

        # Generate object code for instructions in Pass 2
        if opcode in OPTAB:
            opcode_hex = hex(OPTAB[opcode])[2:].upper().zfill(2)  # Get opcode in hex
            operand_address = '0000'  # Default address if operand is not found in SYMTAB

            # Handle indexed addressing mode (e.g., LDA ALPHA,X)
            if operand and ',X' in operand[0]:
                operand[0] = operand[0].replace(',X', '')
                operand_address = symbol_table.get(operand[0], '0000')  # Get symbol address
                operand_address = (int(operand_address, 16) | 0x8000)  # Set index bit (bit 15)
                operand_address = hex(operand_address)[2:].upper().zfill(4)
            elif operand:
                operand_address = symbol_table.get(operand[0], '0000')  # Direct addressing

            # Ensure the operand address is found
            if operand_address == '0000':
                messagebox.showerror("Error", f"Symbol '{operand[0]}' not found in symbol table.")
                return []

            object_code = opcode_hex + operand_address
            current_line += object_code
            locctr += 3  # Each instruction is 3 bytes

        elif opcode == 'WORD':
            object_code = hex(int(operand[0]))[2:].upper().zfill(6)  # Word value (6 hex digits)
            current_line += object_code
            locctr += 3  # Word is 3 bytes

        elif opcode == 'BYTE':
            if operand[0][0] == 'C':  # Character literal
                constant = ''.join([hex(ord(ch))[2:].upper().zfill(2) for ch in operand[0][2:-1]])
                current_line += constant
                locctr += len(constant) // 2  # One byte per character
            elif operand[0][0] == 'X':  # Hexadecimal literal
                constant = operand[0][2:-1]  # Strip X' ' and take hex digits
                current_line += constant
                locctr += len(constant) // 2  # Each hex digit is one byte

        elif opcode == 'RESB':
            locctr += int(operand[0])  # Reserve bytes
            continue

        elif opcode == 'RESW':
            locctr += int(operand[0]) * 3  # Reserve words (3 bytes per word)
            continue

        else:
            messagebox.showerror("Error", f"Invalid opcode: {opcode}")
            return []

        # If line length exceeds 60, write the current line and start a new one
        if len(current_line) > 60:
            output.append(current_line)
            current_line = ""  # Reset for the next line

    if current_line:
        output.append(current_line)  # Append remaining content if any

    return output


# GUI setup
def on_pass1_button_click():
    source_code = code_input.get("1.0", tk.END).strip()
    symbol_table, proglen, output = pass1(source_code)
    
    if symbol_table is None:
        return  # If Pass1 fails, don't proceed to Pass2
    
    symbol_table_text.delete(1.0, tk.END)
    symbol_table_text.insert(tk.END, "\n".join([f"{k}: {v}" for k, v in symbol_table.items()]))
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\n".join(output))

def on_pass2_button_click():
    source_code = code_input.get("1.0", tk.END).strip()
    symbol_table_text_content = symbol_table_text.get("1.0", tk.END).strip().splitlines()
    symbol_table = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in symbol_table_text_content}
    
    if not symbol_table:
        messagebox.showerror("Error", "Pass 1 must be run first to generate the symbol table.")
        return
    
    proglen = int(proglen_input.get(), 16) if proglen_input.get() else 0
    output = pass2(source_code, symbol_table, proglen)
    
    if not output:
        messagebox.showerror("Error", "Pass 2 failed.")
        return
    
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "\n".join(output))

# Tkinter GUI
root = tk.Tk()
root.title("SIC Assembler")

# Assembly code input area
code_label = tk.Label(root, text="Enter Assembly Code:")
code_label.pack()

code_input = tk.Text(root, height=10, width=80)
code_input.pack()

# Buttons for running Pass 1 and Pass 2
pass1_button = tk.Button(root, text="Run Pass 1", command=on_pass1_button_click)
pass1_button.pack()

pass2_button = tk.Button(root, text="Run Pass 2", command=on_pass2_button_click)
pass2_button.pack()

# Symbol table display
symbol_table_label = tk.Label(root, text="Symbol Table:")
symbol_table_label.pack()

symbol_table_text = tk.Text(root, height=10, width=80)
symbol_table_text.pack()

# Program length input
proglen_label = tk.Label(root, text="Program Length (in Hex, for Pass 2):")
proglen_label.pack()

proglen_input = tk.Entry(root)
proglen_input.pack()

# Output display
output_label = tk.Label(root, text="Output:")
output_label.pack()

output_text = tk.Text(root, height=10, width=80)
output_text.pack()

# Start the GUI
root.mainloop()
