from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from controllers.app_controller import AppController
from core import models


class TableDefinitionFrame(ttk.LabelFrame):
    """Define database/table and manage columns (V1.0.1 usable)."""

    def __init__(self, master, controller: AppController, on_updated, on_table_selected=None) -> None:
        super().__init__(master, text="Définition table")
        self.controller = controller
        self.on_updated = on_updated
        self.on_table_selected = on_table_selected

        self.db_name_var = tk.StringVar()
        self.table_name_var = tk.StringVar()
        self._active_index: int | None = None
        self.tables: list[models.TableModel] = []  # Initialize early to avoid attribute errors
        self._build_form()

    def _build_form(self) -> None:
        # Top form: DB + table
        ttk.Label(self, text="Base de données (optionnel)").grid(
            row=0, column=0, sticky="w", padx=6, pady=(6, 2)
        )
        ttk.Entry(self, textvariable=self.db_name_var).grid(
            row=0, column=1, sticky="ew", padx=6, pady=(6, 2)
        )

        ttk.Label(self, text="SGBD").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        self.dbms_var = tk.StringVar(value="SQL Server")
        dbms_combo = ttk.Combobox(
            self, 
            textvariable=self.dbms_var, 
            values=["SQL Server", "MySQL", "PostgreSQL"],
            state="readonly",
            width=18
        )
        dbms_combo.grid(row=1, column=1, sticky="w", padx=6, pady=2)

        ttk.Label(self, text="Table").grid(row=2, column=0, sticky="w", padx=6, pady=2)
        ttk.Entry(self, textvariable=self.table_name_var).grid(
            row=2, column=1, sticky="ew", padx=6, pady=2
        )

        self.columnconfigure(1, weight=1)

        # Table list (multi-table)
        left = ttk.Frame(self)
        left.grid(row=3, column=0, sticky="nsw", padx=(6, 6), pady=(6, 6))
        ttk.Label(left, text="Tables").pack(anchor="w")
        self.table_list = tk.Listbox(left, height=8, exportselection=False)
        self.table_list.pack(fill="y", expand=False)
        self.table_list.bind("<<ListboxSelect>>", self._on_table_select)

        add_frame = ttk.Frame(left)
        add_frame.pack(fill="x", pady=(4, 0))
        ttk.Label(add_frame, text="Nb").pack(side="left")
        self.bulk_count = tk.IntVar(value=1)
        ttk.Spinbox(add_frame, from_=1, to=20, textvariable=self.bulk_count, width=4).pack(side="left", padx=(2, 6))
        ttk.Button(add_frame, text="Ajouter", command=self._add_tables_bulk).pack(side="left")
        ttk.Button(left, text="Supprimer table", command=self._delete_table).pack(fill="x", pady=(4, 0))

        # Columns table
        cols = ("name", "type", "nullable", "pk", "identity")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=9, selectmode="browse")
        self.tree.heading("name", text="Colonne")
        self.tree.heading("type", text="Type SQL")
        self.tree.heading("nullable", text="NULL")
        self.tree.heading("pk", text="PK")
        self.tree.heading("identity", text="AUTO INCREMENT")

        self.tree.column("name", width=140, anchor="w")
        self.tree.column("type", width=120, anchor="w")
        self.tree.column("nullable", width=60, anchor="center")
        self.tree.column("pk", width=45, anchor="center")
        self.tree.column("identity", width=105, anchor="center")

        self.tree.grid(row=3, column=1, columnspan=1, sticky="nsew", padx=6, pady=(6, 6))

        btns = ttk.Frame(self)
        btns.grid(row=4, column=1, columnspan=1, sticky="ew", padx=6, pady=(0, 6))
        ttk.Button(btns, text="➕ Ajouter", command=self._add_column).pack(side="left")
        ttk.Button(btns, text="✏️ Modifier", command=self._edit_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="🗑️ Supprimer", command=self._delete_selected).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="⚡ Appliquer", command=self._apply_to_controller).pack(side="right")

        self.rowconfigure(3, weight=1)
        self.columnconfigure(1, weight=1)

        # Default minimal skeleton columns for convenience
        self._load_demo_defaults()

    def _load_demo_defaults(self) -> None:
        self._add_tables_bulk(initial=True)
        self._active_index = 0

    def load_from_project(self, db_name: str, tables: list[models.TableModel], dbms: str = "sqlserver") -> None:
        """Populate the frame with existing project data."""
        self.db_name_var.set(db_name)
        self.dbms_var.set(dbms)
        # Clear existing
        self.tables = list(tables)  # shallow copy list
        self.table_list.delete(0, "end")
        
        # Repopulate listbox
        if not self.tables:
            # Fallback if empty, though unlikely for a saved project
            self._add_tables_bulk(initial=True)
        else:
            for t in self.tables:
                self.table_list.insert("end", t.name)
            
            # Select first table
            self.table_list.selection_set(0)
            self._active_index = 0
            self._load_table_into_form(0)

    def _insert_row(self, name: str, sql_type: str, *, nullable: bool, pk: bool, identity: bool) -> None:
        self.tree.insert(
            "",
            "end",
            values=(
                name,
                sql_type,
                "YES" if nullable else "NO",
                "YES" if pk else "NO",
                "YES" if identity else "NO",
            ),
        )

    def _selected_iid(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _current_table_index(self) -> int | None:
        sel = self.table_list.curselection()
        return sel[0] if sel else None

    def _add_tables_bulk(self, initial: bool = False) -> None:
        count = self.bulk_count.get() if not initial else 1
        start_index = len(self.tables)
        for i in range(count):
            name = f"table{start_index + i + 1}"
            table = models.TableModel(name=name, columns=[models.ColumnModel(name="id", sql_type="INT", nullable=False, is_primary_key=True, is_auto_increment=False)])
            self.tables.append(table)
            self.table_list.insert("end", name)
        if initial:
            self.table_list.selection_set(0)
            self._active_index = 0
            self._load_table_into_form(0)

    def _delete_table(self) -> None:
        idx = self._active_index
        if idx is None:
            return
        if len(self.tables) <= 1:
            messagebox.showinfo("Info", "Il doit rester au moins une table.")
            return
        # If possible, save current form state before deleting? 
        # Actually no, we are deleting it, so no need to save.
        
        del self.tables[idx]
        self.table_list.delete(idx)
        
        new_index = min(idx, len(self.tables) - 1)
        self.table_list.selection_clear(0, "end")
        self.table_list.selection_set(new_index)
        
        self._active_index = new_index
        self._load_table_into_form(new_index)

    def _on_table_select(self, event=None) -> None:
        # First, save the PREVIOUSLY active table from the current form
        self._persist_current_form()
        
        # Now switch to the NEW selection
        idx = self._current_table_index()
        if idx is None:
            return
        self._active_index = idx
        self._load_table_into_form(idx)

    def _persist_current_form(self) -> None:
        idx = self._active_index
        if idx is None or idx >= len(self.tables):
            return
        cols = []
        for iid in self.tree.get_children():
            name, sql_type, nullable, pk, identity = self.tree.item(iid, "values")
            cols.append(
                models.ColumnModel(
                    name=name,
                    sql_type=sql_type,
                    nullable=(nullable == "YES"),
                    is_primary_key=(pk == "YES"),
                    is_auto_increment=(identity == "YES"),
                )
            )
        # Save to the active slot
        new_name = self.table_name_var.get().strip() or self.tables[idx].name
        self.tables[idx] = models.TableModel(name=new_name, columns=cols, rows=self.tables[idx].rows)
        
        # Update listbox text only if changed
        current_text = self.table_list.get(idx)
        if current_text != new_name:
            # We need to preserve selection if it's on this item or another
            # But changing the listbox while generic events are firing is tricky.
            # Minimal approach:
            was_selected = (self._current_table_index() == idx)
            self.table_list.delete(idx)
            self.table_list.insert(idx, new_name)
            if was_selected:
                self.table_list.selection_set(idx)

    def _load_table_into_form(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.tables):
            return
        table = self.tables[idx]
        self.table_name_var.set(table.name)
        for iid in list(self.tree.get_children()):
            self.tree.delete(iid)
        for col in table.columns:
            self._insert_row(
                col.name,
                col.sql_type,
                nullable=col.nullable,
                pk=col.is_primary_key,
                identity=col.is_auto_increment,
            )
        
        if self.on_table_selected:
            self.on_table_selected(idx)

    def _add_column(self) -> None:
        dlg = _ColumnDialog(self, title="Ajouter une colonne")
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self._maybe_enforce_single_pk(dlg.result["pk"])
        self._insert_row(
            dlg.result["name"],
            dlg.result["type"],
            nullable=dlg.result["nullable"],
            pk=dlg.result["pk"],
            identity=dlg.result["identity"],
        )

    def _edit_selected(self) -> None:
        iid = self._selected_iid()
        if iid is None:
            messagebox.showinfo("Modifier", "Sélectionnez une colonne à modifier.")
            return
        values = self.tree.item(iid, "values")
        current = {
            "name": values[0],
            "type": values[1],
            "nullable": values[2] == "YES",
            "pk": values[3] == "YES",
            "identity": values[4] == "YES",
        }
        dlg = _ColumnDialog(self, title="Modifier la colonne", initial=current)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self._maybe_enforce_single_pk(dlg.result["pk"], editing_iid=iid)
        self.tree.item(
            iid,
            values=(
                dlg.result["name"],
                dlg.result["type"],
                "YES" if dlg.result["nullable"] else "NO",
                "YES" if dlg.result["pk"] else "NO",
                "YES" if dlg.result["identity"] else "NO",
            ),
        )

    def _delete_selected(self) -> None:
        iid = self._selected_iid()
        if iid is None:
            return
        self.tree.delete(iid)

    def _maybe_enforce_single_pk(self, pk_selected: bool, editing_iid: str | None = None) -> None:
        # V1.0.1: one PK only (simplifies SP GetById/Delete)
        if not pk_selected:
            return
        for iid in self.tree.get_children():
            if editing_iid is not None and iid == editing_iid:
                continue
            values = list(self.tree.item(iid, "values"))
            # unset PK/IDENTITY on others
            values[3] = "NO"
            values[4] = "NO"
            self.tree.item(iid, values=tuple(values))

    def _apply_to_controller(self) -> None:
        self._persist_current_form()
        self.controller.set_database_name(self.db_name_var.get().strip())
        self.controller.set_dbms(self.dbms_var.get())
        self.controller.set_tables(self.tables)

        if self.on_updated:
            self.on_updated()


class _ColumnDialog(tk.Toplevel):
    def __init__(self, master, *, title: str, initial: dict | None = None) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result: dict | None = None

        # Center the window
        self.withdraw()  # Hide while calculating
        self.update_idletasks()
        w = 300 # Estimated width
        h = 300 # Estimated height
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.deiconify()

        initial = initial or {"name": "", "type": "", "nullable": True, "pk": False, "identity": False}
        self.name_var = tk.StringVar(value=initial["name"])
        self.type_var = tk.StringVar(value=initial["type"])
        self.null_var = tk.BooleanVar(value=bool(initial["nullable"]))
        self.pk_var = tk.BooleanVar(value=bool(initial["pk"]))
        self.identity_var = tk.BooleanVar(value=bool(initial["identity"]))

        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Nom de colonne").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.name_var, width=26).grid(row=1, column=0, sticky="ew", pady=(2, 8))

        ttk.Label(frame, text="Type SQL").grid(row=2, column=0, sticky="w")
        type_options = [
            "INT",
            "BIGINT",
            "SMALLINT",
            "BIT",
            "DATE",
            "DATETIME",
            "DECIMAL(18,2)",
            "FLOAT",
            "VARCHAR(10)",
            "VARCHAR(20)",
            "VARCHAR(30)",
            "VARCHAR(50)",
            "VARCHAR(100)",
            "VARCHAR(255)",
            "VARCHAR(500)",
            "VARCHAR(MAX)",
            "TEXT",
        ]
        type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=type_options, width=24)
        type_combo.grid(row=3, column=0, sticky="ew", pady=(2, 8))
        type_combo.configure(state="normal")  # allow custom typing

        opts = ttk.Frame(frame)
        opts.grid(row=4, column=0, sticky="w")
        ttk.Checkbutton(opts, text="NULL autorisé", variable=self.null_var).pack(side="left")
        ttk.Checkbutton(opts, text="PK", variable=self.pk_var, command=self._on_pk_toggle).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(opts, text="AUTO INCREMENT", variable=self.identity_var).pack(side="left", padx=(8, 0))

        btns = ttk.Frame(frame)
        btns.grid(row=5, column=0, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Annuler", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="OK", command=self._ok).pack(side="right", padx=(0, 8))

        self._on_pk_toggle()

        self.transient(master)
        self.grab_set()

    def _on_pk_toggle(self) -> None:
        if not self.pk_var.get():
            self.identity_var.set(False)

    def _ok(self) -> None:
        name = self.name_var.get().strip()
        sql_type = self.type_var.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Le nom de colonne est obligatoire.")
            return
        if not sql_type:
            messagebox.showerror("Erreur", "Le type SQL est obligatoire.")
            return
        if self.identity_var.get():
            is_int = "INT" in sql_type.upper()
            is_date = "DATE" in sql_type.upper() or "TIME" in sql_type.upper()
            if not is_int and not is_date:
                messagebox.showerror("Erreur", "L'auto-remplissage n'est autorisé que pour les types numériques (IDENTITY) ou Date/Time (DEFAULT NOW).")
                return
            if is_int and not self.pk_var.get():
                messagebox.showerror("Erreur", "AUTO INCREMENT (INT) n'est autorisé que si la colonne est Primary Key.")
                return
        self.result = {
            "name": name,
            "type": sql_type,
            "nullable": bool(self.null_var.get()),
            "pk": bool(self.pk_var.get()),
            "identity": bool(self.identity_var.get()),
        }
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()
