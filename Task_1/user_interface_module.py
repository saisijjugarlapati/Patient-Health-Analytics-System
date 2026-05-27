import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import matplotlib.pyplot as plt
from load_dataset_module import BaseModule

class UIError(Exception):
    #Custom exception for UI failures
    pass

class StrokeAnalysisApp(BaseModule):
    #Tkinter GUI for querying and analysing the stroke health dataset.

    def __init__(self, root, query_module, stats_module, dataframe):
        super().__init__("UserInterface")
        self.root = root
        self.qm = query_module
        self.__stats = stats_module
        self.__df = dataframe
        self.__current_result = None # private
        self.input_widgets = {}  

        self.root.title("Stroke Risk Health Analysis System")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg="#1a1a2e")

        self._setup_styles()
        self._build_layout()
    
    def get_current_result(self):
        #Returns current query result safely.
        if self.__current_result is None:
            raise UIError("No query has been run yet.")
        return self.__current_result

    def set_current_result(self, df):
        #Validates and stores query result.
        if not isinstance(df, pd.DataFrame):
            raise UIError("Result must be a DataFrame.")
        self.__current_result = df

    # ------------------------------------------------------------------ #
    #  Styles
    # ------------------------------------------------------------------ #
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#1a1a2e")
        style.configure("Card.TFrame", background="#16213e", relief="flat")
        style.configure(
            "TLabel",
            background="#1a1a2e",
            foreground="#e0e0e0",
            font=("Courier New", 10),
        )
        style.configure(
            "Header.TLabel",
            background="#1a1a2e",
            foreground="#00d4ff",
            font=("Courier New", 13, "bold"),
        )
        style.configure(
            "Title.TLabel",
            background="#1a1a2e",
            foreground="#ffffff",
            font=("Courier New", 16, "bold"),
        )
        style.configure(
            "TButton",
            background="#0f3460",
            foreground="#00d4ff",
            font=("Courier New", 10, "bold"),
            borderwidth=0,
            focuscolor="none",
        )
        style.map(
            "TButton",
            background=[("active", "#00d4ff"), ("pressed", "#007a99")],
            foreground=[("active", "#1a1a2e")],
        )
        style.configure(
            "Accent.TButton",
            background="#e94560",
            foreground="#ffffff",
            font=("Courier New", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#ff6b81")],
        )
        style.configure(
            "TCombobox",
            fieldbackground="#0f3460",
            background="#0f3460",
            foreground="#e0e0e0",
            selectbackground="#00d4ff",
            selectforeground="#1a1a2e",
            font=("Courier New", 10),
        )
        style.configure(
            "TEntry",
            fieldbackground="#0f3460",
            foreground="#e0e0e0",
            font=("Courier New", 10),
        )
        style.configure(
            "Treeview",
            background="#0f3460",
            foreground="#e0e0e0",
            fieldbackground="#0f3460",
            font=("Courier New", 9),
            rowheight=22,
        )
        style.configure(
            "Treeview.Heading",
            background="#00d4ff",
            foreground="#1a1a2e",
            font=("Courier New", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", "#e94560")])
        style.configure("TSeparator", background="#0f3460")

    # ------------------------------------------------------------------ #
    #  Layout
    # ------------------------------------------------------------------ #
    def _build_layout(self):
        # ── Header ────────────────────────────────────────────────────── #
        header = tk.Frame(self.root, bg="#0f3460", height=60)
        header.pack(fill="x", side="top")
        tk.Label(
            header,
            text="⬡  STROKE RISK HEALTH ANALYSIS SYSTEM",
            bg="#0f3460",
            fg="#00d4ff",
            font=("Courier New", 14, "bold"),
            pady=15,
        ).pack(side="left", padx=20)

        # ── Main container ────────────────────────────────────────────── #
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel (menu + inputs)
        self.left = ttk.Frame(container, style="Card.TFrame", width=340)
        self.left.pack(side="left", fill="y", padx=(0, 8))
        self.left.pack_propagate(False)

        # Right panel (results)
        self.right = ttk.Frame(container, style="Card.TFrame")
        self.right.pack(side="left", fill="both", expand=True)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        pad = {"padx": 14, "pady": 4}

        ttk.Label(self.left, text="SELECT QUERY", style="Header.TLabel").pack(
            anchor="w", padx=14, pady=(14, 2)
        )
        ttk.Separator(self.left, orient="horizontal").pack(fill="x", padx=14, pady=4)

        # Query choices
        self.queries = [
            "i.   Smokers & Hypertension Age Stats",
            "ii.  Heart Disease Stats",
            "iii. Hypertension Stroke Age by Gender",
            "iv.  Stats by Physical Activity",
            "v.   Stroke Age by Residence",
            "vi.  Dietary Habits by Stroke",
            "vii. Hypertension + Stroke Patients",
            "viii.Heart Disease + Stroke Patients",
            "ix.  Sleep Hours by Stroke",
            "x.   Filter Patients (Custom)",
            "xi.  Categorise by Risk Group",
            "xii. Regional Health Summary",
            "★   Descriptive Statistics",
        ]

        self.query_var = tk.StringVar(value=self.queries[0])
        self.query_combo = ttk.Combobox(
            self.left,
            textvariable=self.query_var,
            values=self.queries,
            state="readonly",
            width=36,
        )
        self.query_combo.pack(**pad, fill="x")
        self.query_combo.bind("<<ComboboxSelected>>", self._on_query_change)

        ttk.Separator(self.left, orient="horizontal").pack(fill="x", padx=14, pady=8)
        ttk.Label(self.left, text="INPUTS / FILTERS", style="Header.TLabel").pack(
            anchor="w", **pad
        )

        # Dynamic input area
        self.input_frame = ttk.Frame(self.left, style="Card.TFrame")
        self.input_frame.pack(fill="x", padx=14, pady=4)

        self._build_filter_inputs()  # Default inputs for query x

        ttk.Separator(self.left, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # Run button
        ttk.Button(
            self.left, text="▶  RUN QUERY", command=self._run_query
        ).pack(fill="x", padx=14, pady=2)
        
        # Export button
        ttk.Button(
            self.left,
            text="⬇  EXPORT TO CSV",
            command=self._export_csv,
            style="Accent.TButton",
        ).pack(fill="x", padx=14, pady=2)

        ttk.Separator(self.left, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # Quit button
        ttk.Button(
            self.left, text="✕  QUIT", command=self._quit
        ).pack(fill="x", padx=14, pady=2)

        # Status bar at bottom of left panel
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(
            self.left,
            textvariable=self.status_var,
            bg="#16213e",
            fg="#888",
            font=("Courier New", 8),
            wraplength=310,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(12, 6))

    def _build_right_panel(self):
        ttk.Label(self.right, text="RESULTS", style="Header.TLabel").pack(
            anchor="w", padx=14, pady=(14, 2)
        )
        ttk.Separator(self.right, orient="horizontal").pack(fill="x", padx=14, pady=4)

        # Treeview + scrollbars
        tree_frame = ttk.Frame(self.right, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.tree = ttk.Treeview(tree_frame, show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Info label beneath tree
        self.info_var = tk.StringVar(value="Run a query to see results.")
        tk.Label(
            self.right,
            textvariable=self.info_var,
            bg="#16213e",
            fg="#00d4ff",
            font=("Courier New", 9),
        ).pack(anchor="w", padx=14, pady=(0, 10))

    # ------------------------------------------------------------------ #
    #  Dynamic input widgets
    # ------------------------------------------------------------------ #
    def _clear_inputs(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.input_widgets = {}

    def _add_input(self, label, key, default="", choices=None):
        row = ttk.Frame(self.input_frame, style="Card.TFrame")
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=18, anchor="w").pack(side="left")
        if choices:
            var = tk.StringVar(value=default)
            w = ttk.Combobox(row, textvariable=var, values=choices, state="readonly", width=16)
            w.pack(side="left")
            self.input_widgets[key] = var
        else:
            var = tk.StringVar(value=default)
            w = ttk.Entry(row, textvariable=var, width=18)
            w.pack(side="left")
            self.input_widgets[key] = var

    def _build_filter_inputs(self):
        #Build inputs for query x (custom filter). Shown by default.
        self._clear_inputs()

        genders = ["", "Male", "Female", "Other"]
        smoke = ["", "Smokes", "Formerly smoked", "Never smoked", "Unknown"]
        regions = ["", "North", "South", "East", "West"]
        residence = ["", "Urban", "Rural"]
        activity = ["", "Sedentary", "Light", "Moderate", "Active"]
        yn = ["", "1", "0"]

        self._add_input("Gender:", "Gender", choices=genders)
        self._add_input("Min Age:", "min_age", default="")
        self._add_input("Max Age:", "max_age", default="")
        self._add_input("Smoking Status:", "Smoking Status", choices=smoke)
        self._add_input("Region:", "Region", choices=regions)
        self._add_input("Residence Type:", "Residence Type", choices=residence)
        self._add_input("Physical Activity:", "Physical Activity", choices=activity)
        self._add_input("Hypertension:", "Hypertension", choices=yn)
        self._add_input("Heart Disease:", "Heart Disease", choices=yn)
        self._add_input("Stroke Occurrence:", "Stroke Occurrence", choices=yn)

    def _build_stats_inputs(self):
        self._clear_inputs()

        numeric_cols = [
            c for c in self.__df.columns
            if pd.api.types.is_numeric_dtype(self.__df[c]) and c != "ID"   
        ]

        self._add_input("Feature:", "feature", choices=numeric_cols,
                        default=numeric_cols[0] if numeric_cols else "")

    def _on_query_change(self, event=None):
        selected = self.query_var.get()
        self._clear_inputs() 
        if selected.startswith("x."):
            self._build_filter_inputs()
        elif "★" in selected:
            self._build_stats_inputs()
        else:
            self._clear_inputs()
            ttk.Label(
                self.input_frame,
                text="No inputs required.",
                foreground="#555",
                background="#16213e",
                font=("Courier New", 9, "italic"),
            ).pack(anchor="w")
            
    # ------------------------------------------------------------------ #
    #  Display results in Treeview
    # ------------------------------------------------------------------ #

    def _display_dataframe(self, df, title=""):
        self.tree.delete(*self.tree.get_children())

        if df is None or df.empty:
            self.info_var.set("No results found.")
            self.set_current_result(pd.DataFrame())
            return

        df = df.reset_index(drop=True)
        cols = list(df.columns)

        self.tree["columns"] = cols

        # ---------------- columns ---------------- #
        for col in cols:
            self.tree.heading(col, text=col)

            # Calculate best-fit width based on content
            cell_lengths = df[col].astype(str).map(len)
            max_len = max(cell_lengths.max(), len(col))

            # Fine-tuned scaling factor
            width = max(80, min(max_len * 7, 300))

            self.tree.column(
                col,
                width=width,
                minwidth=80,
                stretch=False,   
                anchor="center"
            )

        # ---------------- rows (SAFE FIX ONLY) ---------------- #
        for _, row in df.iterrows():
            values = [str(v) for v in row]

            # safety: prevents mismatch crash
            if len(values) != len(cols):
                values = values[:len(cols)]

            self.tree.insert("", "end", values=values)

        self.info_var.set(f"{title}  |  {len(df)} row(s) returned.")
        self.set_current_result(df)
        self.status_var.set(f"Query complete: {len(df)} row(s).")

    # ------------------------------------------------------------------ #
    #  Run query dispatcher
    # ------------------------------------------------------------------ #
    def _run_query(self):
        selected = self.query_var.get()
        self.status_var.set("Running…")
        self.root.update_idletasks()

        try:
            if selected.startswith("i."):
                result = self.qm.get_smoking_hypertension_age_stats()
                self._display_dataframe(result, "Smokers/Hypertension Age Stats")

            elif selected.startswith("ii."):
                result = self.qm.get_heart_disease_stats()
                self._display_dataframe(result, "Heart Disease Stats")

            elif selected.startswith("iii."):
                result = self.qm.get_hypertension_stroke_age_by_gender()
                self._display_dataframe(result, "Hypertension Stroke Age by Gender")

            elif selected.startswith("iv."):
                result = self.qm.get_stats_by_activity_level()
                self._display_dataframe(result.reset_index(), "Stats by Physical Activity")

            elif selected.startswith("v."):
                result = self.qm.get_stroke_age_by_residence()
                self._display_dataframe(result, "Stroke Age by Residence")

            elif selected.startswith("vi."):
                result = self.qm.get_dietary_habits_by_stroke()
                self._display_dataframe(result, "Dietary Habits by Stroke")

            elif selected.startswith("vii."):
                result = self.qm.get_hypertension_stroke_patients()
                self._display_dataframe(result, "Hypertension + Stroke Patients")

            elif selected.startswith("viii."):
                result = self.qm.get_heart_disease_stroke_patients()
                self._display_dataframe(result, "Heart Disease + Stroke Patients")

            elif selected.startswith("ix."):
                result = self.qm.get_sleep_hours_by_stroke()
                self._display_dataframe(result, "Sleep Hours by Stroke")

            elif selected.startswith("x."):
                self._run_filter_query()

            elif selected.startswith("xi."):
                result = self.qm.categorize_by_risk_group()
                self._display_dataframe(result, "Risk Group Categories")

            elif selected.startswith("xii."):
                result = self.qm.generate_regional_summary()
                self._display_dataframe(result, "Regional Health Summary")

            elif "★" in selected:
                self._run_stats_query()

            else:
                raise UIError(f"Unknown query selected: {selected}")

        except UIError as e:
            messagebox.showerror("UI Error", str(e))
            self.status_var.set("Error — see dialog.")
        except Exception as e:
            self.error(f"Query failed: {e}")
            messagebox.showerror("Query Error", f"An error occurred:\n\n{e}")
            self.status_var.set("Error — see dialog.")

    def _run_filter_query(self):
        #Handle query x — custom multi-filter.
        widgets = self.input_widgets 
        kwargs = {}
        errors = []

        # Age range — handled separately (not a direct column filter)
        min_age_str = widgets.get("min_age", tk.StringVar()).get().strip()
        max_age_str = widgets.get("max_age", tk.StringVar()).get().strip()

        min_age = None
        max_age = None

        if min_age_str:
            try:
                min_age = float(min_age_str)
                if min_age < 0:
                    errors.append("Min Age must be a positive number.")
            except ValueError:
                errors.append(f"Min Age '{min_age_str}' is not a valid number.")

        if max_age_str:
            try:
                max_age = float(max_age_str)
                if max_age < 0:
                    errors.append("Max Age must be a positive number.")
            except ValueError:
                errors.append(f"Max Age '{max_age_str}' is not a valid number.")

        if min_age is not None and max_age is not None and min_age > max_age:
            errors.append("Min Age cannot be greater than Max Age.")

        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return

        # Categorical filters
        cat_keys = [
            "Gender", "Smoking Status", "Region",
            "Residence Type", "Physical Activity",
            "Hypertension", "Heart Disease", "Stroke Occurrence",
        ]
        binary_keys = {"Hypertension", "Heart Disease", "Stroke Occurrence"}

        for key in cat_keys:
            var = widgets.get(key)
            if var is None:
                continue
            val = var.get().strip()
            if val == "":
                continue
            if key in binary_keys:
                try:
                    kwargs[key] = int(val)
                except ValueError:
                    errors.append(f"'{key}' must be 0 or 1.")
            else:
                kwargs[key] = val

        if errors:
            messagebox.showerror("Input Error", "\n".join(errors))
            return

        result = self.qm.filter_patients(**kwargs)

        # Apply age range filter manually
        if min_age is not None:
            result = result[result["Age"] >= min_age]
        if max_age is not None:
            result = result[result["Age"] <= max_age]

        result = result.reset_index(drop=True)

        if result.empty:
            messagebox.showinfo("No Results", "No patients matched the selected filters.")
            self._display_dataframe(result, "Filtered Patients")
        else:
            self._display_dataframe(result, "Filtered Patients")

    def _run_stats_query(self):
        #Handle ★ Descriptive Statistics query.
        widgets = self.input_widgets  # ← no more getattr needed
        feature = widgets.get("feature", tk.StringVar()).get().strip()

        if not feature:
            raise UIError("Please select a feature.")

        if feature not in self.__df.columns:
            raise UIError(f"Feature '{feature}' not found in dataset.")

        try:
            desc = self.__stats.describe(self.__df[feature], feature_name=feature)
        except (TypeError, ValueError) as e:
            messagebox.showerror("Statistics Error", f"Cannot compute stats for '{feature}':\n{e}")
            return

        result_df = pd.DataFrame([{
            "Feature": desc["feature"],
            "Mean": round(desc["mean"], 4),
            "Median": round(desc["median"], 4),
            "Mode": desc["mode"],
            "Std Dev": round(desc["std_dev"], 4),
            "Variance": round(desc["variance"], 4),
            "Min": round(desc["min"], 4),
            "Max": round(desc["max"], 4),
            "Range": round(desc["range"], 4),
        }])

        self._display_dataframe(result_df, f"Descriptive Stats: {feature}")
        
    # ------------------------------------------------------------------ #
    #  Export
    # ------------------------------------------------------------------ #
    def _export_csv(self):
        #Exports current query results to a CSV file.
        try:
            result = self.get_current_result()
        except UIError:
            messagebox.showwarning("Export", "No results to export. Please run a query first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Results As",
            initialfile="query_results.csv",
        )
        if not filepath:
            return

        try:
            result.to_csv(filepath, index=False)
            self.log(f"Exported to {filepath}")
            messagebox.showinfo("Export Successful", f"Results saved to:\n{filepath}")
            self.status_var.set(f"Exported → {os.path.basename(filepath)}")
        except PermissionError:
            raise UIError("Permission denied. Choose a different location.")
        except Exception as e:
            raise UIError(f"Failed to export: {e}")
        
    # ------------------------------------------------------------------ #
    #  Quit
    # ------------------------------------------------------------------ #
    def _quit(self):
        #Prompts user confirmation before closing the application.
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.log("Application closed by user.")
            self.root.destroy()

def launch_ui(query_module, stats_module, dataframe):
    #Entry point called from main.py to launch the GUI.
    try:
        root = tk.Tk()
        app = StrokeAnalysisApp(root, query_module, stats_module, dataframe)
        root.mainloop()
    except Exception as e:
        print(f"[UserInterface ERROR] Failed to launch UI: {e}")
        raise UIError(f"UI launch failed: {e}")
