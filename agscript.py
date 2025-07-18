import tkinter as tk
from tkinter import messagebox
import re

class AGScriptInterpreter:
    """
    An interpreter for the AG Script language.
    It handles variable assignments, function definitions/calls,
    conditional logic, and basic GUI elements with Tkinter.
    """
    def __init__(self):
        self.variables = {}
        self.functions = {
            'print': {'params': ['val'], 'body': self.native_print, 'is_native': True},
            'msgbox': {'params': ['msg'], 'body': self.native_msgbox, 'is_native': True},
            'int': {'params': ['val'], 'body': int, 'is_native': True},
        }
        self.root = None
        self.buttons = {}

    # ----------------------------------------------------------------------
    # Native (Built-in) Functions
    # ----------------------------------------------------------------------

    def native_print(self, *args):
        """The native 'print' function."""
        print(*args)

    def native_msgbox(self, msg):
        """The native 'msgbox' function."""
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()
        messagebox.showinfo("AG Script Message", str(msg))

    # ----------------------------------------------------------------------
    # Core Evaluation Logic
    # ----------------------------------------------------------------------

    def get_eval_scope(self, local_vars=None):
        """Constructs the scope for the eval() function."""
        scope = {name: func['body'] for name, func in self.functions.items() if func.get('is_native')}
        
        for name, func_def in self.functions.items():
            if not func_def.get('is_native'):
                scope[name] = self.create_user_func_lambda(name)
        
        scope.update(self.variables)
        if local_vars:
            scope.update(local_vars)
            
        return scope

    def create_user_func_lambda(self, name):
        """Creates a Python lambda to wrap a user-defined function call."""
        def user_func_wrapper(*args):
            return self.call_user_function(name, list(args))
        return user_func_wrapper

    def eval_expr(self, expr, local_vars=None):
        """Evaluates a single AG Script expression."""
        global_scope = self.get_eval_scope()
        return eval(expr, global_scope, local_vars if local_vars else {})

    def call_user_function(self, name, args):
        """Executes a user-defined function."""
        func_def = self.functions[name]
        params = func_def['params']

        if len(args) != len(params):
            raise TypeError(f"{name}() expects {len(params)} arguments but got {len(args)}")

        local_scope = dict(zip(params, args))
        return self.eval_expr(func_def['body'], local_scope)

    # ----------------------------------------------------------------------
    # Line-by-Line Execution
    # ----------------------------------------------------------------------

    def run_line(self, line):
        """Parses and executes a single line of AG Script."""
        line = line.strip()
        if not line or line.startswith("#"):
            return

        # --- Function Definition: func name(params) [return] body ---
        if line.startswith("func "):
            # FIX: Made the 'return' keyword optional in the regex.
            match = re.match(r'func\s+([a-zA-Z_]\w*)\s*\(([^)]*)\)\s*(?:return\s+)?(.*)', line)
            if not match:
                raise SyntaxError(f"Invalid function syntax: {line}")
            name, params_str, body = match.groups()
            params = [p.strip() for p in params_str.split(',') if p.strip()]
            self.functions[name] = {'params': params, 'body': body.strip(), 'is_native': False}
            return

        # --- Button Definition: button name "Text" action ---
        if line.startswith("button "):
            match = re.match(r'button\s+([a-zA-Z_]\w*)\s+"([^"]*)"\s+(.*)', line)
            if not match:
                raise SyntaxError("Invalid button syntax. Expected: button name \"Text\" action")
            btn_var_name, btn_text, action = match.groups()

            if self.root is None:
                self.root = tk.Tk()
                self.root.title("AG Script")
                self.root.geometry("250x300")
            
            def on_click(action=action):
                try:
                    result = self.eval_expr(action)
                    if result is not None:
                        self.native_msgbox(f"Result: {result}")
                except Exception as e:
                    messagebox.showerror("Runtime Error", str(e))
            
            btn = tk.Button(self.root, text=btn_text, command=on_click, width=20)
            btn.pack(pady=5, padx=10)
            self.buttons[btn_var_name] = btn
            return

        # --- If Statement: if condition action ---
        if line.startswith("if "):
            rest = line[3:].strip()
            match = re.match(r'(.+?)\s+(print|msgbox|[a-zA-Z_]\w*.*)', rest)
            if not match:
                raise SyntaxError(f"Invalid if syntax: {line}")
            
            condition, action = match.groups()[:2]
            action = rest[rest.find(action):]
            
            if self.eval_expr(condition):
                self.eval_expr(action)
            return

        # --- Variable Assignment: var = expression ---
        match = re.match(r'^([a-zA-Z_]\w*)\s*=\s*(.*)', line)
        if match:
            var_name, expr = match.groups()
            self.variables[var_name] = self.eval_expr(expr)
            return

        # --- Expression Statement (e.g., a function call) ---
        self.eval_expr(line)

    def run(self, code):
        """Runs a multi-line string of AG Script code."""
        for i, line in enumerate(code.splitlines()):
            try:
                self.run_line(line)
            except Exception as e:
                error_message = f"Error on line {i+1}: {line.strip()}\n\n{type(e).__name__}: {e}"
                print(error_message)
                if self.root:
                    messagebox.showerror("Script Error", error_message)
                return "Execution failed."

        if self.root:
            print("GUI is running. Close the window to exit.")
            self.root.mainloop()

        return "Execution complete."


# This is how you would use the interpreter
if __name__ == '__main__':
    # Your AG Script code, now working with the fix
    ag_script_code = """
# Variable assignment
x = 10
y = 20

# Print variables and expressions
print("x is", x)
print("y is", y)
print("x + y is", x + y)
print("Hello, AG Script!")

# Message box showing sum
msgbox(x + y)

# Define a function with two parameters (with 'return')
func add(a, b) return int(a) + int(b)

# Call function directly and print result
print("Result of add(x,y) is", add(x, y))

# Define a function without parameters
func greet() return "Hello from a function!"

print(greet())

# Inline if statement that prints only if condition true
if x > 5 print("x is greater than 5")
if y < 5 print("This won't print")

# --- GUI Buttons ---
# Note the corrected syntax: button name "text" action

# Button without args that calls a function
func say_hello() return "Button pressed: Hello!"
button btn1 "Say Hello" say_hello()

# Button with args that calls a function
button btn2 "Add 7 + 8" add(7, 8)

# Button that shows message box when clicked (without 'return')
func show_msg() msgbox("Button clicked!")
button btn3 "Show MsgBox" show_msg()
"""

    # Create an interpreter instance and run the code
    interpreter = AGScriptInterpreter()
    interpreter.run(ag_script_code)