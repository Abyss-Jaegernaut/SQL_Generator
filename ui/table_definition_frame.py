from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

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
        self.db_name_var.trace_add("write", lambda *args: self._apply_to_controller())

        ttk.Label(self, text="SGBD").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        self.dbms_var = tk.StringVar(value="SQL Server")
        self.dbms_var.trace_add("write", lambda *args: self._apply_to_controller())
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
        # Container for Listbox and Action buttons
        left.grid_rowconfigure(2, weight=0)
        left.grid_rowconfigure(0, weight=1)
        
        ttk.Label(left, text="Tables").pack(anchor="w")

        # Actions Frame (Pack FIRST at BOTTOM to guarantee visibility)
        actions_frame = ttk.Frame(left)
        actions_frame.pack(side="bottom", fill="x", pady=(5, 0))
        
        # Row 1: Nb + Spinbox + Ajouter Button
        row_add = ttk.Frame(actions_frame)
        row_add.pack(fill="x")
        
        ttk.Label(row_add, text="Nb").pack(side="left")
        
        self.bulk_count = tk.IntVar(value=1)
        sb = ttk.Spinbox(row_add, from_=1, to=20, textvariable=self.bulk_count, width=3)
        sb.pack(side="left", padx=(5, 5))
        
        self.btn_add = tk.Button(row_add, text="Ajouter", command=self._add_tables_bulk, bg="#f0f0f0", relief="raised")
        self.btn_add.pack(side="left", fill="x", expand=True)
        
        # Row 2: Delete Button
        self.btn_del = tk.Button(actions_frame, text="Supprimer table", command=self._delete_table, bg="#f0f0f0", relief="raised")
        self.btn_del.pack(fill="x", pady=(5, 0))
        
        # Frame for Listbox (Pack LAST to fill remaining space)
        list_frame = ttk.Frame(left)
        list_frame.pack(side="top", fill="both", expand=True, pady=2)
        
        self.table_list = tk.Listbox(list_frame, height=11, exportselection=False)
        self.table_list.pack(fill="both", expand=True)
        self.table_list.bind("<<ListboxSelect>>", self._on_table_select)
        
        self.update_theme_styles()

        # Columns table
        cols = ("name", "type", "nullable", "pk", "identity", "fk")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=9, selectmode="browse")
        self.tree.heading("name", text="Colonne")
        self.tree.heading("type", text="Type SQL")
        self.tree.heading("nullable", text="NULL")
        self.tree.heading("pk", text="PK")
        self.tree.heading("identity", text="AUTO INCREMENT")
        self.tree.heading("fk", text="F.KEY (Ref)")

        self.tree.column("name", width=120, anchor="w")
        self.tree.column("type", width=110, anchor="w")
        self.tree.column("nullable", width=50, anchor="center")
        self.tree.column("pk", width=40, anchor="center")
        self.tree.column("identity", width=105, anchor="center")
        self.tree.column("fk", width=120, anchor="w")

        self.tree.grid(row=3, column=1, columnspan=1, sticky="nsew", padx=6, pady=(6, 6))

        btns = ttk.Frame(self)
        btns.grid(row=4, column=1, columnspan=1, sticky="ew", padx=6, pady=(0, 6))
        ttk.Button(btns, text="➕ Ajouter", command=self._add_column).pack(side="left")
        ttk.Button(btns, text="✏️ Modifier", command=self._edit_selected).pack(side="left", padx=(6, 0))
        
        # Move Buttons (Middle)
        ttk.Button(btns, text="⬆️", width=3, command=self._move_column_up).pack(side="left", padx=(6, 0))
        ttk.Button(btns, text="⬇️", width=3, command=self._move_column_down).pack(side="left", padx=(2, 0))
        
        ttk.Button(btns, text="🗑️ Supprimer", command=self._delete_selected).pack(side="left", padx=(6, 0))
        # Button removed as everything is now reactive

        self.rowconfigure(3, weight=1)
        self.columnconfigure(1, weight=1)

        # Default minimal skeleton columns for convenience
        self._load_demo_defaults()

    def _load_demo_defaults(self) -> None:
        self._add_tables_bulk(initial=True)
        self._active_index = 0
        self._apply_to_controller()

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

    def _insert_row(self, name: str, sql_type: str, *, nullable: bool, pk: bool, identity: bool, fk_info: str = "") -> None:
        self.tree.insert(
            "",
            "end",
            values=(
                name,
                sql_type,
                "YES" if nullable else "NO",
                "YES" if pk else "NO",
                "YES" if identity else "NO",
                fk_info
            ),
        )

    def _selected_iid(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _current_table_index(self) -> int | None:
        sel = self.table_list.curselection()
        return sel[0] if sel else None

    def update_theme_styles(self) -> None:
        """Manually update tk.Button styles to match theme approximately."""
        from ui.theme_manager import ThemeManager
        theme = ThemeManager().current_theme
        
        # Default Dark
        bg = theme.button_bg 
        fg = theme.fg
        active_bg = theme.accent
        active_fg = "#ffffff"
        
        # Override for Clair/Light
        if theme.name == "Clair":
            bg = "#f0f0f0" # Standard Windows Button Face
            fg = "#000000"
            active_bg = "#e1e1e1"
            active_fg = "#000000"
        
        try:
             self.btn_add.configure(bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg)
             self.btn_del.configure(bg=bg, fg=fg, activebackground=active_bg, activeforeground=active_fg)
        except: pass

    def _add_tables_bulk(self, initial: bool = False) -> None:
        try:
            # 1. Safe get count
            try:
                count = self.bulk_count.get()
                if count < 1: count = 1
            except:
                count = 1

            # 2. Premium Check
            if not initial and count > 1 and not self.controller.is_activated():
                messagebox.showinfo("Premium Requis", "L'ajout groupé est limité à 1 table en version Standard.")
                count = 1
                self.bulk_count.set(1)

            # 3. Save previous state if possible (safe)
            if not initial:
                self._safe_persist()

            # 4. Generate & Add
            for i in range(count):
                new_name = self._generate_unique_name()
                # Create standard table with ID
                t = models.TableModel(name=new_name, columns=[
                    models.ColumnModel(name="id", sql_type="INT", nullable=False, is_primary_key=True, is_auto_increment=False)
                ])
                self.tables.append(t)
                self.table_list.insert("end", new_name)

            # 5. Update Controller & Selection
            if not initial:
                self._apply_to_controller()
                # Select the last added table
                new_idx = len(self.tables) - 1
                self._select_index_safely(new_idx)

            if initial:
                self._select_index_safely(0)
                
        except Exception as e:
            print(f"ADD ERROR: {e}")
            messagebox.showerror("Erreur", f"Impossible d'ajouter la table: {e}")

    def _generate_unique_name(self) -> str:
        base = "table"
        idx = len(self.tables) + 1
        name = f"{base}{idx}"
        existing = {t.name for t in self.tables}
        while name in existing:
            idx += 1
            name = f"{base}{idx}"
        return name

    def _delete_table(self) -> None:
        try:
            idx = self._active_index
            if idx is None:
                # Try to get from listbox selection directly
                sel = self.table_list.curselection()
                if sel: idx = sel[0]
            
            if idx is None: return

            if len(self.tables) <= 1:
                messagebox.showinfo("Info", "Vous devez garder au moins une table.")
                return

            del self.tables[idx]
            self.table_list.delete(idx)
            
            # Select neighbor
            new_idx = idx if idx < len(self.tables) else len(self.tables) - 1
            self._select_index_safely(new_idx)
            self._apply_to_controller()
            
        except Exception as e:
            print(f"DELETE ERROR: {e}")

    def _move_column_up(self) -> None:
        sel = self.tree.selection()
        if not sel: return
        iid = sel[0]
        idx = self.tree.index(iid)
        
        if idx > 0:
            self.tree.move(iid, "", idx - 1)
            # Reselect/See
            self.tree.see(iid)
            self._apply_to_controller()

    def _move_column_down(self) -> None:
        sel = self.tree.selection()
        if not sel: return
        iid = sel[0]
        idx = self.tree.index(iid)
        
        # Get total items
        total = len(self.tree.get_children())
        
        if idx < total - 1:
            self.tree.move(iid, "", idx + 1)
            # Reselect/See
            self.tree.see(iid)
            self._apply_to_controller()

    def _on_table_select(self, event=None) -> None:
        if getattr(self, "_ignore_select_event", False): return

        try:
            # Save OLD active table logic
            self._safe_persist()

            # Load NEW logic
            sel = self.table_list.curselection()
            if not sel: return
            
            idx = sel[0]
            self._active_index = idx
            self._load_table_into_form(idx)
        except Exception as e:
            print(f"SELECT ERROR: {e}")

    def _select_index_safely(self, idx: int) -> None:
        self._ignore_select_event = True
        try:
            self.table_list.selection_clear(0, "end")
            if 0 <= idx < self.table_list.size():
                self.table_list.selection_set(idx)
                self.table_list.activate(idx)
                self.table_list.see(idx)
                self._active_index = idx
                self._load_table_into_form(idx)
        finally:
            self._ignore_select_event = False

    def _safe_persist(self) -> None:
        """Non-blocking persist."""
        try:
            self._persist_current_form()
        except:
            pass

    def _persist_current_form(self) -> None:
        try:
            idx = self._active_index
            if idx is None or idx >= len(self.tables):
                return
            cols = []
            for iid in self.tree.get_children():
                # Safe read
                values = self.tree.item(iid, "values")
                if not values: continue
                
                name = values[0]
                sql_type = values[1]
                nullable = (values[2] == "YES")
                pk = (values[3] == "YES")
                identity = (values[4] == "YES")
                fk_txt = values[5] if len(values) > 5 else ""
                
                fk_table, fk_col = None, None
                if fk_txt and "(" in fk_txt and ")" in fk_txt:
                    try:
                        clean = fk_txt.replace("Ref: ", "").strip()
                        split = clean.split("(")
                        fk_table = split[0]
                        fk_col = split[1].strip(")")
                    except: pass
                    
                cols.append(
                    models.ColumnModel(
                        name=name,
                        sql_type=sql_type,
                        nullable=nullable,
                        is_primary_key=pk,
                        is_auto_increment=identity,
                        foreign_key_table=fk_table,
                        foreign_key_column=fk_col
                    )
                )
            
            # Save to the active slot
            raw_name = self.table_name_var.get().strip()
            
            # Sanitize table name
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)
            while "__" in clean_name: clean_name = clean_name.replace("__", "_")
            clean_name = clean_name.strip("_")
            
            # Update UI if changed (feedback for user)
            if raw_name != clean_name:
                self.table_name_var.set(clean_name)
            
            new_name = clean_name or self.tables[idx].name
            self.tables[idx] = models.TableModel(name=new_name, columns=cols, rows=self.tables[idx].rows)
            
            # Update listbox text only if changed
            current_text = self.table_list.get(idx)
            if current_text != new_name:
                self._ignore_select_event = True
                try:
                    self.table_list.delete(idx)
                    self.table_list.insert(idx, new_name)
                    if self._active_index == idx:
                        self.table_list.selection_set(idx)
                finally:
                    self._ignore_select_event = False
        except Exception as e:
            # Show error to user to debug silent failures
            messagebox.showerror("Erreur Interne", f"Erreur lors de la sauvegarde de la table : {e}")
            print(f"Error persisting form: {e}")

    def _load_table_into_form(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.tables):
            return
        table = self.tables[idx]
        self.table_name_var.set(table.name)
        for iid in list(self.tree.get_children()):
            self.tree.delete(iid)
        for col in table.columns:
            fk_str = ""
            if col.foreign_key_table and col.foreign_key_column:
                fk_str = f"Ref: {col.foreign_key_table}({col.foreign_key_column})"
            
            self._insert_row(
                col.name,
                col.sql_type,
                nullable=col.nullable,
                pk=col.is_primary_key,
                identity=col.is_auto_increment,
                fk_info=fk_str
            )
        
        if self.on_table_selected:
            self.on_table_selected(idx)

    def _add_column(self) -> None:
        # Find existing PKs and Names
        existing_pks = []
        existing_names = []
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            existing_names.append(vals[0])
            if vals[3] == "YES":
                existing_pks.append(vals[0])

        dlg = _ColumnDialog(self, title="Ajouter une colonne", tables=self.tables, existing_pks=existing_pks, existing_names=existing_names)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self._maybe_enforce_single_pk(dlg.result["pk"])
        
        fk_str = ""
        if dlg.result.get("fk_table") and dlg.result.get("fk_col"):
             fk_str = f"Ref: {dlg.result['fk_table']}({dlg.result['fk_col']})"

        self._insert_row(
            dlg.result["name"],
            dlg.result["type"],
            nullable=dlg.result["nullable"],
            pk=dlg.result["pk"],
            identity=dlg.result["identity"],
            fk_info=fk_str
        )
        self._apply_to_controller()

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
        
        if len(values) > 5 and "Ref: " in values[5]:
             clean = values[5].replace("Ref: ", "").strip()
             try:
                current["fk_table"] = clean.split("(")[0]
                current["fk_col"] = clean.split("(")[1].strip(")")
                current["is_fk"] = True
             except:
                pass
        else:
             current["is_fk"] = False
             current["fk_table"] = ""
             current["fk_col"] = ""

        # Find existing PKs and Names excluding THIS column
        existing_pks = []
        existing_names = []
        for item in self.tree.get_children():
            if item == iid: continue # Skip self
            vals = self.tree.item(item, "values")
            existing_names.append(vals[0])
            if vals[3] == "YES":
                existing_pks.append(vals[0])

        dlg = _ColumnDialog(self, title="Modifier la colonne", initial=current, tables=self.tables, existing_pks=existing_pks, existing_names=existing_names)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        
        fk_str = ""
        if dlg.result.get("fk_table") and dlg.result.get("fk_col"):
             fk_str = f"Ref: {dlg.result['fk_table']}({dlg.result['fk_col']})"
        self._maybe_enforce_single_pk(dlg.result["pk"], editing_iid=iid)
        self.tree.item(
            iid,
            values=(
                dlg.result["name"],
                dlg.result["type"],
                "YES" if dlg.result["nullable"] else "NO",
                "YES" if dlg.result["pk"] else "NO",
                "YES" if dlg.result["identity"] else "NO",
                fk_str
            ),
        )
        self._apply_to_controller()

    def _delete_selected(self) -> None:
        iid = self._selected_iid()
        if iid is None:
            return
        self.tree.delete(iid)
        self._apply_to_controller()

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
    def __init__(self, master, *, title: str, initial: dict | None = None, tables: list = None, existing_pks: list[str] = None, existing_names: list[str] = None) -> None:
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result: dict | None = None
        self.tables = tables or []
        self.existing_pks = existing_pks or []
        self.existing_names = [n.lower() for n in (existing_names or [])] # Store as lower for case-insensitive check

        # Center the window
        self.withdraw()  # Hide while calculating
        self.update_idletasks()
        w = 420 # Increased width for buttons
        h = 440 # Reduced height (optimized)
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.deiconify()

        initial = initial or {"name": "", "type": "", "nullable": True, "pk": False, "identity": False, "is_fk": False, "fk_table": "", "fk_col": ""}
        self.name_var = tk.StringVar(value=initial["name"])
        self.type_var = tk.StringVar(value=initial["type"])
        self.null_var = tk.BooleanVar(value=bool(initial["nullable"]))
        self.pk_var = tk.BooleanVar(value=bool(initial["pk"]))
        self.identity_var = tk.BooleanVar(value=bool(initial["identity"]))
        
        # FK Vars
        self.fk_var = tk.BooleanVar(value=bool(initial.get("is_fk")))
        self.fk_table_var = tk.StringVar(value=initial.get("fk_table", ""))
        self.fk_col_var = tk.StringVar(value=initial.get("fk_col", ""))

        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

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
            "CHAR(10)",
            "DATE",
            "DATETIME",
            "BOOLEAN",
        ]
        type_combo = ttk.Combobox(frame, textvariable=self.type_var, values=type_options, width=24)
        type_combo.grid(row=3, column=0, sticky="ew", pady=(2, 8))
        type_combo.configure(state="normal")  # allow custom typing

        opts = ttk.Frame(frame)
        opts.grid(row=4, column=0, sticky="w")
        
        self.chk_null = ttk.Checkbutton(opts, text="NULL autorisé", variable=self.null_var)
        self.chk_null.pack(side="left")
        
        self.chk_pk = ttk.Checkbutton(opts, text="PK", variable=self.pk_var, command=self._on_pk_toggle)
        self.chk_pk.pack(side="left", padx=(8, 0))
        
        self.chk_identity = ttk.Checkbutton(opts, text="AUTO INCREMENT", variable=self.identity_var)
        self.chk_identity.pack(side="left", padx=(8, 0))

        # FK Section
        fk_frame = ttk.LabelFrame(frame, text="Clé Étrangère (FK)", padding=10)
        fk_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Checkbutton(fk_frame, text="Activer FK", variable=self.fk_var, command=self._toggle_fk).pack(anchor="w")
        
        self.fk_details = ttk.Frame(fk_frame)
        self.fk_details.pack(fill="x", pady=(5, 0))
        
        ttk.Label(self.fk_details, text="Table réf.").pack(side="left")
        table_names = [t.name for t in self.tables]
        self.fk_table_cb = ttk.Combobox(self.fk_details, textvariable=self.fk_table_var, values=table_names, width=12)
        self.fk_table_cb.pack(side="left", padx=5)
        
        ttk.Label(self.fk_details, text="Col.").pack(side="left")
        self.fk_col_cb = ttk.Combobox(self.fk_details, textvariable=self.fk_col_var, width=12, state="readonly")
        self.fk_col_cb.pack(side="left", padx=5)
        
        self.fk_table_cb.bind("<<ComboboxSelected>>", self._on_fk_table_change)

        btns = ttk.Frame(frame)
        btns.grid(row=6, column=0, sticky="e", pady=(10, 0))
        ttk.Button(btns, text="Annuler", command=self._cancel).pack(side="right")
        ttk.Button(btns, text="OK", command=self._ok).pack(side="right", padx=(0, 8))

        self._on_pk_toggle()
        self._toggle_fk()

        # Apply theme at the VERY END to catch all children including FK frames
        from ui.theme_manager import ThemeManager
        tm = ThemeManager()
        tm.refresh_theme(self)
        
        # Force Toplevel background to match theme
        if tm.current_theme:
            self.configure(bg=tm.current_theme.bg)

        self.transient(master)
        self.grab_set()

        self.transient(master)
        self.grab_set()

    def _on_fk_table_change(self, event=None) -> None:
        table_name = self.fk_table_var.get()
        if not table_name: return
        
        # Find target table
        target = next((t for t in self.tables if t.name == table_name), None)
        if target:
            # Update columns list
            cols = [c.name for c in target.columns]
            self.fk_col_cb["values"] = cols
            
            # Auto-select PK
            pk = next((c.name for c in target.columns if c.is_primary_key), None)
            if pk:
                self.fk_col_var.set(pk)
            elif cols:
                self.fk_col_var.set(cols[0])

    def _on_pk_toggle(self) -> None:
        if not self.pk_var.get():
            self.identity_var.set(False)

    def _on_pk_toggle(self) -> None:
        """Handle PK toggle: PK implies NOT NULL and check for Composite Key."""
        is_pk = self.pk_var.get()
        
        # Check for Composite Key Warning
        # Only warn if turning ON, and there are other PKs already
        if is_pk and self.existing_pks:
             msg = (f"Une clé primaire existe déjà ({', '.join(self.existing_pks)}).\n\n"
                    "Voulez-vous ajouter cette colonne à la clé primaire existante (Clé Composite) ?\n"
                    "Non = Annuler le cochage.")
             if not messagebox.askyesno("Clé Composite ?", msg):
                 self.pk_var.set(False)
                 return

        if(is_pk):
            # Disable Nullable and uncheck it
            self.null_var.set(False)
            self.chk_null.configure(state="disabled")
            
            # PK often implies Auto Increment for INT, but let user choose.
            # Could enable Identity if type is INT, but simple is better.
        else:
            # Re-enable Nullable
            self.chk_null.configure(state="normal")
            # Default back to True (Nullable) for convenience? No, keep current state.

    def _toggle_fk(self) -> None:
        if self.fk_var.get():
            for child in self.fk_details.winfo_children():
                try:
                    child.configure(state="normal")
                except: pass
        else:
            for child in self.fk_details.winfo_children():
                try:
                    child.configure(state="disabled")
                except: pass

    def _ok(self) -> None:
        name = self.name_var.get().strip()
        sql_type = self.type_var.get().strip()
        
        # Sanitize name (No spaces allowed in standard SQL identifiers usually)
        # Sanitize name (Keep only A-Z, 0-9, _)
        import re
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        while "__" in name:
            name = name.replace("__", "_")
        name = name.strip("_") # Remove leading/trailing underscores

        if not name:
            messagebox.showerror("Erreur", "Le nom de colonne est obligatoire.")
            return

        # Check duplicate name
        if name.lower() in self.existing_names:
            # If editing, we excluded self from existing_names, so presence means conflict
            messagebox.showerror("Erreur", f"Une colonne nommée '{name}' existe déjà.")
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
        
        # FK Validation
        if self.fk_var.get():
            if not self.fk_table_var.get().strip():
                messagebox.showerror("Erreur", "Veuillez sélectionner une table de référence.")
                return
            if not self.fk_col_var.get().strip():
                messagebox.showerror("Erreur", "Veuillez indiquer la colonne de référence.")
                return

        self.result = {
            "name": name,
            "type": sql_type,
            "nullable": bool(self.null_var.get()),
            "pk": bool(self.pk_var.get()),
            "identity": bool(self.identity_var.get()),
            "fk_table": self.fk_table_var.get().strip() if self.fk_var.get() else None,
            "fk_col": self.fk_col_var.get().strip() if self.fk_var.get() else None,
        }
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()
