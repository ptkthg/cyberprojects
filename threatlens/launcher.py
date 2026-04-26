from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

APP_URL = "http://localhost:8501"


class ThreatLensLauncher:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ThreatLens Launcher")
        self.root.geometry("460x320")
        self.root.configure(bg="#0b1220")
        self.process: subprocess.Popen | None = None

        title = tk.Label(root, text="ThreatLens Launcher", bg="#0b1220", fg="#e2e8f0", font=("Segoe UI", 16, "bold"))
        title.pack(pady=(18, 6))
        author = tk.Label(root, text="Desenvolvido por Patrick Santos", bg="#0b1220", fg="#7dd3fc")
        author.pack(pady=(0, 12))

        frame = tk.Frame(root, bg="#0b1220")
        frame.pack(fill="x", padx=24)

        ttk.Button(frame, text="Iniciar ThreatLens", command=self.start_threatlens).pack(fill="x", pady=5)
        ttk.Button(frame, text="Abrir no navegador", command=self.open_browser).pack(fill="x", pady=5)
        ttk.Button(frame, text="Parar ThreatLens", command=self.stop_threatlens).pack(fill="x", pady=5)
        ttk.Button(frame, text="Sair", command=self.exit_app).pack(fill="x", pady=5)

        self.status_var = tk.StringVar(value="Status: Parado")
        status = tk.Label(root, textvariable=self.status_var, bg="#0b1220", fg="#bae6fd", font=("Consolas", 11))
        status.pack(pady=18)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def start_threatlens(self) -> None:
        if self.process and self.process.poll() is None:
            self.status_var.set(f"Status: Rodando em {APP_URL}")
            return

        app_path = os.path.join(os.getcwd(), "app.py")
        if not os.path.exists(app_path):
            self.status_var.set("Status: Erro ao iniciar")
            messagebox.showerror("Erro", "app.py não encontrado na pasta atual.")
            return

        self.status_var.set("Status: Iniciando")
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.root.after(2200, self.open_browser)
            self.status_var.set(f"Status: Rodando em {APP_URL}")
        except FileNotFoundError:
            self.status_var.set("Status: Erro ao iniciar")
            messagebox.showerror("Erro", "Streamlit não encontrado. Instale as dependências primeiro.")
        except Exception as exc:
            self.status_var.set("Status: Erro ao iniciar")
            messagebox.showerror("Erro", f"Falha ao iniciar: {exc}")

    def open_browser(self) -> None:
        webbrowser.open(APP_URL)

    def stop_threatlens(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.status_var.set("Status: Parado")
        else:
            self.status_var.set("Status: Parado")

    def exit_app(self) -> None:
        self.stop_threatlens()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ThreatLensLauncher(root)
    root.mainloop()
