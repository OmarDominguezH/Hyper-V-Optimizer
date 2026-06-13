# Hyper-V-Optimizer

Esta herramienta está diseñada para desactivar completamente las funciones de virtualización de Windows (Hyper-V, VBS, Device Guard) con el fin de maximizar el rendimiento en emuladores de terceros como BlueStacks, LDPlayer, NoxPlayer y software de virtualización como VMware o VirtualBox.

## 🚀 Cómo usarlo (Paso a paso)

1.  **Requisitos previos:**
    *   Tener instalado **Python 3.x**.
    *   Asegurarse de tener el archivo `hyperv.ico` en la misma carpeta si deseas ver el icono personalizado.
2.  **Ejecución:**
    *   Haz doble clic en el archivo `hyperv.pyw` (usar la extensión `.pyw` es clave para que no se abra una ventana negra de consola).
    *   El programa solicitará permisos de administrador automáticamente de forma silenciosa. Acepta el diálogo de Windows.
3.  **Interfaz:**
    *   Lee la descripción y las advertencias de seguridad.
    *   Haz clic en el botón **"OPTIMIZAR Y REINICIAR"**.
4.  **Proceso:**
    *   Verás una barra de progreso y un log en tiempo real indicando qué comando se está ejecutando.
5.  **Finalización:**
    *   Al terminar, el programa te preguntará si deseas reiniciar el equipo ahora. Se recomienda hacerlo para que los cambios en el cargador de arranque (BCD) surtan efecto.

---

## 🛠️ Cómo funciona el código

El script está construido utilizando Python y la librería gráfica Tkinter, con un enfoque en la ejecución silenciosa y privilegios elevados.

### 1. Gestión de Identidad y Privilegios
*   **`AppUserModelID`**: Se utiliza `ctypes` para asignar un ID de modelo de usuario de aplicación explícito. Esto evita que Windows agrupe el programa con el intérprete de Python en la barra de tareas.
*   **Auto-Elevación Silenciosa**: La función `is_admin()` verifica los permisos. Si no los tiene, usa `ShellExecuteW` con el parámetro `SW_HIDE (0)` para relanzar el script como administrador sin mostrar una ventana de consola intermedia.

### 2. Ejecución de Comandos Sin Ventanas (Modo Invisible)
Para evitar los "flashes" negros del CMD, todas las llamadas al sistema se realizan mediante `subprocess.run` con el flag:
`creationflags=subprocess.CREATE_NO_WINDOW`.
Esto asegura que comandos pesados de PowerShell o BCDedit se ejecuten totalmente en segundo plano.

### 3. Optimizaciones del Sistema
El programa ejecuta una secuencia de 5 comandos críticos:
*   **BCDedit**: Configura `hypervisorlaunchtype` en `off` para desactivar el hipervisor de Windows desde el arranque.
*   **PowerShell**: Deshabilita las características opcionales `VirtualMachinePlatform` y `Microsoft-Hyper-V-All`.
*   **Registro (Reg)**: 
    *   Desactiva **VBS** (Virtualization Based Security / Seguridad basada en virtualización).
    *   Ajusta **LSA** (Local Security Authority) para evitar conflictos de virtualización.

### 4. Persistencia e Inteligencia de Ejecución
La función `set_persistence()` crea una tarea programada en Windows (`schtasks`).
*   **Modo Híbrido**: El código detecta si se está ejecutando como un script `.py` o como un ejecutable `.exe` (usando `sys.frozen`).
*   **Modo Auto**: Si el sistema se reinicia y la tarea se dispara, el programa detecta el argumento `--auto` y ejecuta la optimización de forma invisible sin abrir la interfaz gráfica.

### 5. Multitarea (Threading)
Para que la interfaz de usuario (GUI) no se congele mientras se ejecutan los comandos de PowerShell (que pueden tardar varios segundos), el proceso de optimización se ejecuta en un hilo (`threading.Thread`) separado.

---

## ⚠️ Advertencias importantes
Al usar esta herramienta:
*   **WSL2 y Docker Desktop** dejarán de funcionar.
*   La **Integridad de Memoria** en la Seguridad de Windows se desactivará.
*   El **Sandbox de Windows** no podrá iniciarse.

*Desarrollado para optimización de alto rendimiento en Gaming y Emulación.*