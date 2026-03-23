"""
monitor.py
──────────
Utilitários compartilhados de coleta de métricas:
  - MonitorCPU   : coleta CPU% em thread de background (psutil)
  - medir_bloco  : envolve qualquer operação e retorna métricas
  - carregar_csv : leitura genérica de CSV para lista de dicts
  - imprimir_tabela : imprime tabela formatada com nomes legíveis
  - salvar_csv   : salva resultados em CSV
"""

import csv
import os
import statistics
import threading
import time
import tracemalloc

import psutil


# ─────────────────────────────────────────────
# NOMES LEGÍVEIS DAS MÉTRICAS
# Mapeamento de chave interna → nome para exibição
# ─────────────────────────────────────────────

NOMES_METRICAS = {
    # Inserção
    "ins_tempo_med":     "Tempo de Inserção (s)",
    "ins_tempo_std":     "Tempo de Inserção — Desvio (s)",
    "ins_mem_trace_kb":  "Memória Alocada na Inserção (KB)",
    "ins_mem_ram_kb":    "RAM Consumida na Inserção (KB)",
    "ins_cpu_media_pct": "CPU Médio na Inserção (%)",
    "ins_cpu_pico_pct":  "CPU Pico na Inserção (%)",
    "altura_media":      "Altura da Árvore",
    "altura_std":        "Altura da Árvore — Desvio",
    # Busca sequencial
    "seq_tempo_med":     "Tempo de Busca Sequencial (s)",
    "seq_tempo_std":     "Tempo de Busca Sequencial — Desvio (s)",
    "seq_iter_med":      "Comparações por Busca Sequencial",
    "seq_iter_std":      "Comparações por Busca Sequencial — Desvio",
    "seq_mem_trace_kb":  "Memória na Busca Sequencial (KB)",
    "seq_mem_ram_kb":    "RAM na Busca Sequencial (KB)",
    "seq_cpu_media_pct": "CPU Médio na Busca Sequencial (%)",
    "seq_cpu_pico_pct":  "CPU Pico na Busca Sequencial (%)",
    # Busca binária
    "bin_tempo_med":     "Tempo de Busca Binária (s)",
    "bin_tempo_std":     "Tempo de Busca Binária — Desvio (s)",
    "bin_t_ord_med":     "Tempo de Ordenação para Busca Binária (s)",
    "bin_iter_med":      "Comparações por Busca Binária",
    "bin_iter_std":      "Comparações por Busca Binária — Desvio",
    "bin_mem_trace_kb":  "Memória na Busca Binária (KB)",
    "bin_mem_ram_kb":    "RAM na Busca Binária (KB)",
    "bin_cpu_media_pct": "CPU Médio na Busca Binária (%)",
    "bin_cpu_pico_pct":  "CPU Pico na Busca Binária (%)",
    # Busca em árvore
    "bus_tempo_med":     "Tempo de Busca (s)",
    "bus_tempo_std":     "Tempo de Busca — Desvio (s)",
    "bus_iter_med":      "Comparações por Busca",
    "bus_iter_std":      "Comparações por Busca — Desvio",
    "bus_mem_trace_kb":  "Memória na Busca (KB)",
    "bus_mem_ram_kb":    "RAM na Busca (KB)",
    "bus_cpu_media_pct": "CPU Médio na Busca (%)",
    "bus_cpu_pico_pct":  "CPU Pico na Busca (%)",
}


# ─────────────────────────────────────────────
# MONITOR DE CPU EM BACKGROUND
# ─────────────────────────────────────────────

class MonitorCPU:
    """
    Coleta amostras de uso de CPU (%) em thread separada
    enquanto uma operação está sendo executada.
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
# MEDIÇÃO GENÉRICA
# ─────────────────────────────────────────────

def medir_bloco(fn, *args, **kwargs) -> tuple:
    """
    Executa fn(*args, **kwargs) e coleta tempo, memória e CPU.
    Retorna: (resultado_de_fn, dict_de_metricas)
    """
    processo  = psutil.Process(os.getpid())
    ram_antes = processo.memory_info().rss / 1024

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

    return resultado, {
        "tempo_s":       fim - inicio,
        "mem_trace_kb":  pico_trace / 1024,
        "mem_ram_kb":    ram_depois - ram_antes,
        "cpu_media_pct": cpu_media,
        "cpu_pico_pct":  cpu_pico,
    }


def medir_bloco_repetido(fn, repeticoes: int, *args, **kwargs) -> tuple:
    """
    Executa fn(*args, **kwargs) 'repeticoes' vezes dentro de um único
    bloco de medição de tempo, memória e CPU.
    Retorna: (resultado_da_ultima_chamada, dict_de_metricas)
    """
    processo  = psutil.Process(os.getpid())
    ram_antes = processo.memory_info().rss / 1024

    monitor = MonitorCPU()
    tracemalloc.start()
    monitor.iniciar()
    inicio = time.perf_counter()

    resultado = None
    for _ in range(repeticoes):
        resultado = fn(*args, **kwargs)

    fim = time.perf_counter()
    _, pico_trace = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cpu_media, cpu_pico = monitor.parar()

    ram_depois = processo.memory_info().rss / 1024

    return resultado, {
        "tempo_s":       fim - inicio,
        "mem_trace_kb":  pico_trace / 1024,
        "mem_ram_kb":    ram_depois - ram_antes,
        "cpu_media_pct": cpu_media,
        "cpu_pico_pct":  cpu_pico,
    }


# ─────────────────────────────────────────────
# IMPRESSÃO DE TABELA LEGÍVEL
# ─────────────────────────────────────────────

def imprimir_tabela(titulo: str, dados: dict, ignorar: set = None):
    """
    Imprime uma tabela formatada com nomes legíveis.
    'dados' é o dict de resultado de rodar_experimento().
    'ignorar' é um conjunto de chaves a não exibir (ex: {'N','estrutura'}).
    """
    ignorar = ignorar or {"N", "estrutura"}
    col_nome  = 42
    col_valor = 14

    sep = "─" * (col_nome + col_valor + 7)
    print(f"\n  {titulo}")
    print(f"  {sep}")
    print(f"  {'Métrica':<{col_nome}} {'Valor':>{col_valor}}")
    print(f"  {sep}")

    for chave, valor in dados.items():
        if chave in ignorar:
            continue
        nome = NOMES_METRICAS.get(chave, chave)
        # Detecta se é desvio (std) para exibir junto com a média
        if chave.endswith("_std"):
            continue  # desvio é exibido junto com a média abaixo
        # Busca o desvio correspondente
        chave_std = chave.replace("_med", "_std").replace("_media", "_std")
        std_val   = dados.get(chave_std)

        if isinstance(valor, float):
            if std_val is not None:
                print(f"  {nome:<{col_nome}} {valor:>{col_valor-8}.4f} ± {std_val:.4f}")
            else:
                print(f"  {nome:<{col_nome}} {valor:>{col_valor}.4f}")
        else:
            print(f"  {nome:<{col_nome}} {str(valor):>{col_valor}}")

    print(f"  {sep}")


# ─────────────────────────────────────────────
# LEITURA E ESCRITA DE CSV
# ─────────────────────────────────────────────

def carregar_csv(caminho: str) -> list[dict]:
    registros = []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append(row)
    return registros


def resumo_print(label: str, valores: list[float], fmt: str = ".4f"):
    """Imprime  label : média ± desvio_padrão (usado internamente)."""
    m = statistics.mean(valores)
    s = statistics.stdev(valores) if len(valores) > 1 else 0.0
    print(f"    {label:<32}: {m:{fmt}} ± {s:{fmt}}")


def salvar_csv(caminho: str, linhas: list[dict]):
    """Salva lista de dicts em CSV com cabeçalho de nomes legíveis."""
    if not linhas:
        return
    chaves_internas = list(linhas[0].keys())
    # Cabeçalho legível para o CSV
    cabecalho = {c: NOMES_METRICAS.get(c, c) for c in chaves_internas}

    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=chaves_internas)
        # Escreve cabeçalho com nomes legíveis
        f.write(",".join(cabecalho[c] for c in chaves_internas) + "\n")
        writer.writerows(linhas)