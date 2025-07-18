import tkinter as tk
from tkinter import messagebox

def run(code):
    variables = {}
    lines = code.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        
        # Variable assignment
        if '=' in line and not line.startswith("print") and not line.startswith("msgbox"):
            var_name, expr = line.split('=', 1)
            var_name = var_name.strip()
            expr = expr.strip()
            # Try to evaluate the expression safely
            try:
                # Evaluate with current variables available
                value = eval(expr, {}, variables)
            except Exception:
                # If evaluation fails, store as string literally
                value = expr.strip('"').strip("'")
            variables[var_name] = value
            continue
        
        # print(...)
        if line.startswith("print(") and line.endswith(")"):
            content = line[6:-1].strip()
            # If content is a variable
            if content in variables:
                print(variables[content])
            else:
                # Try evaluating the expression in print
                try:
                    value = eval(content, {}, variables)
                    print(value)
                except Exception:
                    # Otherwise, print as literal string without quotes
                    print(content.strip('"').strip("'"))
            continue
        
        # msgbox(...)
        if line.startswith("msgbox(") and line.endswith(")"):
            content = line[7:-1].strip()
            # Try to evaluate content as variable or expression
            if content in variables:
                messagebox.showinfo("Message", str(variables[content]))
            else:
                try:
                    value = eval(content, {}, variables)
                    messagebox.showinfo("Message", str(value))
                except Exception:
                    messagebox.showinfo("Message", content.strip('"').strip("'"))
            continue

    return "Execution complete"
