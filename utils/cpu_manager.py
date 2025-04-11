import psutil
import os

class CPUInfo:
    def __init__(self):
        pass

    def get_gpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_cpu_temperature(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
                temp_str = file.read().strip()
                temperature_celsius = int(temp_str) / 1000.0
                return temperature_celsius
        except FileNotFoundError:
            return None
        except ValueError:
            return None