from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ProjectManagerDialog(tk.Toplevel):
    """Placeholder dialog for managing saved projects."""

    def __init__(self, master) -> None:
        super().__init__(master)
        self.title("Projets sauvegardés")
        ttk.Label(self, text="Gestion des projets (à implémenter)").pack(padx=8, pady=8)
        ttk.Button(self, text="Fermer", command=self.destroy).pack(padx=8, pady=8)
