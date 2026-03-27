import random
import statistics
import time
from monitor import carregar_csv, imprimir_tabela, medir_bloco, medir_bloco_repetido, resumo_print

class ArrayLinear:
    def __init__(self):
        self.dados: list[dict] = []

    def inserir(self, registro: dict):
        
        self.dados.append(registro)

    def busca_sequencial(self, matricula: str) -> tuple:

        for i, registro in enumerate(self.dados, start=1):
            if registro["matricula"] == matricula:
                return registro, i
        return None, len(self.dados)

    def ordenar(self):
        
        self.dados.sort(key=lambda r: r["matricula"])

    def busca_binaria(self, matricula: str) -> tuple:
        
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


def _fazer_insercao(registros: list) -> tuple:
    arr = ArrayLinear()
    for r in registros:
        arr.inserir(r)
    return arr, 1.0


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


NUM_RODADAS = 5
NUM_BUSCAS  = 50000


def rodar_experimento(N: int, caminho: str) -> dict:
    print(f"\n{'═'*65}")
    print(f"  ARRAY LINEAR | N = {N:,}")
    print(f"{'═'*65}")

    registros_base = carregar_csv(caminho)

    ins  = {"tempo": [], "iter_media": [], "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}
    seq  = {"tempo": [], "iter_media": [], "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}
    bin_ = {"tempo": [], "t_ord": [], "iter_media": [],
            "mem_trace": [], "mem_ram": [], "cpu_media": [], "cpu_pico": []}

    for rodada in range(1, NUM_RODADAS + 1):
        tamanho_populacao = len(registros_base)
        quantidade = min(NUM_BUSCAS, tamanho_populacao)
        # Usamos choices para permitir NUM_BUSCAS > N se necessário no futuro
        chaves = [r["matricula"] for r in random.choices(registros_base, k=quantidade)]

        # --- Inserção ---
        # Usamos medir_bloco_repetido para a CPU registrar atividade
        (arr, ins_it), m_ins = medir_bloco_repetido(_fazer_insercao, 100, registros_base)
        ins["tempo"].append(m_ins["tempo_s"] / 100) # Divide pelo n de repetições
        ins["iter_media"].append(ins_it)
        ins["mem_trace"].append(m_ins["mem_trace_kb"])
        ins["mem_ram"].append(m_ins["mem_ram_kb"])
        ins["cpu_media"].append(m_ins["cpu_media_pct"])
        ins["cpu_pico"].append(m_ins["cpu_pico_pct"])

        # --- Busca Sequencial ---
        dados_seq, m_seq = medir_bloco(_fazer_busca_sequencial, arr, chaves)
        seq["tempo"].append(m_seq["tempo_s"])
        seq["iter_media"].append(dados_seq["iter_media"])
        seq["mem_trace"].append(m_seq["mem_trace_kb"])
        seq["mem_ram"].append(m_seq["mem_ram_kb"])
        seq["cpu_media"].append(m_seq["cpu_media_pct"])
        seq["cpu_pico"].append(m_seq["cpu_pico_pct"])

        # --- Busca Binária ---
        # Criamos uma cópia limpa para a binária
        (arr_bin, _), _ = medir_bloco(_fazer_insercao, registros_base)
        
        # Aqui está o segredo: medimos o bloco da busca
        dados_bin, m_bin = medir_bloco(_fazer_busca_binaria, arr_bin, chaves)
        
        bin_["tempo"].append(m_bin["tempo_s"])
        bin_["t_ord"].append(dados_bin["t_ord_s"])
        bin_["iter_media"].append(dados_bin["iter_media"])
        bin_["mem_trace"].append(m_bin["mem_trace_kb"])
        bin_["mem_ram"].append(m_bin["mem_ram_kb"])
        bin_["cpu_media"].append(m_bin["cpu_media_pct"])
        bin_["cpu_pico"].append(m_bin["cpu_pico_pct"])

        print(f"\n  Rodada {rodada}:")
        print(f"    [Inserção]         tempo={m_ins['tempo_s']:.4f}s  iter={ins_it:.0f}  mem={m_ins['mem_trace_kb']:.1f}KB  cpu={m_ins['cpu_media_pct']:.1f}%")
        print(f"    [Busca Sequencial] tempo={m_seq['tempo_s']:.4f}s  iter={dados_seq['iter_media']:.0f}  mem={m_seq['mem_trace_kb']:.1f}KB  cpu={m_seq['cpu_media_pct']:.1f}%")
        print(f"    [Busca Binária]    tempo={m_bin['tempo_s']:.4f}s  iter={dados_bin['iter_media']:.1f}  ord={dados_bin['t_ord_s']:.4f}s  mem={m_bin['mem_trace_kb']:.1f}KB  cpu={m_bin['cpu_media_pct']:.1f}%")

    def med(lst): return statistics.mean(lst)
    def std(lst): return statistics.stdev(lst) if len(lst) > 1 else 0.0

    resultado = {
        "estrutura":         "Array Linear",
        "N":                 N,
        # Inserção
        "ins_tempo_med":     med(ins["tempo"]),
        "ins_iter_med":      med(ins["iter_media"]),
        "ins_mem_trace_kb":  med(ins["mem_trace"]),
        "ins_cpu_media_pct": med(ins["cpu_media"]),
        # Busca Sequencial
        "seq_tempo_med":     med(seq["tempo"]),
        "seq_iter_med":      med(seq["iter_media"]),
        "seq_mem_trace_kb":  med(seq["mem_trace"]),
        "seq_cpu_media_pct": med(seq["cpu_media"]),
        # Busca Binária
        "bin_tempo_med":     med(bin_["tempo"]),
        "bin_t_ord_med":     med(bin_["t_ord"]),
        "bin_iter_med":      med(bin_["iter_media"]),
        "bin_mem_trace_kb":  med(bin_["mem_trace"]),
        "bin_cpu_media_pct": med(bin_["cpu_media"]),
    }

    # Imprime tabela final de resumo com nomes legíveis
    imprimir_tabela(
        f"RESUMO — Array Linear | N={N:,} (média de {NUM_RODADAS} rodadas)",
        resultado,
        ignorar={
            "N", "estrutura",
            "ins_mem_ram_kb",  "seq_mem_ram_kb",  "bin_mem_ram_kb",
            "ins_cpu_pico_pct","seq_cpu_pico_pct","bin_cpu_pico_pct",
            "ins_iter_std",    "seq_iter_std",    "bin_iter_std",
        }
    )

    return resultado