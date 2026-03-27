import math
import random
import statistics

from monitor import carregar_csv, imprimir_tabela, medir_bloco, medir_bloco_repetido

# Adiciona mapeamento de nomes legíveis específicos da hash ao monitor
from monitor import NOMES_METRICAS

NOMES_METRICAS.update({
    "M":                  "Tamanho da Tabela (M)",
    "hash_nome":          "Função Hash",
    "load_factor":        "Fator de Carga (N/M)",
    "colisoes_totais":    "Colisões Totais na Inserção",
    "ins_tempo_med":      "Tempo de Inserção (s)",
    "ins_tempo_std":      "Tempo de Inserção — Desvio (s)",
    "ins_mem_trace_kb":   "Memória Alocada na Inserção (KB)",
    "ins_mem_ram_kb":     "RAM Consumida na Inserção (KB)",
    "ins_cpu_media_pct":  "CPU Médio na Inserção (%)",
    "ins_cpu_pico_pct":   "CPU Pico na Inserção (%)",
    "bus_tempo_med":      "Tempo de Busca (s)",
    "bus_tempo_std":      "Tempo de Busca — Desvio (s)",
    "bus_iter_med":       "Comparações por Busca",
    "bus_iter_std":       "Comparações por Busca — Desvio",
    "bus_mem_trace_kb":   "Memória na Busca (KB)",
    "bus_mem_ram_kb":     "RAM na Busca (KB)",
    "bus_cpu_media_pct":  "CPU Médio na Busca (%)",
    "bus_cpu_pico_pct":   "CPU Pico na Busca (%)",
})


# ─────────────────────────────────────────────
# REGISTRO
# ─────────────────────────────────────────────

class Registro:
    def __init__(self, matricula: int, nome: str, salario: float, setor: str):
        self.matricula = matricula  # chave principal (9 dígitos)
        self.nome      = nome
        self.salario   = salario
        self.setor     = setor


# ─────────────────────────────────────────────
# TABELA HASH — ENCADEAMENTO SEPARADO
# ─────────────────────────────────────────────

class TabelaHash:
  

    HASH_DIVISAO      = 1
    HASH_MULTIPLICACAO = 2
    HASH_MEIO_QUADRADO = 3

    NOMES_HASH = {
        1: "Divisão",
        2: "Multiplicação (Razão Áurea)",
        3: "Meio-Quadrado (Mid-Square)",
    }

    def __init__(self, tamanho_m: int):
     
        self.M                  = tamanho_m
        self.tabela             = [[] for _ in range(self.M)]
        self.elementos_inseridos = 0
        self.colisoes_totais    = 0

    # ── Funções Hash ──────────────────────────────────────────

    def _hash_divisao(self, chave: int) -> int:
        """
        Método da Divisão: h(k) = k mod M
        Simples e eficiente. Evitar M potência de 2.
        Complexidade: O(1)
        """
        return chave % self.M

    def _hash_multiplicacao(self, chave: int) -> int:
        """
        Método da Multiplicação com constante da Razão Áurea (Knuth).
        h(k) = floor(M * (k*A mod 1)), A = 0.6180339887
        Distribui melhor que a divisão para chaves sequenciais.
        Complexidade: O(1)
        """
        A = 0.6180339887
        return math.floor(self.M * ((chave * A) % 1))

    def _hash_meio_quadrado(self, chave: int) -> int:
        """
        Método Mid-Square: eleva ao quadrado e extrai dígitos centrais.
        Gera boa dispersão mas depende do tamanho da chave.
        Complexidade: O(1)
        """
        quadrado     = chave * chave
        str_quadrado = str(quadrado)
        meio         = len(str_quadrado) // 2
        if len(str_quadrado) >= 3:
            digitos_meio = int(str_quadrado[max(0, meio - 1):meio + 2])
        else:
            digitos_meio = int(str_quadrado)
        return digitos_meio % self.M

    # ── Seletor de Hash ───────────────────────────────────────

    def obter_indice(self, chave: int, tipo_hash: int) -> int:
        if tipo_hash == self.HASH_DIVISAO:
            return self._hash_divisao(chave)
        elif tipo_hash == self.HASH_MULTIPLICACAO:
            return self._hash_multiplicacao(chave)
        elif tipo_hash == self.HASH_MEIO_QUADRADO:
            return self._hash_meio_quadrado(chave)
        else:
            raise ValueError("Tipo de hash inválido. Use 1, 2 ou 3.")

    # ── Inserção ──────────────────────────────────────────────

    def inserir(self, registro: Registro, tipo_hash: int = 1) -> int:
        """
        Insere registro na tabela. Se já existe elemento no índice,
        registra colisão e encadeia na lista.
        Complexidade: O(1) médio, O(n) pior caso.
        Retorna: comprimento da cadeia antes da inserção (iterações de colisão).
        """
        indice = self.obter_indice(registro.matricula, tipo_hash)
        iteracoes = len(self.tabela[indice])  # percurso necessário por colisões
        if iteracoes > 0:
            self.colisoes_totais += 1
        self.tabela[indice].append(registro)
        self.elementos_inseridos += 1
        return iteracoes + 1  # +1 pela inserção em si

    # ── Busca ─────────────────────────────────────────────────

    def buscar(self, matricula: int, tipo_hash: int = 1) -> tuple:
        """
        Busca por matrícula. Percorre a lista da posição calculada.
        Complexidade: O(1) médio, O(n) pior caso (muitas colisões).
        Retorna: (registro | None, iterações)
        """
        indice    = self.obter_indice(matricula, tipo_hash)
        iteracoes = 0
        for registro in self.tabela[indice]:
            iteracoes += 1
            if registro.matricula == matricula:
                return registro, iteracoes
        return None, iteracoes

    # ── Métricas ──────────────────────────────────────────────

    def calcular_load_factor(self) -> float:
        """Fator de Carga = N / M. Indica o nível de ocupação da tabela."""
        return self.elementos_inseridos / self.M


# ─────────────────────────────────────────────
# FUNÇÕES DE MEDIÇÃO
# ─────────────────────────────────────────────

def _converter_registro(row: dict) -> Registro:
    """Converte uma linha do CSV (dict) para objeto Registro."""
    return Registro(
        matricula=int(row["matricula"]),
        nome=row.get("nome", ""),
        salario=float(row.get("salario", 0)),
        setor=row.get("setor", row.get("codigo_setor", "")),
    )


def _fazer_insercao(registros: list, M: int, tipo_hash: int) -> tuple:
    tabela = TabelaHash(M)
    total = 0
    for row in registros:
        reg = _converter_registro(row)
        total += tabela.inserir(reg, tipo_hash)
    iter_media = total / len(registros) if registros else 0.0
    return tabela, iter_media


def _fazer_busca(tabela: TabelaHash, chaves: list, tipo_hash: int) -> dict:
    iteracoes_lista = []
    for ch in chaves:
        _, it = tabela.buscar(int(ch), tipo_hash)
        iteracoes_lista.append(it)
    return {
        "iter_media": statistics.mean(iteracoes_lista),
        "iter_std":   statistics.stdev(iteracoes_lista) if len(iteracoes_lista) > 1 else 0,
    }


# ─────────────────────────────────────────────
# EXPERIMENTO
# ─────────────────────────────────────────────

NUM_RODADAS = 5
NUM_BUSCAS  = 100

VALORES_M   = [100, 1000, 5000]
TIPOS_HASH  = [
    TabelaHash.HASH_DIVISAO,
    TabelaHash.HASH_MULTIPLICACAO,
    TabelaHash.HASH_MEIO_QUADRADO,
]


def rodar_experimento(N: int, caminho: str) -> list[dict]:
    """
    Executa o experimento para todos os valores de M e funções hash.
    Retorna lista de resultados (um por combinação M × hash).
    """
    registros_base = carregar_csv(caminho)
    todos_resultados = []

    for M in VALORES_M:
        for tipo_hash in TIPOS_HASH:
            nome_hash = TabelaHash.NOMES_HASH[tipo_hash]

            print(f"\n{'═'*65}")
            print(f"  TABELA HASH | N={N:,} | M={M} | Hash: {nome_hash}")
            print(f"{'═'*65}")

            ins = {"tempo": [], "iter_media": [], "mem_trace": [], "mem_ram": [],
                   "cpu_media": [], "cpu_pico": [],
                   "colisoes": [], "load_factor": []}
            bus = {"tempo": [], "iter_media": [], "mem_trace": [],
                   "mem_ram": [], "cpu_media": [], "cpu_pico": []}

            for rodada in range(1, NUM_RODADAS + 1):
                chaves = [r["matricula"] for r in random.sample(registros_base, NUM_BUSCAS)]

                # ── Inserção ──────────────────────────────────
                (tabela, ins_it), m_ins = medir_bloco(_fazer_insercao, registros_base, M, tipo_hash)
                ins["tempo"].append(m_ins["tempo_s"])
                ins["iter_media"].append(ins_it)
                ins["mem_trace"].append(m_ins["mem_trace_kb"])
                ins["mem_ram"].append(m_ins["mem_ram_kb"])
                ins["cpu_media"].append(m_ins["cpu_media_pct"])
                ins["cpu_pico"].append(m_ins["cpu_pico_pct"])
                ins["colisoes"].append(tabela.colisoes_totais)
                ins["load_factor"].append(tabela.calcular_load_factor())

                # ── Busca — repetida 500x para capturar CPU ───
                dados_bus, m_bus = medir_bloco_repetido(
                    _fazer_busca, 500, tabela, chaves, tipo_hash
                )
                bus["tempo"].append(m_bus["tempo_s"])
                bus["iter_media"].append(dados_bus["iter_media"])
                bus["mem_trace"].append(m_bus["mem_trace_kb"])
                bus["mem_ram"].append(m_bus["mem_ram_kb"])
                bus["cpu_media"].append(m_bus["cpu_media_pct"])
                bus["cpu_pico"].append(m_bus["cpu_pico_pct"])

                print(f"\n  Rodada {rodada}:")
                print(f"    [Inserção] tempo={m_ins['tempo_s']:.4f}s  iter={ins_it:.2f}  mem={m_ins['mem_trace_kb']:.1f}KB  cpu={m_ins['cpu_media_pct']:.1f}%  colisões={tabela.colisoes_totais}  λ={tabela.calcular_load_factor():.2f}")
                print(f"    [Busca]    tempo={m_bus['tempo_s']:.6f}s  iter={dados_bus['iter_media']:.2f}  mem={m_bus['mem_trace_kb']:.1f}KB  cpu={m_bus['cpu_media_pct']:.1f}%")

            def med(lst): return statistics.mean(lst)
            def std(lst): return statistics.stdev(lst) if len(lst) > 1 else 0.0

            resultado = {
                "estrutura":         f"Hash ({nome_hash})",
                "N":                 N,
                "M":                 M,
                "hash_nome":         nome_hash,
                "load_factor":       med(ins["load_factor"]),
                "colisoes_totais":   med(ins["colisoes"]),
                # Inserção
                "ins_tempo_med":     med(ins["tempo"]),
                "ins_iter_med":      med(ins["iter_media"]),
                "ins_mem_trace_kb":  med(ins["mem_trace"]),
                "ins_cpu_media_pct": med(ins["cpu_media"]),
                # Busca
                "bus_tempo_med":     med(bus["tempo"]),
                "bus_iter_med":      med(bus["iter_media"]),
                "bus_mem_trace_kb":  med(bus["mem_trace"]),
                "bus_cpu_media_pct": med(bus["cpu_media"]),
            }

            # Tabela de resumo legível no terminal
            imprimir_tabela(
                f"RESUMO — Hash {nome_hash} | M={M} | N={N:,} (média de {NUM_RODADAS} rodadas)",
                resultado,
                ignorar={"estrutura", "hash_nome"}
            )

            todos_resultados.append(resultado)

    return todos_resultados