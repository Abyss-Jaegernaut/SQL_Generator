from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from controllers.app_controller import AppController
from core import models


class SampleDataFrame(ttk.LabelFrame):
    """Manually enter data for the active table."""

    def __init__(self, master, controller: AppController, on_updated=None) -> None:
        super().__init__(master, text="Saisie de valeurs (INSERT)")
        self.controller = controller
        self.on_updated = on_updated
        self.active_table: models.TableModel | None = None
        self.entry_vars: dict[str, tk.StringVar] = {}
        self._editing_idx: int | None = None
        
        self._build_ui()

    def _build_ui(self) -> None:
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        
        # Main area: Input form and data grid
        self.input_frame = ttk.LabelFrame(self, text="Saisie / Modification")
        self.input_frame.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        
        # We will dynamically populate input_frame based on columns.
        self.inputs_inner = ttk.Frame(self.input_frame)
        self.inputs_inner.pack(fill="x", padx=4, pady=4)
        
        btn_frame = ttk.Frame(self.input_frame)
        btn_frame.pack(fill="x", padx=4, pady=(0, 4))
        self.submit_btn = ttk.Button(btn_frame, text="✅ Ajouter une ligne", command=self._on_submit)
        self.submit_btn.pack(side="left")
        
        ttk.Button(btn_frame, text="❌ Annuler", command=self._cancel_edit).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="🧹 Effacer tout", command=self._clear_all_rows).pack(side="right", padx=(6, 0))

        # Treeview for data
        self.tree_frame = ttk.LabelFrame(self, text="Lignes saisies (cliquez pour sélectionner)")
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        
        tree_btns = ttk.Frame(self.tree_frame)
        tree_btns.pack(fill="x", padx=4, pady=2)
        ttk.Button(tree_btns, text="📝 Modifier sélection", command=self._load_selected_for_edit).pack(side="left")
        ttk.Button(tree_btns, text="🗑️ Supprimer sélection", command=self._delete_selected_row).pack(side="left", padx=4)

        self.tree = ttk.Treeview(self.tree_frame, show="headings", height=8, selectmode="browse")
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def set_active_table(self, table: models.TableModel | None) -> None:
        self.active_table = table
        self._editing_idx = None
        self._refresh_inputs()
        self._refresh_tree()

    def _refresh_inputs(self) -> None:
        for widget in self.inputs_inner.winfo_children():
            widget.destroy()
        self.entry_vars.clear()

        if not self.active_table:
            ttk.Label(self.inputs_inner, text="Aucune table sélectionnée").pack()
            return

        # Simple grid of inputs
        r = 0
        c = 0
        for col in self.active_table.columns:
            if col.is_auto_increment:
                continue
                
            frame = ttk.Frame(self.inputs_inner)
            frame.grid(row=r, column=c, padx=4, pady=2, sticky="w")
            
            hint = ""
            if "DATE" == col.sql_type.upper():
                hint = " (YYYY-MM-DD)"
            elif "DATETIME" in col.sql_type.upper():
                hint = " (YYYY-MM-DD HH:MM:SS)"
            
            lbl = ttk.Label(frame, text=col.name + hint, font=("Segoe UI", 8))
            lbl.pack(anchor="w")
            
            var = tk.StringVar()
            self.entry_vars[col.name] = var
            ent = ttk.Entry(frame, textvariable=var, width=20)
            ent.pack(fill="x")
            
            c += 1
            if c > 3: # wrap
                c = 0
                r += 1
        
        self.submit_btn.configure(text="✅ Ajouter ligne")
        
        # Ensure new widgets get themed
        from ui.theme_manager import ThemeManager
        ThemeManager().refresh_theme(self.inputs_inner)

    def _refresh_tree(self) -> None:
        # Clear tree
        self.tree.delete(*self.tree.get_children())
        if not self.active_table:
            return

        # Setup columns
        cols = [c.name for c in self.active_table.columns]
        self.tree.configure(columns=cols)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="w")
        
        # Load existing rows from table model
        for row_dict in self.active_table.rows:
            values = [row_dict.get(c, "") for c in cols]
            self.tree.insert("", "end", values=values)

    def _on_submit(self) -> None:
        if not self.active_table:
            return
        
        from core import validators
        
        row_data = {}
        for col in self.active_table.columns:
            if col.name in self.entry_vars:
                val = self.entry_vars[col.name].get().strip()
                
                # VALIDATION
                res = validators.validate_data_value(val, col.sql_type)
                if not res.is_valid:
                    messagebox.showerror("Erreur de type", f"Valeur invalide pour '{col.name}':\n" + "\n".join(res.errors))
                    return
                
                row_data[col.name] = val if val else "NULL"
            elif col.is_auto_increment:
                row_data[col.name] = "(AUTO)"
            else:
                row_data[col.name] = "NULL"
        
        if self._editing_idx is not None:
            # Update existing
            self.active_table.rows[self._editing_idx] = row_data
            self._editing_idx = None
            self.submit_btn.configure(text="✅ Ajouter ligne")
        else:
            # Add new
            self.active_table.rows.append(row_data)
        
        self._refresh_tree()
        
        # Clear inputs for next entry
        for v in self.entry_vars.values():
            v.set("")
            
        if self.on_updated:
            self.on_updated()

    def _load_selected_for_edit(self, event=None) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        idx = self.tree.index(item_id)
        
        if not self.active_table or idx >= len(self.active_table.rows):
            return
            
        self._editing_idx = idx
        row_data = self.active_table.rows[idx]
        
        for k, v in self.entry_vars.items():
            v.set(row_data.get(k, ""))
            
        self.submit_btn.configure(text="💾 Mettre à jour")

    def _cancel_edit(self) -> None:
        self._editing_idx = None
        self.submit_btn.configure(text="✅ Ajouter ligne")
        for v in self.entry_vars.values():
            v.set("")

    def _delete_selected_row(self) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        
        if not messagebox.askyesno("Confirmer", "Supprimer cette ligne ?"):
            return
            
        item_id = selection[0]
        idx = self.tree.index(item_id)
        
        if self.active_table and idx < len(self.active_table.rows):
            del self.active_table.rows[idx]
            self._refresh_tree()
            if self._editing_idx == idx:
                self._cancel_edit()
            elif self._editing_idx is not None and self._editing_idx > idx:
                self._editing_idx -= 1
                
            if self.on_updated:
                self.on_updated()

    def _on_tree_select(self, event) -> None:
        # Optional: Auto-load for edit on select? 
        # Maybe better to keep it manual via button to avoid clearing unsaved new info.
        pass

    def _clear_all_rows(self) -> None:
        if self.active_table:
            if not messagebox.askyesno("Confirmer", "Supprimer TOUTES les lignes ?"):
                return
            self.active_table.rows.clear()
            self._editing_idx = None
            self._refresh_tree()
            self._cancel_edit()
            if self.on_updated:
                self.on_updated()

