from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ActivationWindow(tk.Toplevel):
    """Modal window asking for activation code."""

    def __init__(self, master: tk.Misc, expected_code: str, on_success) -> None:
        super().__init__(master)
        self.expected_code = expected_code
        self.on_success = on_success

        self.title("Activation requise")
        self.resizable(False, False)

        self.code_var = tk.StringVar()
        self._build_ui()

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Entrez le code d'activation :").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.code_var, show="*")
        entry.grid(row=1, column=0, sticky="ew", pady=6)
        entry.focus_set()

        self.message = ttk.Label(frame, text="", foreground="red")
        self.message.grid(row=2, column=0, sticky="w")

        btn = ttk.Button(frame, text="Activer", command=self._on_validate)
        btn.grid(row=3, column=0, sticky="e", pady=(8, 0))

        frame.columnconfigure(0, weight=1)

    def _on_validate(self) -> None:
        try:
            if self.code_var.get().strip() == self.expected_code:
                self.destroy()
                if self.on_success:
                    self.on_success()
            else:
                self.message.config(text="Code invalide.")
        except Exception as e:
            self.message.config(text=f"Erreur: {str(e)}")

    def _on_close(self) -> None:
        # Block closing to enforce activation; alternatively, exit the app.
        self.message.config(text="Activation requise pour continuer.")