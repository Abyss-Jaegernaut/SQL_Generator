import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from controllers.app_controller import AppController
from ui.history_dialog import HistoryDialog
from ui.license_dialog import LicenseDialog
from ui.sample_data_frame import SampleDataFrame
from ui.sql_preview_frame import SQLPreviewFrame
from ui.table_definition_frame import TableDefinitionFrame


class MainWindow(ttk.Frame):
    """Main container for the application UI."""

    def __init__(self, master: tk.Misc, controller: AppController) -> None:
        super().__init__(master)
        self.controller = controller
        self.actions_vars = {
            "Database": tk.BooleanVar(value=True),
            "Table": tk.BooleanVar(value=True),
            "Data (Inserts)": tk.BooleanVar(value=True),
            "Insert": tk.BooleanVar(value=False),
            "GetById": tk.BooleanVar(value=False),
            "SelectAll": tk.BooleanVar(value=False),
            "Update": tk.BooleanVar(value=False),
            "Delete": tk.BooleanVar(value=False),
        }
        self.pack(fill="both", expand=True)
        self._setup_style()
        self._update_title()
        self._build_menu()
        self._build_layout()
        self._refresh_outputs()

    def _setup_style(self) -> None:
        """Configure custom ttk styles for a premium look."""
        style = ttk.Style()
        
        # Try to use a modern theme base
        current_themes = style.theme_names()
        if "vista" in current_themes:
            style.theme_use("vista")
        elif "clam" in current_themes:
            style.theme_use("clam")

        # Colors
        bg_main = "#f8f9fa"
        accent_color = "#0078d4"
        text_main = "#212529"
        border_color = "#dee2e6"

        style.configure("TFrame", background=bg_main)
        style.configure("TLabelframe", background=bg_main, foreground=accent_color, font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background=bg_main, foreground=accent_color)
        
        style.configure("TLabel", background=bg_main, foreground=text_main, font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9), padding=5)

        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        
        # Configure root
        self.winfo_toplevel().configure(bg=bg_main)

    def _update_title(self) -> None:
        root = self.winfo_toplevel()
        try:
            status = "PREMIUM" if self.controller.is_activated() else "VERSION D'ÉVALUATION"
        except Exception:
            # In case of error checking activation, assume not activated
            status = "VERSION D'ÉVALUATION"
        root.title(f"SQL Generator CRUD - {status}")

    def _build_menu(self) -> None:
        root = self.winfo_toplevel()
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Sauvegarder le projet…", command=self._save_project)
        file_menu.add_command(label="Charger un projet…", command=self._load_project)
        file_menu.add_separator()
        file_menu.add_command(label="Historique des générations…", command=self._show_history)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=root.destroy)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Activer la licence…", command=self._show_license)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=lambda: messagebox.showinfo("À propos", "SQL Generator CRUD v1.1\nDéveloppé pour un workflow SQL rapide."))

        menubar.add_cascade(label="Fichier", menu=file_menu)
        menubar.add_cascade(label="Aide", menu=help_menu)
        root.config(menu=menubar)

    def _show_license(self) -> None:
        try:
            if self.controller.is_activated():
                messagebox.showinfo("Licence", "Produit déjà activé (Version Premium).")
                return
            
            dialog = LicenseDialog(self, self.controller)
            self.wait_window(dialog)
            if hasattr(dialog, 'success') and dialog.success:
                self._update_title()
        except Exception as e:
            messagebox.showerror("Erreur", f"Problème avec le système d'activation: {str(e)}")

    def _show_history(self) -> None:
        try:
            history = self.controller.get_history()
            if not history:
                messagebox.showinfo("Historique", "L'historique est vide.")
                return
            HistoryDialog(self, history)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'accéder à l'historique: {str(e)}")

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.sample_data_frame = SampleDataFrame(master=self, controller=self.controller, on_updated=self._refresh_outputs)
        self.sample_data_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        self.table_frame = TableDefinitionFrame(
            master=self,
            controller=self.controller,
            on_updated=self._refresh_outputs,
            on_table_selected=self._on_table_selected,
        )
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        self.sql_preview_frame = SQLPreviewFrame(
            master=self, 
            actions_vars=self.actions_vars, 
            on_actions_changed=self._refresh_outputs,
            on_save_history=self.controller.add_to_history
        )
        self.sql_preview_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)

    def _on_table_selected(self, table_idx: int) -> None:
        """Called when user selects a different table in the definition frame."""
        # Use the tables from table_frame directly, not from controller
        # Guard against callback firing during initialization before table_frame is assigned
        if not hasattr(self, 'table_frame'):
            return
        
        tables = self.table_frame.tables
        if 0 <= table_idx < len(tables):
            self.sample_data_frame.set_active_table(tables[table_idx])
        else:
            self.sample_data_frame.set_active_table(None)

    def _refresh_outputs(self) -> None:
        try:
            active_actions = [k for k, v in self.actions_vars.items() if v.get()]
            scripts = self.controller.build_sql_artifacts(active_actions)
            self.sql_preview_frame.show_scripts(scripts)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du SQL: {str(e)}")

    def _save_project(self) -> None:
        try:
            # Use database name as project key; ask if missing.
            name = self.controller.current_project.database_name.strip()
            if not name:
                name = simpledialog.askstring("Sauvegarder", "Nom du projet (utilisé comme clé) :")
                if not name:
                    return
                self.controller.set_database_name(name.strip())
            self.controller.save_project()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder le projet: {str(e)}")

    def _load_project(self) -> None:
        try:
            projects = self.controller.list_projects()
            if not projects:
                tk.messagebox.showinfo("Charger", "Aucun projet sauvegardé.")
                return
            # Simple picker: ask by exact name
            names = "\n".join(f"- {p['name']}" for p in projects)
            name = simpledialog.askstring("Charger", f"Nom exact du projet à charger :\n\n{names}")
            if not name:
                return
            self.controller.current_project = self.controller.storage.load_project_by_name(name.strip())
            # Refresh UI with all tables
            self.table_frame.load_from_project(
                self.controller.current_project.database_name,
                self.controller.current_project.tables,
                self.controller.current_project.dbms
            )
            self._refresh_outputs()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le projet: {str(e)}")