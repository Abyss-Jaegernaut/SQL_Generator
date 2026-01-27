from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LicensePage(ttk.Frame):
    """A Frame-based UI for software license activation."""

    def __init__(self, master, controller, on_success=None) -> None:
        super().__init__(master)
        self.controller = controller
        self.on_success = on_success
        self.success = False
        self._current_machine_code = None
        self._build_ui()

    def _build_ui(self) -> None:
        # Padding frame for centering
        container = ttk.Frame(self, padding=20)
        container.pack(expand=True)

        ttk.Label(
            container, 
            text="SQL Generator CRUD - Premium", 
            font=("Segoe UI", 14, "bold"),
            foreground="#007acc"
        ).pack(pady=(0, 20))

        # Machine code section
        machine_frame = ttk.LabelFrame(container, text="Votre code machine", padding=10)
        machine_frame.pack(fill="x", pady=(0, 20))
        
        self.machine_code_label = ttk.Label(
            machine_frame, 
            text="Récupération du code machine...",
            font=("Consolas", 11, "bold"),
            foreground="blue"
        )
        self.machine_code_label.pack(pady=5)
        
        machine_desc = ttk.Label(
            machine_frame,
            text="Ce code est unique à votre ordinateur. Envoyez-le au développeur pour obtenir une clé d'activation.",
            wraplength=400,
            font=("Segoe UI", 9)
        )
        machine_desc.pack(pady=(5, 0))
        
        # Button to copy machine code
        self.copy_btn = ttk.Button(
            machine_frame, 
            text="Copier le code machine", 
            command=self._copy_machine_code,
            state="disabled"
        )
        self.copy_btn.pack(pady=(10, 0))
        
        # Activation key section
        activation_frame = ttk.LabelFrame(container, text="Clé d'activation", padding=10)
        activation_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            activation_frame, 
            text="Entrez votre clé d'activation :", 
            wraplength=400
        ).pack(pady=(0, 5))

        self.key_var = tk.StringVar()
        self.entry = ttk.Entry(activation_frame, textvariable=self.key_var, font=("Consolas", 11), justify="center")
        self.entry.pack(fill="x", pady=5)
        self.entry.focus_set()

        hint_label = ttk.Label(
            activation_frame, 
            text="Format: XXXX-XXXX-XXXX-XXXX-XXXX",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        hint_label.pack()

        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Activer la Licence", command=self._activate, width=20).pack(side="left", padx=5)
        
        # Add exit button
        ttk.Button(btn_frame, text="Quitter", command=lambda: self.master.destroy(), width=10).pack(side="left", padx=5)

        # Load machine code
        self.after(200, self._load_machine_code)

    def _load_machine_code(self):
        try:
            self._current_machine_code = self.controller.get_machine_code()
            self.machine_code_label.config(text=self._current_machine_code)
            self.copy_btn.config(state="normal")
        except Exception as e:
            self.machine_code_label.config(text="Erreur de détection matérielle")

    def _copy_machine_code(self):
        try:
            if not self._current_machine_code:
                return
            self.master.clipboard_clear()
            self.master.clipboard_append(self._current_machine_code)
            self.master.update() # Ensure clipboard is updated on Windows
            messagebox.showinfo("Copié", "Code machine copié !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de copier: {e}")

    def _activate(self) -> None:
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("Attention", "Veuillez entrer une clé d'activation.")
            return

        try:
            if self.controller.activate_license(key):
                messagebox.showinfo("Succès", "Licence activée avec succès !")
                self.success = True
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror("Erreur", "Clé de licence invalide.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'activation: {e}")
