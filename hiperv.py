import os
import sys
import ctypes
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_pc():
    """Reinicia la computadora inmediatamente."""
    try:
        subprocess.run("shutdown /r /t 5", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo reiniciar automáticamente: {e}")

def disable_hyperv_all_versions(log_widget, progress_bar, root, btn):
    sys32 = os.path.join(os.environ['SystemRoot'], 'System32')
    bcdedit = os.path.join(sys32, 'bcdedit.exe')
    powershell = os.path.join(sys32, 'WindowsPowerShell', 'v1.0', 'powershell.exe')
    reg = os.path.join(sys32, 'reg.exe')

    commands = [
        (f'{bcdedit} /set hypervisorlaunchtype off', "Desactivando Hipervisor (BCD)..."),
        (f'{powershell} -Command "Disable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart"', "Quitando VM Platform..."),
        (f'{powershell} -Command "Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart"', "Buscando Hyper-V..."),
        (f'{reg} add "HKLM\\System\\CurrentControlSet\\Control\\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 0 /f', "Desactivando VBS..."),
        (f'{reg} add "HKLM\\System\\CurrentControlSet\\Control\\Lsa" /v LsaCfgFlags /t REG_DWORD /d 0 /f', "Ajustando LSA...")
    ]
    
    total = len(commands)
    for i, (cmd, desc) in enumerate(commands):
        log_widget.insert(tk.END, f"• {desc}\n")
        log_widget.see(tk.END)
        subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Actualizar progreso
        val = ((i + 1) / total) * 100
        progress_bar['value'] = val
        root.update_idletasks()

    set_persistence()
    log_widget.insert(tk.END, "\n[✔] PROCESO FINALIZADO.")
    
    if messagebox.askyesno("Reinicio Requerido", "La optimización se aplicó con éxito.\n\n¿Desea REINICIAR el equipo ahora mismo? (Recomendado)"):
        restart_pc()
    else:
        btn.config(state="normal", text="REINICIAR MANUALMENTE", command=restart_pc)

def set_persistence():
    try:
        script_path = os.path.abspath(sys.argv[0])
        task_name = "StopHyperVAuto"
        sys32 = os.path.join(os.environ['SystemRoot'], 'System32')
        schtasks = os.path.join(sys32, 'schtasks.exe')
        cmd = f'{schtasks} /create /tn "{task_name}" /tr "pythonw.exe \'{script_path}\' --auto" /sc onlogon /rl highest /f'
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def show_warning_and_start(log_widget, progress_bar, btn, root):
    advertencia = (
        "⚠️ ADVERTENCIA DE SEGURIDAD ⚠️\n\n"
        "Este programa desactivará funciones de virtualización y seguridad del núcleo (VBS).\n\n"
        "EFECTOS SECUNDARIOS:\n"
        "• WSL2 (Linux) y Docker dejarán de funcionar.\n"
        "• El Sandbox de Windows será deshabilitado.\n"
        "• La 'Integridad de Memoria' en Seguridad de Windows se apagará.\n\n"
        "¿Desea continuar bajo su propia responsabilidad?"
    )
    if messagebox.askokcancel("Confirmar Optimización", advertencia):
        btn.config(state="disabled")
        thread = threading.Thread(target=disable_hyperv_all_versions, args=(log_widget, progress_bar, root, btn))
        thread.start()

# --- Lógica de Ejecución ---
if not is_admin():
    # Cambiamos el último parámetro de 1 a 0 (SW_HIDE) para que el proceso elevado no abra una consola.
    # También usamos sys.exit() para cerrar el proceso actual que no tiene permisos.
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
    sys.exit()
else:
    if "--auto" in sys.argv:
        sys32 = os.path.join(os.environ['SystemRoot'], 'System32')
        subprocess.run(f'{os.path.join(sys32, "bcdedit.exe")} /set hypervisorlaunchtype off', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit()

    root = tk.Tk()
    root.title("Hyper-V Killer & Optimizer")
    root.geometry("550x520")
    root.configure(bg="#ffffff")
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", thickness=10, background='#d32f2f')

    # Header
    header = tk.Frame(root, bg="#d32f2f", height=70)
    header.pack(fill="x")
    tk.Label(header, text="DESACTIVADOR DE VIRTUALIZACIÓN", fg="white", bg="#d32f2f", font=("Segoe UI", 12, "bold")).pack(pady=20)

    content = tk.Frame(root, bg="#ffffff", padx=30, pady=10)
    content.pack(fill="both", expand=True)

    # Descripción
    tk.Label(content, text="DESCRIPCIÓN:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(anchor="w")
    tk.Label(content, text="Esta herramienta apaga completamente el motor de Hyper-V y la Seguridad\nBasada en Virtualización (VBS) para permitir que emuladores como\nBlueStacks, LDPlayer o VMware funcionen a máxima velocidad.", 
             bg="#ffffff", justify="left", font=("Segoe UI", 9)).pack(pady=5, anchor="w")

    # Consola
    log_txt = tk.Text(content, height=8, font=("Consolas", 9), bg="#f8f9fa", fg="#212529", bd=1, relief="solid")
    log_txt.pack(fill="x", pady=10)

    progress = ttk.Progressbar(content, orient="horizontal", mode="determinate", style="TProgressbar")
    progress.pack(fill="x", pady=5)

    # Botón Principal
    btn_run = tk.Button(content, text="OPTIMIZAR Y REINICIAR", 
                        command=lambda: show_warning_and_start(log_txt, progress, btn_run, root),
                        bg="#d32f2f", fg="white", font=("Segoe UI", 11, "bold"), 
                        relief="flat", cursor="hand2", padx=20, pady=10)
    btn_run.pack(pady=15)

    tk.Label(root, text="El sistema se reiniciará para aplicar los cambios.", bg="#ffffff", fg="#cc0000", font=("Segoe UI", 8, "italic")).pack(pady=5)

    root.mainloop()