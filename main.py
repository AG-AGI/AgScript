import customtkinter as ctk
import tkinter as tk
import agscript
import io
from contextlib import redirect_stdout
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

KEYWORDS = [
    "print", "def", "class", "if", "elif", "else", "for", "while", "return", "import", "from",
    "as", "with", "try", "except", "finally", "in", "is", "and", "or", "not", "lambda", "pass",
    "break", "continue", "True", "False", "None"
]

OPERATORS = r"[\=\+\-\*/%<>!:]"

class AgIDE(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AgIDE")
        self.geometry("800x600")
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=10, pady=10)
        self.run_button = ctk.CTkButton(self.button_frame, text="Run Code", command=self.run_code, corner_radius=55)
        self.run_button.pack(side="left", padx=(0, 5))
        self.toggle_terminal_button = ctk.CTkButton(
            self.button_frame, text="Hide Terminal", command=self.toggle_terminal, corner_radius=55
        )
        self.toggle_terminal_button.pack(side="left")
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(padx=10, pady=(0, 5), fill="both", expand=True)
        self.editor = tk.Text(
            self.editor_frame,
            font=("Consolas", 14),
            undo=True,
            highlightthickness=0,  
            bd=5,
            insertbackground="white",
            bg="#1e1e1e",
            fg="white",
            wrap="none"
        )
        self.editor.pack(fill="both", expand=True)
        self.setup_tags()
        self.editor.bind("<KeyRelease>", self.on_text_change)
        self.terminal_frame = ctk.CTkFrame(self)
        self.terminal_frame.pack(fill="both", padx=10, pady=(0, 10), expand=False)
        self.console = ctk.CTkTextbox(
            self.terminal_frame,
            height=180,
            font=("Consolas", 12),
            fg_color="#222222",
            text_color="#00ff00",
            state="disabled"
        )
        self.console.pack(fill="both", expand=True)
        self.terminal_visible = True

    def setup_tags(self):
        self.editor.tag_configure("paren", foreground="#1E90FF")
        self.editor.tag_configure("string", foreground="#32CD32")
        self.editor.tag_configure("keyword", foreground="#FFA500")
        self.editor.tag_configure("comment", foreground="#32CD32")
        self.editor.tag_configure("operator", foreground="#1E90FF")

    def toggle_terminal(self):
        if self.terminal_visible:
            self.terminal_frame.pack_forget()
            self.toggle_terminal_button.configure(text="Show Terminal")
            self.editor_frame.pack_configure(expand=True)
            self.terminal_visible = False
        else:
            self.terminal_frame.pack(fill="both", padx=10, pady=(0, 10), expand=False)
            self.toggle_terminal_button.configure(text="Hide Terminal")
            self.editor_frame.pack_configure(expand=True)
            self.terminal_visible = True

    def run_code(self):
        code = self.editor.get("1.0", "end-1c")
        self.execute_code(code)

    def execute_code(self, code):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        try:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                result = agscript.run(code)
            output = buffer.getvalue()
            self.console.insert("end", output)
            if result is not None:
                self.console.insert("end", f"\nReturned: {result}")
        except Exception as e:
            self.console.insert("end", f"Error: {e}")
        finally:
            self.console.configure(state="disabled")

    def on_text_change(self, event=None):
        code = self.editor.get("1.0", "end-1c")
        for tag in ["paren", "string", "keyword", "comment", "operator"]:
            self.editor.tag_remove(tag, "1.0", "end")
        for match in re.finditer(r"#.*", code):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("comment", start, end)
        for match in re.finditer(r"(\".*?\"|\'.*?\')", code, re.DOTALL):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("string", start, end)
        for match in re.finditer(r"[\(\)]", code):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("paren", start, end)
        for match in re.finditer(OPERATORS, code):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.editor.tag_add("operator", start, end)
        for kw in KEYWORDS:
            for match in re.finditer(rf"\b{kw}\b", code):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.editor.tag_add("keyword", start, end)

if __name__ == "__main__":
    app = AgIDE()
    app.mainloop()
