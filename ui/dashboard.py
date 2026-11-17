import os
import threading
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from organizer.file_manager import FileOrganizer


# ---------------------------------------------------------------------------
# Smart File Organizer — redesigned desktop interface
# ---------------------------------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#0B0C12"
SIDEBAR = "#10111A"
PANEL = "#171923"
PANEL_ALT = "#1D2030"
BORDER = "#292C3B"
TEXT = "#F4F5FA"
MUTED = "#9298AE"
PURPLE = "#8B3DFF"
PURPLE_HOVER = "#7428E8"
GREEN = "#36C995"
ORANGE = "#F0A34A"
RED = "#F16D7A"
BLUE = "#5B9BFF"

CATEGORY_META = {
    "Images": ("▧", "#B783FF"),
    "Documents": ("▤", "#6FA8FF"),
    "Videos": ("▷", "#F18B9A"),
    "Audio": ("♫", "#E6A0FF"),
    "Web Files": ("⌘", "#56C9C0"),
    "Source Code": ("</>", "#80A7FF"),
    "Data Files": ("▦", "#E8B45C"),
    "Archives": ("▣", "#D49A65"),
    "Applications": ("◈", "#F08D72"),
    "Fonts": ("Aa", "#B4A0FF"),
    "Design Files": ("✧", "#F28BC2"),
    "3D Files": ("◇", "#7CC7E8"),
    "E-books": ("▥", "#A4C77A"),
    "System Files": ("⚙", "#9CA5B8"),
    "Temporary Files": ("◷", "#E6A45C"),
    "Others": ("···", "#A0A5B5"),
}


class SmartFileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Organizer")
        self.geometry("1440x900")
        self.minsize(1120, 720)
        self.configure(fg_color=BG)

        self.organizer = FileOrganizer()
        self.selected_folder = None
        self.preview_items = []
        self.current_page = "Overview"
        self.last_result = None
        self.search_var = ctk.StringVar()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.show_page("Overview")

    # ------------------------------- shared UI ------------------------------

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=238, fg_color=SIDEBAR, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(8, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(25, 30))
        logo = ctk.CTkFrame(brand, width=42, height=42, corner_radius=13, fg_color=PURPLE)
        logo.pack(side="left")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="S", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").place(relx=.5, rely=.48, anchor="center")
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=11)
        ctk.CTkLabel(brand_text, text="Smart File", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(brand_text, text="ORGANIZER", font=ctk.CTkFont(size=9, weight="bold"), text_color=MUTED).pack(anchor="w", pady=(1, 0))

        ctk.CTkLabel(self.sidebar, text="WORKSPACE", text_color="#666D83", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=25, pady=(0, 10))
        self.nav_buttons = {}
        nav_items = [
            ("Overview", "⌂"),
            ("Smart Organizer", "▤"),
            ("File Explorer", "▣"),
            ("Storage Analyzer", "▥"),
            ("Activity History", "◷"),
        ]
        for name, glyph in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {glyph}     {name}", anchor="w",
                height=45, corner_radius=11, fg_color="transparent",
                hover_color="#222333", text_color=MUTED,
                font=ctk.CTkFont(size=13, weight="normal"),
                command=lambda n=name: self.show_page(n),
            )
            btn.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[name] = btn

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(self.sidebar, text="QUICK ACCESS", text_color="#666D83", font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=25, pady=(0, 10))
        self.folder_shortcut = ctk.CTkButton(
            self.sidebar, text="  +   Choose a folder", anchor="w", height=42,
            corner_radius=10, fg_color="#211B32", hover_color="#302044",
            text_color="#C8A9FF", font=ctk.CTkFont(size=12, weight="bold"),
            command=self.choose_folder,
        )
        self.folder_shortcut.pack(fill="x", padx=13)

        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=22, pady=22)
        ctk.CTkLabel(footer, text="●  SYSTEM READY", text_color=GREEN, font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(footer, text="Version 1.0.0", text_color="#62687B", font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(7, 0))

    def _header(self, title, subtitle, action_text=None, action=None):
        head = ctk.CTkFrame(self.main, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=34, pady=(27, 18))
        head.grid_columnconfigure(0, weight=1)
        left = ctk.CTkFrame(head, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text=title, text_color=TEXT, font=ctk.CTkFont(size=27, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(left, text=subtitle, text_color=MUTED, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(5, 0))
        if action_text:
            ctk.CTkButton(head, text=action_text, command=action, height=40, corner_radius=12,
                          fg_color=PURPLE, hover_color=PURPLE_HOVER,
                          font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="e", padx=(12, 0))

    def _content(self):
        frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent", corner_radius=0)
        frame.grid(row=1, column=0, sticky="nsew", padx=34, pady=(0, 25))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="content")
        return frame

    def _card(self, parent, title=None, subtitle=None, **kwargs):
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=17, border_width=1, border_color=BORDER, **kwargs)
        if title:
            ctk.CTkLabel(card, text=title, text_color=TEXT, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=18, pady=(16, 2))
        if subtitle:
            ctk.CTkLabel(card, text=subtitle, text_color=MUTED, font=ctk.CTkFont(size=11)).pack(anchor="w", padx=18, pady=(0, 10))
        return card

    def _clear_main(self):
        for child in self.main.winfo_children():
            child.destroy()

    def show_page(self, page):
        self.current_page = page
        self._clear_main()
        for name, btn in self.nav_buttons.items():
            active = name == page
            btn.configure(
                fg_color="#2A1D40" if active else "transparent",
                text_color="#D5BFFF" if active else MUTED,
                font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
            )
        if page == "Overview":
            self._overview()
        elif page == "Smart Organizer":
            self._organizer_page()
        elif page == "File Explorer":
            self._explorer_page()
        elif page == "Storage Analyzer":
            self._storage_page()
        else:
            self._history_page()

    def choose_folder(self):
        selected = filedialog.askdirectory(title="Choose a folder to scan")
        if selected:
            self.selected_folder = Path(selected)
            self.preview_items = []
            self.show_page(self.current_page if self.current_page != "Overview" else "Overview")

    def _scan(self):
        if not self.selected_folder or not self.selected_folder.exists():
            return []
        rows = []
        try:
            for item in self.selected_folder.iterdir():
                if item.is_file():
                    try:
                        rows.append({
                            "path": item,
                            "name": item.name,
                            "category": self.organizer.get_category(item),
                            "size": item.stat().st_size,
                            "modified": item.stat().st_mtime,
                        })
                    except OSError:
                        continue
        except OSError as exc:
            messagebox.showerror("Scan failed", str(exc))
        return rows

    @staticmethod
    def _format_size(size):
        size = float(size)
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024

    def _stat_card(self, parent, title, value, detail, glyph, accent):
        card = self._card(parent)
        card.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=17, pady=(15, 8))
        ctk.CTkLabel(top, text=title, text_color=MUTED, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        icon = ctk.CTkLabel(top, text=glyph, text_color=accent, fg_color="#282039", corner_radius=9, width=32, height=32, font=ctk.CTkFont(size=16, weight="bold"))
        icon.pack(side="right")
        ctk.CTkLabel(card, text=value, text_color=TEXT, font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=17)
        ctk.CTkLabel(card, text=detail, text_color=MUTED, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=17, pady=(3, 15))
        return card

    # -------------------------------- overview ------------------------------

    def _overview(self):
        folder_name = self.selected_folder.name if self.selected_folder else "Your workspace"
        self._header(folder_name, str(self.selected_folder) if self.selected_folder else "A clear view of your files and storage", "＋  Choose folder", self.choose_folder)
        content = self._content()
        if not self.selected_folder:
            welcome = self._card(content)
            welcome.grid(row=0, column=0, columnspan=4, sticky="ew", padx=2, pady=(5, 18))
            welcome.configure(height=245)
            welcome.pack_propagate(False)
            ctk.CTkLabel(welcome, text="✦", text_color=PURPLE, font=ctk.CTkFont(size=43)).pack(pady=(36, 7))
            ctk.CTkLabel(welcome, text="Give your files a little breathing room.", text_color=TEXT, font=ctk.CTkFont(size=22, weight="bold")).pack()
            ctk.CTkLabel(welcome, text="Choose a folder to scan, preview file categories, and organize safely.", text_color=MUTED, font=ctk.CTkFont(size=12)).pack(pady=(8, 18))
            ctk.CTkButton(welcome, text="Choose a folder", command=self.choose_folder, height=42, width=190, corner_radius=12, fg_color=PURPLE, hover_color=PURPLE_HOVER).pack()
            self._quick_features(content, row=1)
            return

        rows = self._scan()
        total_size = sum(x["size"] for x in rows)
        categories = Counter(x["category"] for x in rows)
        self._stat_card(content, "TOTAL FILES", str(len(rows)), "Files in selected folder", "▤", PURPLE).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "FOLDER SIZE", self._format_size(total_size), "Combined file size", "◫", BLUE).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "CATEGORIES", str(len(categories)), "File types detected", "▦", GREEN).grid(row=0, column=2, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "READY TO SORT", str(len(rows)), "Top-level files scanned", "✦", ORANGE).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        cat_card = self._card(content, "File categories", "How your files are distributed")
        cat_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(14, 5))
        for category, count in categories.most_common(8):
            self._category_row(cat_card, category, count, len(rows))
        if not categories:
            ctk.CTkLabel(cat_card, text="No files found in this folder.", text_color=MUTED).pack(anchor="w", padx=18, pady=18)

        actions = self._card(content, "Quick actions", "Common tasks, one click away")
        actions.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=5, pady=(14, 5))
        self._action_button(actions, "▤", "Preview organization", "Review where files will go", lambda: self.show_page("Smart Organizer"))
        self._action_button(actions, "▥", "Analyze storage", "Explore folder size and categories", lambda: self.show_page("Storage Analyzer"))
        self._action_button(actions, "◷", "Activity history", "Review recent operations", lambda: self.show_page("Activity History"))

        recent = self._card(content, "Files in this folder", f"Showing up to 8 of {len(rows)} files")
        recent.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=(14, 5))
        self._file_table(recent, rows[:8])

    def _quick_features(self, parent, row):
        features = [
            ("▤", "Smart organization", "Sort files into useful categories.", PURPLE),
            ("▥", "Storage insights", "Understand what occupies your space.", BLUE),
            ("↶", "Safer workflow", "Preview before moving your files.", GREEN),
        ]
        for col, (glyph, title, desc, accent) in enumerate(features):
            card = self._card(parent)
            card.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
            ctk.CTkLabel(card, text=glyph, text_color=accent, font=ctk.CTkFont(size=24)).pack(anchor="w", padx=17, pady=(16, 5))
            ctk.CTkLabel(card, text=title, text_color=TEXT, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=17)
            ctk.CTkLabel(card, text=desc, text_color=MUTED, font=ctk.CTkFont(size=10), wraplength=230).pack(anchor="w", padx=17, pady=(5, 16))

    def _category_row(self, parent, category, count, total):
        glyph, accent = CATEGORY_META.get(category, ("•", MUTED))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=17, pady=7)
        ctk.CTkLabel(row, text=glyph, width=28, text_color=accent, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkLabel(row, text=category, text_color=TEXT, font=ctk.CTkFont(size=11)).pack(side="left", padx=7)
        ctk.CTkLabel(row, text=str(count), text_color=MUTED, font=ctk.CTkFont(size=10)).pack(side="right")
        bar_bg = ctk.CTkFrame(parent, height=5, fg_color="#2B2E3D", corner_radius=5)
        bar_bg.pack(fill="x", padx=52, pady=(0, 3))
        bar_bg.pack_propagate(False)
        fill = ctk.CTkFrame(bar_bg, height=5, fg_color=accent, corner_radius=5)
        fill.place(relx=0, rely=0, relwidth=max(.015, count / max(total, 1)), relheight=1)

    def _action_button(self, parent, glyph, title, desc, command):
        row = ctk.CTkFrame(parent, fg_color="#1D2030", corner_radius=11)
        row.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(row, text=glyph, text_color="#C5A5FF", width=38, font=ctk.CTkFont(size=19)).pack(side="left", padx=(9, 2), pady=10)
        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="left", fill="x", expand=True, pady=8)
        ctk.CTkLabel(text_box, text=title, text_color=TEXT, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(text_box, text=desc, text_color=MUTED, font=ctk.CTkFont(size=9)).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(row, text="Open  ›", width=75, height=30, corner_radius=8, fg_color="#302346", hover_color="#46305F", text_color="#D5BFFF", command=command).pack(side="right", padx=10)

    # ------------------------------ organizer -------------------------------

    def _organizer_page(self):
        self._header("Smart Organizer", "Preview every change before files are moved.", "＋  Choose folder", self.choose_folder)
        content = self._content()
        if not self.selected_folder:
            self._empty_state(content, "Choose a folder to get started", "The organizer scans files and suggests a category for each one.", self.choose_folder)
            return
        rows = self._scan()
        self.preview_items = rows
        summary = self._card(content)
        summary.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        top = ctk.CTkFrame(summary, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=15)
        ctk.CTkFrame(top, width=9, height=9, fg_color=GREEN, corner_radius=5).pack(side="left", padx=(0, 9))
        ctk.CTkLabel(top, text=f"SCAN COMPLETE  ·  {len(rows)} FILES FOUND", text_color=TEXT, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkLabel(summary, text=str(self.selected_folder), text_color=MUTED, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=18, pady=(0, 14))

        table = self._card(content, "Organization preview", "Nothing moves until you confirm.")
        table.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=10)
        self._file_table(table, rows, show_status=True, max_rows=200)
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=8)
        ctk.CTkLabel(bottom, text="Review the categories above. Existing category folders are left untouched.", text_color=MUTED, font=ctk.CTkFont(size=10)).pack(side="left")
        ctk.CTkButton(bottom, text="Organize files  →", command=self.organize_confirm, height=42, width=170, corner_radius=11, fg_color=PURPLE, hover_color=PURPLE_HOVER, font=ctk.CTkFont(size=12, weight="bold"), state="normal" if rows else "disabled").pack(side="right")

    def _file_table(self, parent, rows, show_status=False, max_rows=100):
        header = ctk.CTkFrame(parent, fg_color="#202333", corner_radius=8)
        header.pack(fill="x", padx=14, pady=(10, 4))
        cols = [("FILE NAME", .47), ("CATEGORY", .25), ("SIZE", .15), ("STATUS" if show_status else "TYPE", .13)]
        for title, width in cols:
            ctk.CTkLabel(header, text=title, text_color=MUTED, font=ctk.CTkFont(size=9, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True, padx=10, pady=10)
        for item in rows[:max_rows]:
            line = ctk.CTkFrame(parent, fg_color="transparent")
            line.pack(fill="x", padx=14, pady=1)
            glyph, accent = CATEGORY_META.get(item["category"], ("•", MUTED))
            ctk.CTkLabel(line, text=item["name"], text_color=TEXT, font=ctk.CTkFont(size=10), anchor="w").pack(side="left", fill="x", expand=True, padx=10, pady=9)
            ctk.CTkLabel(line, text=f"{glyph}  {item['category']}", text_color=accent, font=ctk.CTkFont(size=10), anchor="w").pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkLabel(line, text=self._format_size(item["size"]), text_color=MUTED, font=ctk.CTkFont(size=10), anchor="w").pack(side="left", fill="x", expand=True, padx=10)
            final = "Ready" if show_status else Path(item["name"]).suffix.lower() or "—"
            ctk.CTkLabel(line, text=final, text_color=GREEN if show_status else MUTED, font=ctk.CTkFont(size=10), anchor="w").pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkFrame(parent, height=1, fg_color="#252838").pack(fill="x", padx=15)
        if len(rows) > max_rows:
            ctk.CTkLabel(parent, text=f"Showing first {max_rows} files.", text_color=MUTED, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=20, pady=8)

    def organize_confirm(self):
        if not self.selected_folder:
            return
        count = len(self.preview_items)
        if count == 0:
            return
        ok = messagebox.askyesno(
            "Confirm organization",
            f"Move {count} files into category folders inside:\n\n{self.selected_folder}\n\nThis changes the selected folder. Continue?",
            icon="warning",
        )
        if not ok:
            return
        result = self.organizer.organize_folder(self.selected_folder)
        self.last_result = result
        messagebox.showinfo(
            "Organization complete",
            f"Files moved: {result.get('moved', 0)}\nFiles failed: {result.get('failed', 0)}",
        )
        self.show_page("Overview")

    # ------------------------------- explorer --------------------------------

    def _explorer_page(self):
        self._header("File Explorer", "Browse files in the folder you selected.", "＋  Choose folder", self.choose_folder)
        content = self._content()
        if not self.selected_folder:
            self._empty_state(content, "No folder selected", "Choose a folder to browse its files.", self.choose_folder)
            return
        search = ctk.CTkEntry(content, textvariable=self.search_var, placeholder_text="Search by file name or category...", height=40, corner_radius=10, fg_color=PANEL, border_color=BORDER)
        search.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=(5, 12))
        rows = self._scan()
        table = self._card(content, "Folder contents", f"{len(rows)} files · {self.selected_folder}")
        table.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self._file_table(table, rows, max_rows=500)
        search.bind("<KeyRelease>", lambda _e: self._filter_explorer(table))

    def _filter_explorer(self, table):
        # Refresh the explorer with the current search string.
        for child in table.winfo_children():
            child.destroy()
        query = self.search_var.get().lower().strip()
        rows = [r for r in self._scan() if query in r["name"].lower() or query in r["category"].lower()]
        ctk.CTkLabel(table, text=f"{len(rows)} matching files", text_color=MUTED, font=ctk.CTkFont(size=10)).pack(anchor="w", padx=18, pady=(10, 0))
        self._file_table(table, rows, max_rows=500)

    # ------------------------------- storage ---------------------------------

    def _storage_page(self):
        self._header("Storage Analyzer", "Understand the size and composition of your selected folder.", "＋  Choose folder", self.choose_folder)
        content = self._content()
        if not self.selected_folder:
            self._empty_state(content, "Select a folder to analyze", "We'll calculate file sizes and show a category breakdown.", self.choose_folder)
            return
        rows = self._scan()
        by_category = Counter()
        for item in rows:
            by_category[item["category"]] += item["size"]
        total = sum(by_category.values())
        self._stat_card(content, "TOTAL SIZE", self._format_size(total), "Combined size of scanned files", "◫", BLUE).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "FILES", str(len(rows)), "Top-level files", "▤", PURPLE).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "LARGEST CATEGORY", max(by_category, key=by_category.get) if by_category else "—", "By total file size", "▦", GREEN).grid(row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=5)
        card = self._card(content, "Storage by category", "Relative usage based on file size")
        card.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=14)
        for category, size in by_category.most_common():
            glyph, accent = CATEGORY_META.get(category, ("•", MUTED))
            line = ctk.CTkFrame(card, fg_color="transparent")
            line.pack(fill="x", padx=18, pady=(12, 2))
            ctk.CTkLabel(line, text=f"{glyph}  {category}", text_color=TEXT, font=ctk.CTkFont(size=11)).pack(side="left")
            ctk.CTkLabel(line, text=f"{self._format_size(size)}  ·  {size / total * 100:.1f}%" if total else self._format_size(size), text_color=MUTED, font=ctk.CTkFont(size=10)).pack(side="right")
            bar = ctk.CTkFrame(card, height=8, fg_color="#2B2E3D", corner_radius=5)
            bar.pack(fill="x", padx=18, pady=(5, 8))
            bar.pack_propagate(False)
            fill = ctk.CTkFrame(bar, fg_color=accent, corner_radius=5)
            fill.place(relx=0, rely=0, relwidth=size / total if total else 0, relheight=1)

    # -------------------------------- history --------------------------------

    def _history_page(self):
        self._header("Activity History", "A summary of the latest organization operation.")
        content = self._content()
        result = self.last_result
        if not result:
            self._empty_state(content, "No activity yet", "Your completed organization summary will appear here.")
            return
        card = self._card(content, "Latest operation", "Result from your most recent organization")
        card.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self._stat_card(content, "FILES MOVED", str(result.get("moved", 0)), "Successfully organized", "✓", GREEN).grid(row=1, column=0, sticky="ew", padx=5, pady=10)
        self._stat_card(content, "FAILED", str(result.get("failed", 0)), "Could not be moved", "!", RED).grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        details = result.get("details", [])
        if details:
            detail_card = self._card(content, "Operation details", f"{len(details)} files processed")
            detail_card.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
            for item in details[:100]:
                line = ctk.CTkFrame(detail_card, fg_color="transparent")
                line.pack(fill="x", padx=18, pady=5)
                ctk.CTkLabel(line, text=item.get("name", "File"), text_color=TEXT, font=ctk.CTkFont(size=10)).pack(side="left")
                ctk.CTkLabel(line, text=item.get("category", "—"), text_color=MUTED, font=ctk.CTkFont(size=10)).pack(side="right")

    # ------------------------------ utilities --------------------------------

    def _empty_state(self, parent, title, desc, command=None):
        card = self._card(parent)
        card.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(card, text="▤", text_color=PURPLE, font=ctk.CTkFont(size=38)).pack(pady=(36, 8))
        ctk.CTkLabel(card, text=title, text_color=TEXT, font=ctk.CTkFont(size=19, weight="bold")).pack()
        ctk.CTkLabel(card, text=desc, text_color=MUTED, font=ctk.CTkFont(size=11)).pack(pady=(7, 18))
        if command:
            ctk.CTkButton(card, text="Choose a folder", command=command, height=40, width=170, corner_radius=10, fg_color=PURPLE, hover_color=PURPLE_HOVER).pack(pady=(0, 30))
        else:
            ctk.CTkLabel(card, text="Select a folder to populate this workspace.", text_color=MUTED, font=ctk.CTkFont(size=10)).pack(pady=(0, 35))

