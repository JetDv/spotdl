"""Shared GUI implementation for the SpotDL downloader."""

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import ttk

from .core import download, init_spotdl_client
from .types import DownloadOption, DownloadRequest


class StringVarCompat:
    def __init__(self, value: str = ""):
        self._value = value

    def set(self, value: str):
        self._value = value

    def get(self) -> str:
        return self._value


class DummyWidget:
    def grid(self, *args, **kwargs):
        pass

    def pack(self, *args, **kwargs):
        pass

    def config(self, *args, **kwargs):
        pass

    def grid_forget(self, *args, **kwargs):
        pass


class SpotdlDownloaderUI:
    def __init__(self):
        self._headless = False
        self._root = None

        try:
            self._root = tk.Tk()
        except tk.TclError:
            self._headless = True
            self._root = None

        if self._root is not None:
            self._root.title("SpotDL YouTube MP3 Puller")
            self._root.geometry("620x260")
            self._root.resizable(False, False)

        self._state = {
            "option_var": StringVarCompat(value=DownloadOption.ONE_SONG.value)
            if self._headless
            else tk.StringVar(value=DownloadOption.ONE_SONG.value),
            "source_var": StringVarCompat() if self._headless else tk.StringVar(),
            "file_path_var": StringVarCompat() if self._headless else tk.StringVar(),
            "status_var": StringVarCompat(value="Select an option to begin.")
            if self._headless
            else tk.StringVar(value="Select an option to begin."),
        }
        self._widgets = {}

        self.init_spotdl()
        self.create_widgets()
        self.update_input_controls()

    def init_spotdl(self):
        try:
            init_spotdl_client()
        except Exception as exc:
            if self._headless:
                print(f"Spotify Client Initialization warning: {exc}")
            else:
                messagebox.showwarning(
                    "Spotify Client Initialization",
                    f"Could not initialize Spotify client: {exc}",
                )

    def create_widgets(self):
        if self._headless:
            self._widgets["input_frame"] = DummyWidget()
            self._widgets["single_input_label"] = DummyWidget()
            self._widgets["single_input_entry"] = DummyWidget()
            self._widgets["file_input_label"] = DummyWidget()
            self._widgets["file_input_entry"] = DummyWidget()
            self._widgets["browse_button"] = DummyWidget()
            self._widgets["download_button"] = DummyWidget()
            self._widgets["status_label"] = DummyWidget()
            return

        container = ttk.Frame(self._root, padding=16)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="Download type:", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        radio_frame = ttk.Frame(container)
        radio_frame.pack(anchor="w", pady=(8, 12), fill="x")

        for option in DownloadOption:
            ttk.Radiobutton(
                radio_frame,
                text=option.value.title(),
                variable=self._state["option_var"],
                value=option.value,
                command=self.update_input_controls,
            ).pack(side="left", padx=(0, 12))

        self._widgets["input_frame"] = ttk.Frame(container)
        self._widgets["input_frame"].pack(fill="x")

        self._widgets["single_input_label"] = ttk.Label(self._widgets["input_frame"], text="Spotify URL:")
        self._widgets["single_input_entry"] = ttk.Entry(
            self._widgets["input_frame"], textvariable=self._state["source_var"], width=72
        )

        self._widgets["file_input_label"] = ttk.Label(self._widgets["input_frame"], text="JSON file:")
        self._widgets["file_input_entry"] = ttk.Entry(
            self._widgets["input_frame"],
            textvariable=self._state["file_path_var"],
            width=56,
            state="readonly",
        )
        self._widgets["browse_button"] = ttk.Button(
            self._widgets["input_frame"], text="Browse...", command=self.browse_json_file
        )

        action_frame = ttk.Frame(container)
        action_frame.pack(fill="x", pady=(16, 0))

        self._widgets["download_button"] = ttk.Button(
            action_frame, text="Download", command=self.on_download, width=14
        )
        self._widgets["download_button"].pack(side="right")

        self._widgets["status_label"] = ttk.Label(
            container,
            textvariable=self._state["status_var"],
            wraplength=580,
            foreground="gray25",
        )
        self._widgets["status_label"].pack(fill="x", pady=(16, 0))

    def update_input_controls(self):
        if self._headless:
            return

        for widget in self._widgets["input_frame"].winfo_children():
            widget.grid_forget()

        option = DownloadOption(self._state["option_var"].get())
        if option in (DownloadOption.ONE_SONG, DownloadOption.PLAYLIST):
            label_text = (
                "Spotify or YouTube song URL:"
                if option == DownloadOption.ONE_SONG
                else "Spotify playlist URL:"
            )
            self._widgets["single_input_label"].config(text=label_text)
            self._widgets["single_input_label"].grid(row=0, column=0, sticky="w")
            self._widgets["single_input_entry"].grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self._widgets["input_frame"].columnconfigure(0, weight=1)
            self.set_status("Enter the Spotify URL and press Download.")
        else:
            self._widgets["file_input_label"].grid(row=0, column=0, sticky="w")
            self._widgets["file_input_entry"].grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self._widgets["browse_button"].grid(row=1, column=1, padx=(10, 0), pady=(4, 0))
            self._widgets["input_frame"].columnconfigure(0, weight=1)
            self.set_status("Select a JSON file containing song definitions and press Download.")

    def browse_json_file(self):
        path = filedialog.askopenfilename(
            title="Choose songs JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*")],
            initialdir=Path.cwd(),
        )
        if path:
            self._state["file_path_var"].set(path)
            self.set_status(f"Selected JSON file: {Path(path).name}")

    def on_download(self):
        option = DownloadOption(self._state["option_var"].get())
        source = None

        if option in (DownloadOption.ONE_SONG, DownloadOption.PLAYLIST):
            source = self._state["source_var"].get().strip()
            if not source:
                self.set_status("Please enter a Spotify URL before downloading.", error=True)
                return
        else:
            source = self._state["file_path_var"].get().strip()
            if not source:
                self.set_status("Please select a JSON file before downloading.", error=True)
                return

        request = DownloadRequest(option=option, source=source)
        self._widgets["download_button"].config(state="disabled")
        self.set_status("Starting download... This may take a few minutes.")

        thread = threading.Thread(
            target=self.download_in_background, args=(request,), daemon=True
        )
        thread.start()

    def download_in_background(self, request: DownloadRequest):
        try:
            success = download(request)
            if success:
                self.set_status("Download finished successfully.")
            else:
                self.set_status("Download failed. Check the console for details.", error=True)
        except Exception as exc:
            self.set_status(f"Download error: {exc}", error=True)
        finally:
            self.after(0, lambda: self._widgets["download_button"].config(state="normal"))

    def set_status(self, message: str, error: bool = False):
        self._state["status_var"].set(message)
        if not self._headless:
            self.after(0, lambda: self._widgets["status_label"].config(foreground="red" if error else "gray25"))

    def after(self, delay, callback=None):
        if callback:
            callback()

    def withdraw(self):
        if self._root is not None:
            self._root.withdraw()

    def mainloop(self):
        if self._root is not None:
            self._root.mainloop()


if __name__ == "__main__":
    app = SpotdlDownloaderUI()
    app.mainloop()
