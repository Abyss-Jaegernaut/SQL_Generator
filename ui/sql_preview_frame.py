from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class SQLPreviewFrame(ttk.LabelFrame):
    """Shows generated SQL scripts with action toggles."""

    def __init__(self, master, controller, actions_vars: dict[str, tk.BooleanVar], on_actions_changed, on_save_history=None) -> None:
        super().__init__(master, text="Aperçu SQL")
        self.controller = controller
        self.actions_vars = actions_vars
        self.on_actions_changed = on_actions_changed
        self.on_save_history = on_save_history
        
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Button(toolbar, text="📋 Copier", command=self.copy_all).pack(side="left")
        ttk.Button(toolbar, text="💾 Exporter .sql", command=self.export_sql).pack(side="left", padx=(6, 0))
        ttk.Button(toolbar, text="📜 Sauvegarder dans l'historique", command=self._save_to_history).pack(side="left", padx=(6, 0))

        # Actions area (Single line as requested)
        actions_frame = ttk.Frame(self)
        actions_frame.pack(fill="x", padx=4, pady=(2, 2))
        
        ttk.Label(actions_frame, text="✅ Sections / Procédures :", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))
        
        for name, var in self.actions_vars.items():
            # Standard tk.Checkbutton as requested
            chk = tk.Checkbutton(
                actions_frame, 
                text=name, 
                variable=var, 
                command=self.on_actions_changed,
                font=("Segoe UI", 9)
            )
            chk.pack(side="left", padx=(2, 2))
            
        ttk.Button(actions_frame, text="🔁 Tout sélectionner", command=self._select_all).pack(side="left", padx=(6, 0))

        self.text = tk.Text(self, height=24, wrap="none", font=("Consolas", 10))
        self._configure_syntax_highlighting()
        self.text.configure(state="disabled")
        self.text.pack(fill="both", expand=True, padx=4, pady=4)
        self._last_sql = ""

    def _configure_syntax_highlighting(self) -> None:
        """Configure text widget tags for SQL syntax highlighting using the current theme."""
        from ui.theme_manager import ThemeManager
        theme = ThemeManager().current_theme
        syntax = theme.syntax_colors

        # Keywords
        self.text.tag_configure("keyword", foreground=syntax.get("keyword", "#c678dd"), font=("Consolas", 10, "bold"))
        # Identifiers
        self.text.tag_configure("identifier", foreground=syntax.get("identifier", "#e5c07b"))
        # Types and general numbers
        self.text.tag_configure("number", foreground=syntax.get("type", "#61afef"))
        # Strings
        self.text.tag_configure("string", foreground=syntax.get("string", "#98c379"))
        # Comments
        self.text.tag_configure("comment", foreground=syntax.get("comment", "#5c6370"))
        # Extra (Functions etc)
        self.text.tag_configure("function", foreground=syntax.get("type", "#61afef"))

    def _select_all(self) -> None:
        # If all are checked, uncheck all. Otherwise check all.
        all_checked = all(v.get() for v in self.actions_vars.values())
        target = not all_checked
        for v in self.actions_vars.values():
            v.set(target)
        self.on_actions_changed()

    def show_scripts(self, scripts: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self._last_sql = scripts or ""
        if not self._last_sql.strip():
            self.text.insert(tk.END, "Aucune table définie pour le moment.\n")
        else:
            self.text.insert(tk.END, self._last_sql)
            self._apply_syntax_highlighting()
        self.text.configure(state="disabled")

    def _apply_syntax_highlighting(self) -> None:
        """Apply syntax highlighting to the SQL text."""
        content = self.text.get("1.0", tk.END)
        
        # SQL Keywords
        keywords = r'\b(SELECT|FROM|WHERE|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|DATABASE|IF|NOT|EXISTS|USE|GO|BEGIN|END|PRIMARY|KEY|IDENTITY|AUTO_INCREMENT|SERIAL|BIGSERIAL|NULL|DEFAULT|CONSTRAINT|FOREIGN|REFERENCES|INDEX|UNIQUE|CHECK|AS|ON|AND|OR|IN|LIKE|BETWEEN|ORDER|BY|GROUP|HAVING|JOIN|LEFT|RIGHT|INNER|OUTER|UNION|CASE|WHEN|THEN|ELSE|DROP|ALTER|ADD|MODIFY|COLUMN|VARCHAR|INT|BIGINT|SMALLINT|DECIMAL|FLOAT|DATETIME|TIMESTAMP|DATE|TEXT|BIT|BOOLEAN|CHAR|NVARCHAR|PROCEDURE|FUNCTION|RETURN|DECLARE|EXEC|EXECUTE)\b'
        for match in re.finditer(keywords, content, re.IGNORECASE):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("keyword", start_idx, end_idx)
        
        # Comments (-- style)
        for match in re.finditer(r'--[^\n]*', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("comment", start_idx, end_idx)
        
        # Strings (single quotes)
        for match in re.finditer(r"'[^']*'", content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("string", start_idx, end_idx)
        
        # Numbers
        for match in re.finditer(r'\b\d+\b', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("number", start_idx, end_idx)
        
        # Square brackets, backticks, or quotes for identifiers
        for match in re.finditer(r'(\[[^\]]+\]|`[^`]+`|"[^"]+")', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.text.tag_add("identifier", start_idx, end_idx)

    def _save_to_history(self) -> None:
        if not self.controller.is_activated():
            messagebox.showinfo("Premium Requis", "La sauvegarde de s'historique est une fonctionnalité Premium.")
            return

        if not self._last_sql.strip():
            return
        if self.on_save_history:
            self.on_save_history(self._last_sql)
            messagebox.showinfo("Historique", "Script sauvegardé dans l'historique.")

    def copy_all(self) -> None:
        if not self._last_sql.strip():
            return
        self.clipboard_clear()
        self.clipboard_append(self._last_sql)
        messagebox.showinfo("Copié", "SQL copié dans le presse-papiers.")

    def export_sql(self) -> None:
        if not self.controller.is_activated():
            messagebox.showinfo("Premium Requis", "L'exportation en fichier .sql est réservée aux utilisateurs Premium.\n\nVous pouvez copier le code dans le presse-papier gratuitement.")
            return

        if not self._last_sql.strip():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("All files", "*.*")],
            title="Exporter le script SQL",
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._last_sql)
        messagebox.showinfo("Export", f"Fichier exporté :\n{path}")
