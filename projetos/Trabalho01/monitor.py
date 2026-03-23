import csv
import os
import statistics
import threading
import time
import tracemalloc

import psutil


# ─────────────────────────────────────────────
# MONITOR DE CPU EM BACKGROUND
# ─────────────────────────────────────────────

class MonitorCPU:
    """
    Coleta amostras de uso de CPU (%) em thread separada
    enquanto uma operação está sendo executada.

    Uso:
        monitor = MonitorCPU()
        monitor.iniciar()
        ... operação ...
        media, pico = monitor.parar()
    """

    def __init__(self, intervalo: float = 0.05):
        self.intervalo = intervalo
        self.amostras: list[float] = []
        self._rodando = False
        self._thread: threading.Thread | None = None

    def iniciar(self):
        self.amostras = []
        self._rodando = True
        self._thread = threading.Thread(target=self._coletar, daemon=True)
        self._thread.start()

    def _coletar(self):
        processo = psutil.Process(os.getpid())
        while self._rodando:
            self.amostras.append(processo.cpu_percent(interval=None))
            time.sleep(self.intervalo)

    def parar(self) -> tuple[float, float]:
        self._rodando = False
        if self._thread:
            self._thread.join()
        if not self.amostras:
            return 0.0, 0.0
        return statistics.mean(self.amostras), max(self.amostras)


# ─────────────────────────────────────────────
# MEDIÇÃO GENÉRICA DE UM BLOCO DE CÓDIGO
# ─────────────────────────────────────────────

def medir_bloco(fn, *args, **kwargs) -> tuple:
    """
    Executa fn(*args, **kwargs) e coleta:
      - tempo_s       : duração em segundos
      - mem_trace_kb  : pico de memória rastreada pelo tracemalloc (KB)
      - mem_ram_kb    : delta de RSS do processo (KB)
      - cpu_media_pct : uso médio de CPU durante a execução (%)
      - cpu_pico_pct  : pico de CPU durante a execução (%)

    Retorna: (resultado_de_fn, dict_de_metricas)
    """
    processo  = psutil.Process(os.getpid())
    ram_antes = processo.memory_info().rss / 1024  # KB

    monitor = MonitorCPU()
    tracemalloc.start()
    monitor.iniciar()
    inicio = time.perf_counter()

    resultado = fn(*args, **kwargs)

    fim = time.perf_counter()
    _, pico_trace = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cpu_media, cpu_pico = monitor.parar()

    ram_depois = processo.memory_info().rss / 1024
    delta_ram  = ram_depois - ram_antes

    metricas = {
        "tempo_s":       fim - inicio,
        "mem_trace_kb":  pico_trace / 1024,
        "mem_ram_kb":    delta_ram,
        "cpu_media_pct": cpu_media,
        "cpu_pico_pct":  cpu_pico,
    }
    return resultado, metricas


# ─────────────────────────────────────────────
# LEITURA DE CSV
# ─────────────────────────────────────────────

def carregar_csv(caminho: str) -> list[dict]:
    registros = []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append(row)
    return registros


# ─────────────────────────────────────────────
# IMPRESSÃO DE RESUMO
# ─────────────────────────────────────────────

def resumo_print(label: str, valores: list[float], fmt: str = ".4f"):
    """Imprime  label : média ± desvio_padrão."""
    m = statistics.mean(valores)
    s = statistics.stdev(valores) if len(valores) > 1 else 0.0
    print(f"    {label:<28}: {m:{fmt}} ± {s:{fmt}}")


def salvar_csv(caminho: str, linhas: list[dict]):
    """Salva lista de dicts em CSV."""
    if not linhas:
        return
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        writer.writeheader()
        writer.writerows(linhas)