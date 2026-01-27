import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

def generate_key(machine_code, secret_phrase="SQL_GENERATOR_SECRET"):
    """Generate an activation key based on the machine code."""
    # Important: Remove dashes and prefix to be robust against formatting
    clean_code = machine_code.replace('MACH-', '').replace('-', '').strip().upper()
    if not clean_code:
        return ""
    combined = clean_code + secret_phrase
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    
    # Format: XXXX-XXXX-XXXX-XXXX-XXXX
    formatted_key = "{0}-{1}-{2}-{3}-{4}".format(
        hashed[:4].upper(), 
        hashed[4:8].upper(), 
        hashed[8:12].upper(), 
        hashed[12:16].upper(), 
        hashed[16:20].upper()
    )
    return formatted_key

class KeyGenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Generator - Key Generator")
        self.root.geometry("500x320")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        # Try to use a better theme
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
            
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=10)
        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(
            main_frame, 
            text="Générateur de Clés d'Activation", 
            font=("Segoe UI", 16, "bold"),
            foreground="#007acc"
        ).pack(pady=(0, 20))

        # Input Section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=5)

        ttk.Label(input_frame, text="Code Machine du Client :", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.machine_code_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, textvariable=self.machine_code_var, font=("Consolas", 12))
        self.entry.pack(fill="x", pady=5)
        self.entry.focus_set()
        
        ttk.Label(input_frame, text="Ex: MACH-XXXX-XXXX-XXXX", font=("Segoe UI", 8), foreground="gray").pack(anchor="w")

        # Output Section
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill="x", pady=10)

        ttk.Label(output_frame, text="Clé Générée :", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(output_frame, textvariable=self.key_var, font=("Consolas", 12, "bold"), state="readonly", justify="center")
        self.key_entry.pack(fill="x", pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)

        # Use a more visible button style
        self.gen_btn = ttk.Button(btn_frame, text="GÉNÉRER LA CLÉ", command=self._on_generate, width=25)
        self.gen_btn.pack(side="left", padx=10)
        
        self.copy_btn = ttk.Button(btn_frame, text="COPIER", command=self._on_copy, width=15)
        self.copy_btn.pack(side="left", padx=10)

    def _on_generate(self):
        m_code = self.machine_code_var.get().strip()
        if not m_code.startswith("MACH-"):
            messagebox.showerror("Erreur", "Le code machine est invalide.\nIl doit commencer par 'MACH-'")
            return
        
        key = generate_key(m_code)
        self.key_var.set(key)

    def _on_copy(self):
        key = self.key_var.get()
        if key:
            self.root.clipboard_clear()
            self.root.clipboard_append(key)
            self.root.update() # Ensure clipboard synchronization on Windows
            messagebox.showinfo("Succès", "Clé copiée dans le presse-papier !")
        else:
            messagebox.showwarning("Attention", "Veuillez d'abord générer une clé.")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyGenApp(root)
    root.mainloop()
