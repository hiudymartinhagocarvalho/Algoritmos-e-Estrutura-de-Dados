import random
import statistics

from monitor import carregar_csv, medir_bloco, resumo_print


# ─────────────────────────────────────────────
# BST — SEM BALANCEAMENTO
# ─────────────────────────────────────────────

class NoBST:
    def __init__(self, registro: dict):
        self.registro = registro
        self.esq = None
        self.dir = None


class BST:
    """
    Árvore Binária de Busca padrão, sem balanceamento.
    Inserção e busca: O(log n) médio, O(n) pior caso (dados ordenados).
    """

    def __init__(self):
        self.raiz = None

    def inserir(self, registro: dict) -> int:
        cnt = [0]
        self.raiz = self._inserir(self.raiz, registro, cnt)
        return cnt[0]

    def _inserir(self, no, registro, cnt):
        cnt[0] += 1
        if no is None:
            return NoBST(registro)
        chave = registro["matricula"]
        if chave < no.registro["matricula"]:
            no.esq = self._inserir(no.esq, registro, cnt)
        elif chave > no.registro["matricula"]:
            no.dir = self._inserir(no.dir, registro, cnt)
        return no  # duplicata ignorada

    def buscar(self, matricula: str) -> tuple:
        """Retorna (registro | None, iterações)."""
        return self._buscar(self.raiz, matricula, 0)

    def _buscar(self, no, matricula, iteracoes):
        iteracoes += 1
        if no is None:
            return None, iteracoes
        if matricula == no.registro["matricula"]:
            return no.registro, iteracoes
        elif matricula < no.registro["matricula"]:
            return self._buscar(no.esq, matricula, iteracoes)
        else:
            return self._buscar(no.dir, matricula, iteracoes)

    def altura(self) -> int:
        return self._altura(self.raiz)

    def _altura(self, no) -> int:
        if no is None:
            return 0
        return 1 + max(self._altura(no.esq), self._altura(no.dir))


# ─────────────────────────────────────────────
# AVL — COM BALANCEAMENTO AUTOMÁTICO
# ─────────────────────────────────────────────

class NoAVL:
    def __init__(self, registro: dict):
        self.registro = registro
        self.esq = None
        self.dir = None
        self.altura = 1


class AVL:
    """
    Árvore AVL: mantém |FB| <= 1 via rotações.
    Inserção e busca garantidas em O(log n) no pior caso.
    """

    def __init__(self):
        self.raiz = None

    def _alt(self, no) -> int:
        return no.altura if no else 0

    def _fb(self, no) -> int:
        return self._alt(no.esq) - self._alt(no.dir) if no else 0

    def _upd(self, no):
        no.altura = 1 + max(self._alt(no.esq), self._alt(no.dir))

    def _rot_dir(self, y):
        x = y.esq; T2 = x.dir
        x.dir = y; y.esq = T2
        self._upd(y); self._upd(x)
        return x

    def _rot_esq(self, x):
        y = x.dir; T2 = y.esq
        y.esq = x; x.dir = T2
        self._upd(x); self._upd(y)
        return y

    def _balancear(self, no):
        self._upd(no)
        fb = self._fb(no)
        if fb > 1 and self._fb(no.esq) >= 0:        # EE
            return self._rot_dir(no)
        if fb > 1 and self._fb(no.esq) < 0:         # ED
            no.esq = self._rot_esq(no.esq)
            return self._rot_dir(no)
        if fb < -1 and self._fb(no.dir) <= 0:       # DD
            return self._rot_esq(no)
        if fb < -1 and self._fb(no.dir) > 0:        # DE
            no.dir = self._rot_dir(no.dir)
            return self._rot_esq(no)
        return no

    def inserir(self, registro: dict) -> int:
        cnt = [0]
        self.raiz = self._inserir(self.raiz, registro, cnt)
        return cnt[0]

    def _inserir(self, no, registro, cnt):
        cnt[0] += 1
        if no is None:
            return NoAVL(registro)
        chave = registro["matricula"]
        if chave < no.registro["matricula"]:
            no.esq = self._inserir(no.esq, registro, cnt)
        elif chave > no.registro["matricula"]:
            no.dir = self._inserir(no.dir, registro, cnt)
        else:
            return no  # duplicata ignorada
        return self._balancear(no)

    def buscar(self, matricula: str) -> tuple:
        """Retorna (registro | None, iterações)."""
        return self._buscar(self.raiz, matricula, 0)

    def _buscar(self, no, matricula, iteracoes):
        iteracoes += 1
        if no is None:
            return None, iteracoes
        if matricula == no.registro["matricula"]:
            return no.registro, iteracoes
        elif matricula < no.registro["matricula"]:
            return self._buscar(no.esq, matricula, iteracoes)
        else:
            return self._buscar(no.dir, matricula, iteracoes)

    def altura(self) -> int:
        return self._alt(self.raiz)


# ─────────────────────────────────────────────
# FUNÇÕES DE MEDIÇÃO
# ─────────────────────────────────────────────

def _fazer_insercao(registros: list, usar_avl: bool):
    arvore = AVL() if usar_avl else BST()
    total = 0
    for r in registros:
        total += arvore.inserir(r)
    iter_media = total / len(registros) if registros else 0.0
    return arvore, iter_media


def _fazer_busca(arvore, chaves: list) -> dict:
    iteracoes_lista = []
    for ch in chaves:
        _, it = arvore.buscar(ch)
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


def rodar_experimento(N: int, caminho: str, usar_avl: bool) -> dict:
    nome = "AVL (com balanceamento)" if usar_avl else "BST (sem balanceamento)"
    print(f"\n{'═'*65}")
    print(f"  {nome} | N = {N:,}")
    print(f"{'═'*65}")

    registros_base = carregar_csv(caminho)

    ins  = {"tempo": [], "iter_media": [], "mem_trace": [], "mem_ram": [],
            "cpu_media": [], "cpu_pico": [], "altura": []}
    bus  = {"tempo": [], "iter_media": [], "mem_trace": [],
            "mem_ram": [], "cpu_media": [], "cpu_pico": []}

    for rodada in range(1, NUM_RODADAS + 1):
        chaves = [r["matricula"] for r in random.sample(registros_base, NUM_BUSCAS)]

        # ── Inserção ──────────────────────────────────────────
        (arvore, ins_it), m_ins = medir_bloco(_fazer_insercao, registros_base, usar_avl)
        h = arvore.altura()
        ins["tempo"].append(m_ins["tempo_s"])
        ins["iter_media"].append(ins_it)
        ins["mem_trace"].append(m_ins["mem_trace_kb"])
        ins["mem_ram"].append(m_ins["mem_ram_kb"])
        ins["cpu_media"].append(m_ins["cpu_media_pct"])
        ins["cpu_pico"].append(m_ins["cpu_pico_pct"])
        ins["altura"].append(h)

        # ── Busca ─────────────────────────────────────────────
        dados_bus, m_bus = medir_bloco(_fazer_busca, arvore, chaves)
        bus["tempo"].append(m_bus["tempo_s"])
        bus["iter_media"].append(dados_bus["iter_media"])
        bus["mem_trace"].append(m_bus["mem_trace_kb"])
        bus["mem_ram"].append(m_bus["mem_ram_kb"])
        bus["cpu_media"].append(m_bus["cpu_media_pct"])
        bus["cpu_pico"].append(m_bus["cpu_pico_pct"])

        print(f"\n  Rodada {rodada}:")
        print(f"    [INS] tempo={m_ins['tempo_s']:.4f}s  iter={ins_it:.1f}  mem={m_ins['mem_trace_kb']:.1f}KB  cpu={m_ins['cpu_media_pct']:.1f}%  altura={h}")
        print(f"    [BUS] tempo={m_bus['tempo_s']:.4f}s  iter={dados_bus['iter_media']:.1f}  mem={m_bus['mem_trace_kb']:.1f}KB  cpu={m_bus['cpu_media_pct']:.1f}%")

    # ── Resumo ────────────────────────────────────────────────
    print(f"\n  {'─'*60}")
    print(f"  RESUMO (média ± desvio padrão) — {nome} | N={N:,}")
    print(f"  {'─'*60}")

    print("  [INSERÇÃO]")
    resumo_print("Tempo (s)",        ins["tempo"])
    resumo_print("Iterações",        ins["iter_media"])
    resumo_print("Memória (KB)",     ins["mem_trace"])
    resumo_print("CPU (%)",          ins["cpu_media"])
    resumo_print("Altura da árvore", ins["altura"], fmt=".1f")

    print(f"  [BUSCA — O(log n)]")
    resumo_print("Tempo (s)",    bus["tempo"])
    resumo_print("Iterações",    bus["iter_media"])
    resumo_print("Memória (KB)", bus["mem_trace"])
    resumo_print("CPU (%)",      bus["cpu_media"])

    def med(lst): return statistics.mean(lst)
    def std(lst): return statistics.stdev(lst) if len(lst) > 1 else 0.0

    return {
        "estrutura":         nome,
        "N":                 N,
        # Inserção
        "ins_tempo_med":     med(ins["tempo"]),
        "ins_iter_med":      med(ins["iter_media"]),
        "ins_mem_trace_kb":  med(ins["mem_trace"]),
        "ins_cpu_media_pct": med(ins["cpu_media"]),
        "altura_media":      med(ins["altura"]),
        # Busca
        "bus_tempo_med":     med(bus["tempo"]),
        "bus_iter_med":      med(bus["iter_media"]),
        "bus_mem_trace_kb":  med(bus["mem_trace"]),
        "bus_cpu_media_pct": med(bus["cpu_media"]),
    }