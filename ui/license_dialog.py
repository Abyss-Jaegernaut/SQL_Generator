from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LicenseDialog(tk.Toplevel):
    """Dialog to enter and validate the software license."""

    def __init__(self, master, controller) -> None:
        super().__init__(master)
        self.controller = controller
        self.title("Activation de Licence")
        self.geometry("450x250")
        self.resizable(False, False)
        
        # Make modal
        self.transient(master)
        self.grab_set()

        # Center
        self.withdraw()
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (450/2)
        y = (hs/2) - (250/2)
        self.geometry('+%d+%d' % (x, y))
        self.deiconify()
        self.attributes("-topmost", True)
        self.focus_force()
        self.lift()

        self.success = False
        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, 
            text="SQL Generator CRUD - Premium", 
            font=("Segoe UI", 12, "bold"),
            foreground="#007acc"
        ).pack(pady=(0, 10))

        ttk.Label(
            frame, 
            text="Veuillez entrer votre clé de licence pour activer le produit :",
            wraplength=400
        ).pack(pady=(0, 15))

        self.key_var = tk.StringVar()
        self.entry = ttk.Entry(frame, textvariable=self.key_var, font=("Consolas", 12), justify="center")
        self.entry.pack(fill="x", pady=5)
        self.entry.focus_set()

        hint_label = ttk.Label(
            frame, 
            text="Format: XXXX-XXXX-XXXX-XXXX-XXXX",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        hint_label.pack()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Activer", command=self._activate, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Plus tard", command=self.destroy, width=15).pack(side="left", padx=5)

    def _activate(self) -> None:
        try:
            key = self.key_var.get().strip()
            if self.controller.activate_license(key):
                messagebox.showinfo("Succès", "Licence activée avec succès ! Merci de votre confiance.")
                self.success = True
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Clé de licence invalide. Veuillez vérifier votre saisie.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème lors de l'activation: {str(e)}")