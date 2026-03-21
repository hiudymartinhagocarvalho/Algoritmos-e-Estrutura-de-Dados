import csv
import time
import tracemalloc
import statistics
import os


# ─────────────────────────────────────────────
# ESTRUTURA: ARRAY LINEAR
# ─────────────────────────────────────────────

class ArrayLinear:
    def __init__(self):
        self.dados = []  # lista Python usada como array dinâmico

    def inserir(self, registro: dict):
        """Insere registro no final do array. Custo: O(1) amortizado."""
        self.dados.append(registro)

    def buscar(self, matricula: str):
        """
        Busca linear sequencial.
        Percorre elemento por elemento até encontrar ou esgotar.
        Custo: O(n) no pior caso.
        Retorna: (registro | None, número de iterações)
        """
        iteracoes = 0
        for registro in self.dados:
            iteracoes += 1
            if registro["matricula"] == matricula:
                return registro, iteracoes
        return None, iteracoes

    def tamanho(self):
        return len(self.dados)


# ─────────────────────────────────────────────
# LEITURA DO CSV
# ─────────────────────────────────────────────

def carregar_csv(caminho: str) -> list:
    """Lê o arquivo CSV e retorna lista de dicionários."""
    registros = []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append(row)
    return registros


# ─────────────────────────────────────────────
# MÉTRICAS
# ─────────────────────────────────────────────

def medir_insercao(registros: list):
    """
    Insere todos os registros no array e coleta:
    - Tempo total de inserção
    - Pico de memória (tracemalloc)
    Retorna: (array preenchido, tempo_s, pico_mem_kb)
    """
    tracemalloc.start()
    inicio = time.perf_counter()

    arr = ArrayLinear()
    for r in registros:
        arr.inserir(r)

    fim = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return arr, fim - inicio, pico / 1024  # tempo em s, memória em KB


def medir_busca(arr: ArrayLinear, chaves: list):
    """
    Executa buscas para as chaves fornecidas e coleta:
    - Tempo total de busca
    - Média de iterações por busca
    - Pico de memória
    Retorna: (tempo_s, media_iteracoes, pico_mem_kb)
    """
    tracemalloc.start()
    inicio = time.perf_counter()

    iteracoes_lista = []
    for ch in chaves:
        _, it = arr.buscar(ch)
        iteracoes_lista.append(it)

    fim = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return fim - inicio, statistics.mean(iteracoes_lista), pico / 1024


# ─────────────────────────────────────────────
# EXPERIMENTO: 5 RODADAS POR VOLUME
# ─────────────────────────────────────────────

NUM_RODADAS = 5
NUM_BUSCAS  = 100  # chaves buscadas por rodada

_BASE = os.path.join(os.path.dirname(__file__), "..", "..")
ARQUIVOS = {
    10_000:  os.path.join(_BASE, "datasets", "dados_10000.csv"),
    50_000:  os.path.join(_BASE, "datasets", "dados_50000.csv"),
    100_000: os.path.join(_BASE, "datasets", "dados_100000.csv"),
}


def rodar_experimento(N: int, caminho: str):
    print(f"\n{'─'*55}")
    print(f"  Array Linear | N = {N:,}")
    print(f"{'─'*55}")

    registros_base = carregar_csv(caminho)

    t_ins_list, m_ins_list = [], []
    t_bus_list, m_bus_list, it_list = [], [], []

    for rodada in range(1, NUM_RODADAS + 1):
        # Seleciona chaves de busca aleatoriamente (sem embaralhar os dados)
        import random
        amostra = random.sample(registros_base, NUM_BUSCAS)
        chaves  = [r["matricula"] for r in amostra]

        # Inserção
        arr, t_ins, m_ins = medir_insercao(registros_base)
        t_ins_list.append(t_ins)
        m_ins_list.append(m_ins)

        # Busca
        t_bus, media_it, m_bus = medir_busca(arr, chaves)
        t_bus_list.append(t_bus)
        m_bus_list.append(media_it)
        it_list.append(media_it)

        print(f"  Rodada {rodada}: ins={t_ins:.4f}s | "
              f"mem_ins={m_ins:.1f}KB | "
              f"busca={t_bus:.4f}s | "
              f"iter_media={media_it:.1f}")

    print(f"\n  RESUMO (média ± desvio padrão):")
    print(f"  Inserção  : {statistics.mean(t_ins_list):.4f}s "
          f"± {statistics.stdev(t_ins_list):.4f}s")
    print(f"  Mem Ins   : {statistics.mean(m_ins_list):.1f}KB "
          f"± {statistics.stdev(m_ins_list):.1f}KB")
    print(f"  Busca     : {statistics.mean(t_bus_list):.4f}s "
          f"± {statistics.stdev(t_bus_list):.4f}s")
    print(f"  Iterações : {statistics.mean(it_list):.1f} "
          f"± {statistics.stdev(it_list):.1f}")

    return {
        "N": N,
        "t_ins_media": statistics.mean(t_ins_list),
        "t_ins_std":   statistics.stdev(t_ins_list),
        "mem_ins_kb":  statistics.mean(m_ins_list),
        "t_bus_media": statistics.mean(t_bus_list),
        "t_bus_std":   statistics.stdev(t_bus_list),
        "iter_media":  statistics.mean(it_list),
        "iter_std":    statistics.stdev(it_list),
    }


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    resultados = []

    for N, caminho in ARQUIVOS.items():
        if not os.path.exists(caminho):
            print(f"[AVISO] Arquivo não encontrado: {caminho}")
            continue
        res = rodar_experimento(N, caminho)
        resultados.append(res)

    # Salva resumo em CSV
    import csv as csv_mod
    with open("resultados_array.csv", "w", newline="", encoding="utf-8") as f:
        campos = ["N", "t_ins_media", "t_ins_std", "mem_ins_kb",
                  "t_bus_media", "t_bus_std", "iter_media", "iter_std"]
        writer = csv_mod.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print("\n\nResultados salvos em: resultados_array.csv")
    print("Experimento concluído!")