import asyncio
import threading
from queue import Queue
import tkinter as tk
from tkinter import ttk
import tempfile
import os

from pybricksdev.ble import find_device
from pybricksdev.connections.pybricks import PybricksHubBLE


# ---------------------------------------------------------
# TEXTO DESCRIPTIVO DE COMANDOS
# ---------------------------------------------------------
def comando_a_texto(cmd: str) -> str:
    textos = {
        "inicio": "Posición Inicial",
        "verde": "Clasificado → Verde",
        "azul": "Clasificado → Azul",
        "rojo": "Clasificado → Rojo",
        "amarillo": "Clasificado → Amarillo",
        "clasificar": "Clasificación automática continua",
        "empujar": "Empujar bloque",
        "tirar": "Abrir garra",
    }
    return textos.get(cmd, "Comando ejecutado")


# ---------------------------------------------------------
# PROGRAMA PYBRICKS QUE SE ENVÍA AL HUB
# ---------------------------------------------------------
def create_program(cmd: str) -> str:

    # ----- CLASIFICACIÓN AUTOMÁTICA CONTINUA -----
    if cmd == "clasificar":
        return """
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

hub = PrimeHub()

motorE = Motor(Port.E)   # Movimiento
motorF = Motor(Port.F)   # Garra
sensor = ColorSensor(Port.C)

motorF.control.limits(speed=300, acceleration=800)

while True:

    color = sensor.color()

    # ⛔ DETENER SI ES BLANCO
    if color == Color.WHITE:
        hub.light.on(Color.WHITE)
        wait(500)
        break

    if color == Color.GREEN:
        motorE.run_target(300, -45)
    elif color == Color.BLUE:
        motorE.run_target(300, -70)
    elif color == Color.RED:
        motorE.run_target(300, 90)
    elif color == Color.YELLOW:
        motorE.run_target(300, 125)
    else:
        wait(300)
        continue

    wait(200)

    # 🔓 ABRIR GARRA
    motorF.run_angle(300, -40)
    wait(200)

    # 👉 EMPUJAR BLOQUE
    motorF.run_angle(300, 40)
    wait(200)

    # 🏠 VOLVER A INICIO
    motorE.run_target(300, 0)
    wait(500)
"""

    # ----- COMANDOS MANUALES -----
    acciones = {
        "inicio": "motorE.run_target(100, 0)",
        "verde": "motorE.run_target(100, -45)",
        "azul": "motorE.run_target(100, -70)",
        "rojo": "motorE.run_target(100, 90)",
        "amarillo": "motorE.run_target(100, 125)",
        "empujar": "motorF.run_angle(100, 40)",
        "tirar": "motorF.run_angle(100, -40)",
    }

    return f"""
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait

hub = PrimeHub()

motorE = Motor(Port.E)
motorF = Motor(Port.F)

motorF.control.limits(speed=300, acceleration=800)

{acciones.get(cmd, "")}

wait(100)
"""


# ---------------------------------------------------------
# EJECUCIÓN DEL COMANDO EN EL HUB
# ---------------------------------------------------------
async def execute_command(hub, cmd, log):
    program = create_program(cmd)

    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
            f.write(program.encode("utf-8"))
            path = f.name

        log("📤 Enviando comando al hub...")
        await hub.run(path)
        log(f"✅ {comando_a_texto(cmd)}")

    except Exception as e:
        log(f"❌ Error: {e}")

    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------
# HILO BLE
# ---------------------------------------------------------
class BLEWorker:
    def __init__(self, log_queue: Queue):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._thread_main, daemon=True)
        self.queue = None
        self.hub = None
        self.log_queue = log_queue

    def log(self, msg):
        self.log_queue.put(msg)

    def _thread_main(self):
        asyncio.set_event_loop(self.loop)
        self.queue = asyncio.Queue()
        self.loop.create_task(self._runner())
        self.loop.run_forever()

    async def _runner(self):
        try:
            self.log("🔍 Buscando hub SP-7...")
            device = await find_device(name="SP-7")
            if not device:
                self.log("❌ No se encontró el hub.")
                return

            self.hub = PybricksHubBLE(device)
            await self.hub.connect()
            self.log("🔗 Conectado al hub SP-7")

            while True:
                cmd = await self.queue.get()
                await execute_command(self.hub, cmd, self.log)

        except Exception as e:
            self.log(f"❌ Error BLE: {e}")

        finally:
            if self.hub:
                await self.hub.disconnect()
                self.log("🔌 Hub desconectado")

    def start(self):
        if not self.thread.is_alive():
            self.thread.start()

    def stop(self):
        if self.loop.is_running():
            for task in asyncio.all_tasks(self.loop):
                task.cancel()
            self.loop.call_soon_threadsafe(self.loop.stop)

    def send_command(self, cmd: str):
        if self.queue:
            self.loop.call_soon_threadsafe(self.queue.put_nowait, cmd)


# ---------------------------------------------------------
# INTERFAZ GRÁFICA
# ---------------------------------------------------------
def main_gui():
    root = tk.Tk()
    root.title("Clasificador Automático - SP-7")
    root.geometry("420x600")

    log_queue = Queue()
    worker = BLEWorker(log_queue)
    worker.start()

    frame_log = ttk.LabelFrame(root, text="Estado")
    frame_log.pack(fill="both", padx=10, pady=10)

    txt = tk.Text(frame_log, height=12, state="disabled")
    txt.pack(fill="both", padx=5, pady=5)

    def update_logs():
        while not log_queue.empty():
            msg = log_queue.get()
            txt.config(state="normal")
            txt.insert("end", msg + "\n")
            txt.see("end")
            txt.config(state="disabled")
        root.after(100, update_logs)

    update_logs()

    frame_ctrl = ttk.LabelFrame(root, text="Control")
    frame_ctrl.pack(fill="both", padx=10, pady=10)

    ttk.Button(frame_ctrl, text="🏠 Inicio",
               command=lambda: worker.send_command("inicio")).pack(fill="x", pady=4)

    ttk.Button(frame_ctrl, text="🎨 Clasificación automática (continua)",
               command=lambda: worker.send_command("clasificar")).pack(fill="x", pady=6)

    ttk.Button(frame_ctrl, text="🟢 Verde",
               command=lambda: worker.send_command("verde")).pack(fill="x", pady=2)

    ttk.Button(frame_ctrl, text="🔵 Azul",
               command=lambda: worker.send_command("azul")).pack(fill="x", pady=2)

    ttk.Button(frame_ctrl, text="🔴 Rojo",
               command=lambda: worker.send_command("rojo")).pack(fill="x", pady=2)

    ttk.Button(frame_ctrl, text="🟡 Amarillo",
               command=lambda: worker.send_command("amarillo")).pack(fill="x", pady=2)

    ttk.Button(frame_ctrl, text="🔓 Abrir garra",
               command=lambda: worker.send_command("tirar")).pack(fill="x", pady=4)

    ttk.Button(frame_ctrl, text="➡ Empujar",
               command=lambda: worker.send_command("empujar")).pack(fill="x", pady=4)

    def on_close():
        worker.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    main_gui()
