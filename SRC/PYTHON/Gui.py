import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk  # Make sure you have Pillow installed

class MachineCodeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Machine Code Converter")
        self.root.geometry("500x600")
        self.root.configure(bg="#D3D3D3")  # Light gray background to mimic Windows theme

        # Initialize attributes for symbol table and machine code output
        self.symbol_table = {}
        self.address_counter = 0
        self.machine_code = []

        # Apply a theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#D3D3D3", foreground="#000000", font=("Segoe UI", 10))
        style.configure("TButton", background="#E6E6E6", foreground="#000000", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#C0C0C0")])  # Change button color on hover
        style.configure("TEntry", background="#FFFFFF", foreground="#000000", font=("Segoe UI", 10))

        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        # Title label
        title_label = ttk.Label(self.root, text="Machine Code Converter", font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Input field for assembly code
        ttk.Label(self.root, text="Enter Assembly Code:").grid(row=1, column=0, padx=10, pady=5)
        self.code_text = tk.Text(self.root, height=8, width=40, bg="#FFFFFF", fg="#000000", font=("Courier New", 10))
        self.code_text.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

        # Convert and Clear buttons
        convert_button = ttk.Button(self.root, text="Convert", command=self.choose_pass)
        convert_button.grid(row=3, column=0, pady=10)
        clear_button = ttk.Button(self.root, text="Clear", command=self.clear_all)
        clear_button.grid(row=3, column=1, pady=10)

        # Output Symbol Table
        ttk.Label(self.root, text="Symbol Table (Pass 1):").grid(row=4, column=0, padx=10, pady=5)
        self.symbol_table_text = tk.Text(self.root, height=8, width=40, bg="#FFFFFF", fg="#000000", font=("Courier New", 10), state="disabled")
        self.symbol_table_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        # Output Machine Code
        ttk.Label(self.root, text="Machine Code (Pass 2):").grid(row=6, column=0, padx=10, pady=5)
        self.machine_code_text = tk.Text(self.root, height=8, width=40, bg="#FFFFFF", fg="#000000", font=("Courier New", 10), state="disabled")
        self.machine_code_text.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    def choose_pass(self):
        # Dialog box to choose Pass 1 or Pass 2
        choice = simpledialog.askstring("Choose Pass", "Enter '1' for Pass 1 or '2' for Pass 2:", parent=self.root)
        
        if choice == "1":
            self.run_pass1()
        elif choice == "2":
            self.run_pass2()
        else:
            messagebox.showerror("Invalid Input", "Please enter '1' or '2'.")

    def run_pass1(self):
        self.symbol_table.clear()
        self.address_counter = 0
        code_lines = self.code_text.get("1.0", "end").strip().splitlines()

        self.symbol_table_text.config(state="normal")
        self.symbol_table_text.delete("1.0", "end")

        # Generate the symbol table by parsing labels
        for line in code_lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue  # Ignore empty lines and comments
            
            label, opcode, operand = self.parse_line(line)
            
            if label:
                if label in self.symbol_table:
                    messagebox.showerror("Error", f"Duplicate label '{label}' found.")
                    return
                self.symbol_table[label] = self.address_counter
            
            # Update address counter for each instruction
            self.address_counter += 1

        self.display_symbol_table()

    def run_pass2(self):
        self.machine_code.clear()
        code_lines = self.code_text.get("1.0", "end").strip().splitlines()

        self.machine_code_text.config(state="normal")
        self.machine_code_text.delete("1.0", "end")

        for line in code_lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue  # Ignore empty lines and comments
            
            label, opcode, operand = self.parse_line(line)

            if opcode and operand:
                # Use symbol table for label resolution
                if operand in self.symbol_table:
                    address = self.symbol_table[operand]
                    machine_instruction = f"{opcode} {address}"
                else:
                    machine_instruction = f"{opcode} {operand}"
                self.machine_code.append(machine_instruction)

        # Display machine code in output
        self.display_machine_code()

    def parse_line(self, line):
        """Parse a line into label, opcode, and operand."""
        label, opcode, operand = None, None, None
        parts = line.split()
        
        if len(parts) == 3:
            label, opcode, operand = parts
        elif len(parts) == 2:
            if parts[0][-1] == ":":
                label, opcode = parts
                operand = ""
            else:
                opcode, operand = parts
        elif len(parts) == 1:
            opcode = parts[0]

        # Remove ":" from labels if present
        if label and label.endswith(":"):
            label = label[:-1]

        return label, opcode, operand

    def display_symbol_table(self):
        self.symbol_table_text.config(state="normal")
        self.symbol_table_text.delete("1.0", "end")
        
        for symbol, address in self.symbol_table.items():
            self.symbol_table_text.insert("end", f"{symbol} : {address}\n")
        
        self.symbol_table_text.config(state="disabled")

    def display_machine_code(self):
        self.machine_code_text.config(state="normal")
        self.machine_code_text.delete("1.0", "end")
        
        for instruction in self.machine_code:
            self.machine_code_text.insert("end", f"{instruction}\n")
        
        self.machine_code_text.config(state="disabled")

    def clear_all(self):
        self.code_text.delete("1.0", "end")
        self.symbol_table_text.config(state="normal")
        self.symbol_table_text.delete("1.0", "end")
        self.symbol_table_text.config(state="disabled")
        self.machine_code_text.config(state="normal")
        self.machine_code_text.delete("1.0", "end")
        self.machine_code_text.config(state="disabled")
        self.symbol_table.clear()
        self.machine_code.clear()
        self.address_counter = 0

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = MachineCodeConverter(root)
    root.mainloop()
