from __future__ import annotations

import os
import socket
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
        self.root.geometry("560x430")
        self.root.configure(bg="#0b1220")
        self.process: subprocess.Popen | None = None

        tk.Label(root, text="ThreatLens Launcher", bg="#0b1220", fg="#e2e8f0", font=("Segoe UI", 16, "bold")).pack(pady=(14, 4))
        tk.Label(root, text="Desenvolvido por Patrick Santos", bg="#0b1220", fg="#7dd3fc").pack(pady=(0, 8))
        tk.Label(root, text="LinkedIn: [INSERIR_LINK_LINKEDIN] | GitHub: [INSERIR_LINK_GITHUB]", bg="#0b1220", fg="#94a3b8", font=("Segoe UI", 9)).pack(pady=(0, 10))

        frame = tk.Frame(root, bg="#0b1220")
        frame.pack(fill="x", padx=24)

        ttk.Button(frame, text="Iniciar ThreatLens", command=self.start_threatlens).pack(fill="x", pady=4)
        ttk.Button(frame, text="Abrir no navegador", command=self.open_browser).pack(fill="x", pady=4)
        ttk.Button(frame, text="Parar ThreatLens", command=self.stop_threatlens).pack(fill="x", pady=4)
        ttk.Button(frame, text="Verificar ambiente", command=self.check_environment).pack(fill="x", pady=4)
        ttk.Button(frame, text="Sair", command=self.exit_app).pack(fill="x", pady=4)

        self.status_var = tk.StringVar(value="Status do servidor: Parado")
        tk.Label(root, textvariable=self.status_var, bg="#0b1220", fg="#bae6fd", font=("Consolas", 11)).pack(pady=(10, 6))

        tk.Label(root, text="Logs", bg="#0b1220", fg="#e2e8f0", anchor="w").pack(fill="x", padx=24)
        self.log = tk.Text(root, height=7, bg="#111827", fg="#cbd5e1")
        self.log.pack(fill="both", expand=True, padx=24, pady=(2, 16))
        self._log("Launcher iniciado.")

        self.root.after(1800, self.refresh_server_status)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _log(self, text: str) -> None:
        self.log.insert("end", f"- {text}\n")
        self.log.see("end")

    def _is_server_online(self) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", 8501), timeout=1):
                return True
        except OSError:
            return False

    def refresh_server_status(self) -> None:
        self.status_var.set(f"Status do servidor: {'Rodando em ' + APP_URL if self._is_server_online() else 'Parado'}")
        self.root.after(1800, self.refresh_server_status)

    def check_environment(self) -> None:
        app_path = os.path.join(os.getcwd(), "app.py")
        if not os.path.exists(app_path):
            messagebox.showerror("Ambiente", "app.py não encontrado na pasta atual.")
            self._log("Falha: app.py ausente.")
            return
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            msg = f"OK | Python {sys.version.split()[0]} | {result.stdout.strip()}"
            messagebox.showinfo("Ambiente", msg)
            self._log(msg)
        else:
            messagebox.showerror("Ambiente", "Streamlit não instalado neste ambiente.")
            self._log("Falha: streamlit não encontrado.")

    def start_threatlens(self) -> None:
        if self.process and self.process.poll() is None:
            self._log("Instância já em execução.")
            return
        if self._is_server_online():
            self._log("Servidor já ativo; evitando múltiplas instâncias.")
            self.open_browser()
            return

        app_path = os.path.join(os.getcwd(), "app.py")
        if not os.path.exists(app_path):
            self.status_var.set("Status do servidor: Erro ao iniciar")
            messagebox.showerror("Erro", "app.py não encontrado na pasta atual.")
            self._log("Erro: app.py ausente.")
            return

        try:
            self.status_var.set("Status do servidor: Iniciando")
            self.process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._log("Processo streamlit iniciado.")
            self.root.after(2200, self.open_browser)
        except Exception:
            self.status_var.set("Status do servidor: Erro ao iniciar")
            messagebox.showerror("Erro", "Falha ao iniciar. Verifique se Streamlit está instalado.")
            self._log("Erro ao iniciar streamlit.")

    def open_browser(self) -> None:
        webbrowser.open(APP_URL)
        self._log("Navegador aberto em http://localhost:8501")

    def stop_threatlens(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self._log("Processo streamlit encerrado.")
        else:
            self._log("Nenhum processo local para encerrar.")

    def exit_app(self) -> None:
        self.stop_threatlens()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    ThreatLensLauncher(root)
    root.mainloop()
