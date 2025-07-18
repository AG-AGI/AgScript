import tkinter as tk
from tkinter import messagebox

class AGScriptInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.root = None
        self.buttons = {}

    def eval_expr(self, expr, local_vars=None):
        local_vars = local_vars or self.variables
        try:
            return eval(expr, {}, local_vars)
        except Exception:
            return expr.strip('"').strip("'")

    def call_function(self, name, args):
        if name not in self.functions:
            raise Exception(f"Function '{name}' is not defined")
        func = self.functions[name]
        if len(args) != len(func['params']):
            raise Exception(f"Function '{name}' expects {len(func['params'])} arguments but got {len(args)}")
        local_vars = self.variables.copy()
        for param, arg in zip(func['params'], args):
            local_vars[param] = self.eval_expr(arg)
        try:
            return eval(func['body'], {}, local_vars)
        except Exception as e:
            raise Exception(f"Error in function '{name}': {e}")

    def run_line(self, line):
        line = line.strip()
        if not line or line.startswith("#"):
            return

        if line.startswith("func "):
            _, rest = line.split("func ", 1)
            signature, ret_expr = rest.split("return", 1)
            signature = signature.strip()
            ret_expr = ret_expr.strip()
            name, params = signature.split("(", 1)
            name = name.strip()
            params = params.rstrip(")").strip()
            param_list = [p.strip() for p in params.split(",")] if params else []
            self.functions[name] = {'params': param_list, 'body': ret_expr}
            return

        if line.startswith("if "):
            _, rest = line.split("if ", 1)
            cond_end = rest.find(" ")
            if cond_end == -1:
                raise Exception("Invalid if syntax")
            cond = rest[:cond_end].strip()
            cmd = rest[cond_end+1:].strip()
            if self.eval_expr(cond):
                self.run_line(cmd)
            return

        if '=' in line and not line.startswith(("print", "msgbox", "button")):
            var_name, expr = line.split('=', 1)
            var_name = var_name.strip()
            expr = expr.strip()
            value = self.eval_expr(expr)
            self.variables[var_name] = value
            return

        if line.startswith("print(") and line.endswith(")"):
            content = line[6:-1].strip()
            val = self.eval_expr(content)
            print(val)
            return

        if line.startswith("msgbox(") and line.endswith(")"):
            content = line[7:-1].strip()
            val = self.eval_expr(content)
            messagebox.showinfo("Message", str(val))
            return

        if line.startswith("button "):
            if self.root is None:
                self.root = tk.Tk()
                self.root.withdraw()

            parts = line.split(" ", 2)
            if len(parts) < 3:
                raise Exception("Invalid button syntax")

            btn_name = parts[1].strip()
            rest = parts[2].strip()

            # Extract button text in quotes and function call after
            if rest.startswith('('):
                # Find closing quote
                end_quote = rest.find('")')
                if end_quote == -1:
                    raise Exception("Invalid button syntax: missing closing quote")
                btn_text = rest[1:end_quote]

                func_call = rest[end_quote+2:].strip()
                # Parse function name and optional args
                if '(' in func_call and func_call.endswith(')'):
                    fname, fargs_str = func_call.split('(', 1)
                    fname = fname.strip()
                    fargs_str = fargs_str[:-1]  # remove trailing )
                    fargs = [a.strip() for a in fargs_str.split(',')] if fargs_str else []
                else:
                    fname = func_call
                    fargs = []

                def on_click(fname=fname, fargs=fargs):
                    try:
                        ret = self.call_function(fname, fargs)
                        if ret is not None:
                            print(ret)
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

                if btn_name in self.buttons:
                    btn = self.buttons[btn_name]
                    btn.config(text=btn_text, command=on_click)
                else:
                    btn = tk.Button(self.root, text=btn_text, command=on_click)
                    btn.pack()
                    self.buttons[btn_name] = btn

                self.root.deiconify()
            else:
                raise Exception("Invalid button syntax")
            return

        if '(' in line and line.endswith(')'):
            name, args_str = line.split('(', 1)
            name = name.strip()
            args_str = args_str[:-1]
            args = [a.strip() for a in args_str.split(',')] if args_str else []
            ret = self.call_function(name, args)
            if ret is not None:
                print(ret)
            return

        raise Exception(f"Unknown command: {line}")

    def run(self, code):
        for line in code.splitlines():
            try:
                self.run_line(line)
            except Exception as e:
                print(f"Error: {e}")

        if self.root:
            self.root.mainloop()

        return "Execution complete"

_interpreter_instance = AGScriptInterpreter()

def run(code):
    return _interpreter_instance.run(code)
