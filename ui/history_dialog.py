from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class HistoryDialog(tk.Toplevel):
    """Dialog to view last 10 generated SQL scripts."""

    def __init__(self, master, history: list[dict]) -> None:
        super().__init__(master)
        self.title("Historique des Générations")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Center the window
        self.withdraw()
        self.update_idletasks()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (900/2)
        y = (hs/2) - (600/2)
        self.geometry('+%d+%d' % (x, y))
        self.deiconify()

        self.history = history
        self._build_ui()
        from ui.theme_manager import ThemeManager
        ThemeManager().apply_theme(ThemeManager().current_theme.name, self)

    def _build_ui(self) -> None:
        # Split screen: List on left, preview on right
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Left: List of history entries
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Dernières générations (max 10)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        
        self.tree = ttk.Treeview(left_frame, columns=("id", "project", "date"), show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("project", text="Projet")
        self.tree.heading("date", text="Date")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("project", width=150, anchor="w")
        self.tree.column("date", width=150, anchor="w")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Right: SQL Preview
        right_frame = ttk.LabelFrame(paned, text="Contenu SQL")
        paned.add(right_frame, weight=3)

        self.text = tk.Text(right_frame, wrap="none", font=("Consolas", 10))
        vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.text.yview)
        hsb = ttk.Scrollbar(right_frame, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.text.pack(side="top", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
        self.text.configure(state="disabled")

        # Load data
        for entry in self.history:
            self.tree.insert("", "end", values=(entry["id"], entry["project_name"], entry["created_at"]), tags=(str(entry["id"]),))

        if self.history:
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)

    def _on_select(self, event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        entry_id = item["values"][0]
        
        # Find entry in history
        entry = next((e for e in self.history if e["id"] == entry_id), None)
        if entry:
            self.text.configure(state="normal")
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, entry["sql_content"])
            self.text.configure(state="disabled")
