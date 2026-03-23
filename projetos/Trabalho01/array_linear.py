"""
array_linear.py
───────────────
Implementação do Array Linear e seu experimento comparativo entre
busca sequencial O(n) e busca binária O(log n).

Métricas coletadas por operação:
  - Tempo (s)
  - Memória tracemalloc (KB)
  - RAM delta psutil (KB)
  - CPU média e pico (%)
  - Iterações médias
"""

import random
import statistics
import time

from monitor import carregar_csv, medir_bloco, resumo_print


# ─────────────────────────────────────────────
# ESTRUTURA: ARRAY LINEAR
# ─────────────────────────────────────────────

class ArrayLinear:
    def __init__(self):
        self.dados: list[dict] = []

    def inserir(self, registro: dict):
        """Insere ao final. Complexidade: O(1) amortizado."""
        self.dados.append(registro)

    def busca_sequencial(self, matricula: str) -> tuple:
        """
        Percorre o array do início ao fim.
        Complexidade: O(n) no pior caso.
        Retorna: (registro | None, iterações)
        """
        for i, registro in enumerate(self.dados, start=1):
            if registro["matricula"] == matricula:
                return registro, i
        return None, len(self.dados)

    def ordenar(self):
        """Ordena in-place por matrícula. Necessário para busca binária."""
        self.dados.sort(key=lambda r: r["matricula"])

    def busca_binaria(self, matricula: str) -> tuple:
        """
        Busca binária sobre array JÁ ORDENADO.
        Complexidade: O(log n).
        Retorna: (registro | None, iterações)
        """
        esq, dir_ = 0, len(self.dados) - 1
        iteracoes = 0
        while esq <= dir_:
            iteracoes += 1
            meio = (esq + dir_) // 2
            chave_meio = self.dados[meio]["matricula"]
            if chave_meio == matricula:
                return self.dados[meio], iteracoes
            elif chave_meio < matricula:
                esq = meio + 1
            else:
                dir_ = meio - 1
        return None, iteracoes


# ─────────────────────────────────────────────
# FUNÇÕES DE MEDIÇÃO
# ─────────────────────────────────────────────

def _fazer_insercao(registros: list) -> "ArrayLinear":
    arr = ArrayLinear()
    for r in registros:
        arr.inserir(r)
    return arr


def _fazer_busca_sequencial(arr: ArrayLinear, chaves: list) -> dict:
    iteracoes_lista = []
    for ch in chaves:
        _, it = arr.busca_sequencial(ch)
        iteracoes_lista.append(it)
    return {
        "iter_media": statistics.mean(iteracoes_lista),
        "iter_std":   statistics.stdev(iteracoes_lista) if len(iteracoes_lista) > 1 else 0,
    }


def _fazer_busca_binaria(arr: ArrayLinear, chaves: list) -> dict:
    # Mede ordenação separadamente
    inicio_ord = time.perf_counter()
    arr.ordenar()
    t_ord = time.perf_counter() - inicio_ord

    iteracoes_lista = []
    for ch in chaves:
        _, it = arr.busca_binaria(ch)
        iteracoes_lista.append(it)
    return {
        "t_ord_s":    t_ord,
        "iter_media": statistics.mean(iteracoes_lista),
        "iter_std":   statistics.stdev(iteracoes_lista) if len(iteracoes_lista) > 1 else 0,
    }


# ─────────────────────────────────────────────
# EXPERIMENTO
# ─────────────────────────────────────────────

NUM_RODADAS = 5
NUM_BUSCAS  = 100


def rodar_experimento(N: int, caminho: str) -> dict:
    print(f"\n{'═'*65}")
    print(f"  ARRAY LINEAR | N = {N:,}")
    print(f"{'═'*65}")

    registros_base = carregar_csv(caminho)

    # Acumuladores
    ins  = {"tempo": [], "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}
    seq  = {"tempo": [], "iter_media": [], "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}
    bin_ = {"tempo": [], "t_ord": [], "iter_media": [],
            "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}

    for rodada in range(1, NUM_RODADAS + 1):
        chaves = [r["matricula"] for r in random.sample(registros_base, NUM_BUSCAS)]

        # ── Inserção ──────────────────────────────────────────
        arr, m_ins = medir_bloco(_fazer_insercao, registros_base)
        ins["tempo"].append(m_ins["tempo_s"])
        ins["mem_trace"].append(m_ins["mem_trace_kb"])
        ins["mem_ram"].append(m_ins["mem_ram_kb"])
        ins["cpu_media"].append(m_ins["cpu_media_pct"])
        ins["cpu_pico"].append(m_ins["cpu_pico_pct"])

        # ── Busca Sequencial ──────────────────────────────────
        dados_seq, m_seq = medir_bloco(_fazer_busca_sequencial, arr, chaves)
        seq["tempo"].append(m_seq["tempo_s"])
        seq["iter_media"].append(dados_seq["iter_media"])
        seq["mem_trace"].append(m_seq["mem_trace_kb"])
        seq["mem_ram"].append(m_seq["mem_ram_kb"])
        seq["cpu_media"].append(m_seq["cpu_media_pct"])
        seq["cpu_pico"].append(m_seq["cpu_pico_pct"])

        # ── Busca Binária (array fresco para não usar o já medido) ──
        arr2, _ = medir_bloco(_fazer_insercao, registros_base)
        dados_bin, m_bin = medir_bloco(_fazer_busca_binaria, arr2, chaves)
        bin_["tempo"].append(m_bin["tempo_s"])
        bin_["t_ord"].append(dados_bin["t_ord_s"])
        bin_["iter_media"].append(dados_bin["iter_media"])
        bin_["mem_trace"].append(m_bin["mem_trace_kb"])
        bin_["mem_ram"].append(m_bin["mem_ram_kb"])
        bin_["cpu_media"].append(m_bin["cpu_media_pct"])
        bin_["cpu_pico"].append(m_bin["cpu_pico_pct"])

        print(f"\n  Rodada {rodada}:")
        print(f"    [INS] tempo={m_ins['tempo_s']:.4f}s  "
              f"mem_trace={m_ins['mem_trace_kb']:.1f}KB  "
              f"ram_delta={m_ins['mem_ram_kb']:.1f}KB  "
              f"cpu={m_ins['cpu_media_pct']:.1f}%")
        print(f"    [SEQ] tempo={m_seq['tempo_s']:.4f}s  "
              f"iter={dados_seq['iter_media']:.0f}  "
              f"mem_trace={m_seq['mem_trace_kb']:.1f}KB  "
              f"cpu={m_seq['cpu_media_pct']:.1f}%")
        print(f"    [BIN] tempo={m_bin['tempo_s']:.4f}s  "
              f"iter={dados_bin['iter_media']:.1f}  "
              f"ord={dados_bin['t_ord_s']:.4f}s  "
              f"mem_trace={m_bin['mem_trace_kb']:.1f}KB  "
              f"cpu={m_bin['cpu_media_pct']:.1f}%")

    # ── Resumo ────────────────────────────────────────────────
    print(f"\n  {'─'*60}")
    print(f"  RESUMO (média ± desvio padrão) — N={N:,}")
    print(f"  {'─'*60}")

    print("  [INSERÇÃO]")
    resumo_print("Tempo (s)",            ins["tempo"])
    resumo_print("Mem tracemalloc (KB)", ins["mem_trace"])
    resumo_print("RAM delta (KB)",       ins["mem_ram"])
    resumo_print("CPU média (%)",        ins["cpu_media"])
    resumo_print("CPU pico (%)",         ins["cpu_pico"])

    print("  [BUSCA SEQUENCIAL — O(n)]")
    resumo_print("Tempo (s)",            seq["tempo"])
    resumo_print("Iterações médias",     seq["iter_media"])
    resumo_print("Mem tracemalloc (KB)", seq["mem_trace"])
    resumo_print("RAM delta (KB)",       seq["mem_ram"])
    resumo_print("CPU média (%)",        seq["cpu_media"])
    resumo_print("CPU pico (%)",         seq["cpu_pico"])

    print("  [BUSCA BINÁRIA — O(log n)]")
    resumo_print("Tempo (s)",            bin_["tempo"])
    resumo_print("Tempo ordenação (s)",  bin_["t_ord"])
    resumo_print("Iterações médias",     bin_["iter_media"])
    resumo_print("Mem tracemalloc (KB)", bin_["mem_trace"])
    resumo_print("RAM delta (KB)",       bin_["mem_ram"])
    resumo_print("CPU média (%)",        bin_["cpu_media"])
    resumo_print("CPU pico (%)",         bin_["cpu_pico"])

    def med(lst): return statistics.mean(lst)
    def std(lst): return statistics.stdev(lst) if len(lst) > 1 else 0.0

    return {
        "estrutura": "Array Linear",
        "N": N,
        # Inserção
        "ins_tempo_med":     med(ins["tempo"]),
        "ins_tempo_std":     std(ins["tempo"]),
        "ins_mem_trace_kb":  med(ins["mem_trace"]),
        "ins_mem_ram_kb":    med(ins["mem_ram"]),
        "ins_cpu_media_pct": med(ins["cpu_media"]),
        "ins_cpu_pico_pct":  med(ins["cpu_pico"]),
        # Busca sequencial
        "seq_tempo_med":     med(seq["tempo"]),
        "seq_tempo_std":     std(seq["tempo"]),
        "seq_iter_med":      med(seq["iter_media"]),
        "seq_iter_std":      std(seq["iter_media"]),
        "seq_mem_trace_kb":  med(seq["mem_trace"]),
        "seq_mem_ram_kb":    med(seq["mem_ram"]),
        "seq_cpu_media_pct": med(seq["cpu_media"]),
        "seq_cpu_pico_pct":  med(seq["cpu_pico"]),
        # Busca binária
        "bin_tempo_med":     med(bin_["tempo"]),
        "bin_tempo_std":     std(bin_["tempo"]),
        "bin_t_ord_med":     med(bin_["t_ord"]),
        "bin_iter_med":      med(bin_["iter_media"]),
        "bin_iter_std":      std(bin_["iter_media"]),
        "bin_mem_trace_kb":  med(bin_["mem_trace"]),
        "bin_mem_ram_kb":    med(bin_["mem_ram"]),
        "bin_cpu_media_pct": med(bin_["cpu_media"]),
        "bin_cpu_pico_pct":  med(bin_["cpu_pico"]),
    }