"""Tkinter front end for a de-nest job.

This module is UI wiring only: it collects three paths, runs
:func:`app.denest.job.run_job` on a worker thread, and shows its log. All
behaviour worth testing lives in the other ``app.denest`` modules. It is
excluded from coverage (see ``pyproject.toml``) because Tk needs a display,
which CI does not have.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from app.denest.job import run_job

TITLE = "S4P De-nester"
DEFAULT_OUTPUT_FOLDER = "renamed_s4p"
POLL_MS = 100

INTRO = (
    "Copies nested S4P files into one folder as "
    "<switch/GPU>_Leg_<legLocation>_<original filename>.s4p, "
    "then writes a leg map containing only those serials. "
    "A serial with more than one S4P file gets one row per file."
)


class App(tk.Tk):
    """Main window: three path pickers, a Run button, and a log."""

    def __init__(self) -> None:
        super().__init__()
        self.title(TITLE)
        self.geometry("860x560")
        self.minsize(720, 480)
        # Messages from the worker thread: ("log" | "done" | "error", text).
        self._messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self._worker: threading.Thread | None = None

        self.legmap_var = tk.StringVar()
        self.root_var = tk.StringVar()
        self.output_var = tk.StringVar()

        self._build()
        self.after(POLL_MS, self._drain_messages)

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=INTRO, wraplength=820, justify=tk.LEFT).grid(
            row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10)
        )

        self._path_row(frame, 1, "Leg map CSV", self.legmap_var, self._browse_legmap)
        self._path_row(frame, 2, "S4P root folder", self.root_var, self._browse_root)
        self._path_row(frame, 3, "Output folder", self.output_var, self._browse_output)

        self.run_button = ttk.Button(frame, text="Run", command=self._start)
        self.run_button.grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 8))

        self.log = tk.Text(frame, height=18, wrap=tk.WORD, state=tk.DISABLED)
        self.log.grid(row=5, column=0, columnspan=3, sticky="nsew")
        frame.rowconfigure(5, weight=1)
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.log.yview)
        scroll.grid(row=5, column=3, sticky="ns")
        self.log.configure(yscrollcommand=scroll.set)

    def _path_row(
        self,
        frame: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        browse: Callable[[], None],
    ) -> None:
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        ttk.Button(frame, text="Browse", command=browse).grid(row=row, column=2, pady=3)

    def _browse_legmap(self) -> None:
        current = self.legmap_var.get().strip()
        selected = filedialog.askopenfilename(
            title="Select leg map CSV",
            initialdir=str(Path(current).parent) if current else "",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if selected:
            self.legmap_var.set(selected)

    def _browse_root(self) -> None:
        selected = filedialog.askdirectory(
            title="Select S4P root folder", initialdir=self.root_var.get().strip()
        )
        if selected:
            self.root_var.set(selected)
            if not self.output_var.get():
                self.output_var.set(str(Path(selected) / DEFAULT_OUTPUT_FOLDER))

    def _browse_output(self) -> None:
        initial = self.output_var.get().strip() or self.root_var.get().strip()
        selected = filedialog.askdirectory(title="Select output folder", initialdir=initial)
        if selected:
            self.output_var.set(selected)

    def _set_log(self, text: str, *, append: bool) -> None:
        self.log.configure(state=tk.NORMAL)
        if not append:
            self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, text)
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _drain_messages(self) -> None:
        try:
            while True:
                kind, text = self._messages.get_nowait()
                if kind == "log":
                    self._set_log(text + "\n", append=True)
                elif kind == "done":
                    self.run_button.configure(state=tk.NORMAL)
                    messagebox.showinfo(TITLE, text)
                elif kind == "error":
                    self.run_button.configure(state=tk.NORMAL)
                    self._set_log(f"Error: {text}\n", append=True)
                    messagebox.showerror(TITLE, text)
        except queue.Empty:
            pass
        self.after(POLL_MS, self._drain_messages)

    def _start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        values = (self.legmap_var.get(), self.root_var.get(), self.output_var.get())
        legmap, root, output = (value.strip() for value in values)
        if not (legmap and root and output):
            messagebox.showerror(
                TITLE, "Select a leg map CSV, an S4P root folder and an output folder."
            )
            return

        self._set_log("", append=False)
        self.run_button.configure(state=tk.DISABLED)

        def log(message: str) -> None:
            self._messages.put(("log", message))

        def work() -> None:
            try:
                summary = run_job(Path(legmap), Path(root), Path(output), log)
            except Exception as exc:  # report anything to the user rather than die silently
                self._messages.put(("error", str(exc)))
            else:
                self._messages.put(("done", summary.describe()))

        self._worker = threading.Thread(target=work, daemon=True)
        self._worker.start()


def launch() -> None:
    """Open the main window and block until it is closed."""
    App().mainloop()
