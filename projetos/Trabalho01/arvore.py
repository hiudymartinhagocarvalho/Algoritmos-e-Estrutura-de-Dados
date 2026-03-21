import csv
import time
import tracemalloc
import statistics
import random
import os


# ─────────────────────────────────────────────
# BST — ÁRVORE BINÁRIA DE BUSCA (SEM BALANCEAMENTO)
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

    def inserir(self, registro: dict):
        self.raiz = self._inserir(self.raiz, registro)

    def _inserir(self, no, registro):
        if no is None:
            return NoBST(registro)
        chave = registro["matricula"]
        if chave < no.registro["matricula"]:
            no.esq = self._inserir(no.esq, registro)
        elif chave > no.registro["matricula"]:
            no.dir = self._inserir(no.dir, registro)
        # chave duplicada: ignora
        return no

    def buscar(self, matricula: str):
        """
        Busca binária na árvore.
        Retorna: (registro | None, iterações)
        """
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

    def altura(self):
        return self._altura(self.raiz)

    def _altura(self, no):
        if no is None:
            return 0
        return 1 + max(self._altura(no.esq), self._altura(no.dir))


# ─────────────────────────────────────────────
# AVL — BST COM BALANCEAMENTO AUTOMÁTICO
# ─────────────────────────────────────────────

class NoAVL:
    def __init__(self, registro: dict):
        self.registro = registro
        self.esq = None
        self.dir = None
        self.altura = 1  # altura do nó na árvore


class AVL:
    """
    Árvore AVL: mantém |FB| <= 1 em todos os nós via rotações.
    Inserção e busca garantidas em O(log n) no pior caso.
    """

    def __init__(self):
        self.raiz = None

    # ── utilidades de altura e fator de balanceamento ──

    def _altura(self, no):
        return no.altura if no else 0

    def _fb(self, no):
        """Fator de Balanceamento = altura(esq) - altura(dir)."""
        return self._altura(no.esq) - self._altura(no.dir) if no else 0

    def _atualizar_altura(self, no):
        no.altura = 1 + max(self._altura(no.esq), self._altura(no.dir))

    # ── rotações ──

    def _rot_direita(self, y):
        """Rotação simples à direita."""
        x  = y.esq
        T2 = x.dir
        x.dir = y
        y.esq = T2
        self._atualizar_altura(y)
        self._atualizar_altura(x)
        return x

    def _rot_esquerda(self, x):
        """Rotação simples à esquerda."""
        y  = x.dir
        T2 = y.esq
        y.esq = x
        x.dir = T2
        self._atualizar_altura(x)
        self._atualizar_altura(y)
        return y

    def _balancear(self, no):
        """Aplica rotação adequada se o nó estiver desbalanceado."""
        self._atualizar_altura(no)
        fb = self._fb(no)

        # Caso Esquerda-Esquerda
        if fb > 1 and self._fb(no.esq) >= 0:
            return self._rot_direita(no)

        # Caso Esquerda-Direita
        if fb > 1 and self._fb(no.esq) < 0:
            no.esq = self._rot_esquerda(no.esq)
            return self._rot_direita(no)

        # Caso Direita-Direita
        if fb < -1 and self._fb(no.dir) <= 0:
            return self._rot_esquerda(no)

        # Caso Direita-Esquerda
        if fb < -1 and self._fb(no.dir) > 0:
            no.dir = self._rot_direita(no.dir)
            return self._rot_esquerda(no)

        return no

    # ── inserção ──

    def inserir(self, registro: dict):
        self.raiz = self._inserir(self.raiz, registro)

    def _inserir(self, no, registro):
        if no is None:
            return NoAVL(registro)
        chave = registro["matricula"]
        if chave < no.registro["matricula"]:
            no.esq = self._inserir(no.esq, registro)
        elif chave > no.registro["matricula"]:
            no.dir = self._inserir(no.dir, registro)
        else:
            return no  # duplicata ignorada
        return self._balancear(no)

    # ── busca (idêntica à BST) ──

    def buscar(self, matricula: str):
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

    def altura(self):
        return self._altura(self.raiz)


# ─────────────────────────────────────────────
# LEITURA DO CSV
# ─────────────────────────────────────────────

def carregar_csv(caminho: str) -> list:
    registros = []
    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append(row)
    return registros


# ─────────────────────────────────────────────
# COLETA DE MÉTRICAS
# ─────────────────────────────────────────────

def medir_insercao(registros: list, usar_avl: bool):
    """Insere todos os registros na árvore escolhida e coleta métricas."""
    tracemalloc.start()
    inicio = time.perf_counter()

    arvore = AVL() if usar_avl else BST()
    for r in registros:
        arvore.inserir(r)

    fim = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return arvore, fim - inicio, pico / 1024


def medir_busca(arvore, chaves: list):
    """Executa buscas e coleta tempo, iterações e memória."""
    tracemalloc.start()
    inicio = time.perf_counter()

    iteracoes_lista = []
    for ch in chaves:
        _, it = arvore.buscar(ch)
        iteracoes_lista.append(it)

    fim = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return fim - inicio, statistics.mean(iteracoes_lista), pico / 1024


# ─────────────────────────────────────────────
# EXPERIMENTO: 5 RODADAS POR VOLUME E TIPO
# ─────────────────────────────────────────────

NUM_RODADAS = 5
NUM_BUSCAS  = 100

_BASE = os.path.join(os.path.dirname(__file__), "..", "..")
ARQUIVOS = {
    10_000:  os.path.join(_BASE, "datasets", "dados_10000.csv"),
    50_000:  os.path.join(_BASE, "datasets", "dados_50000.csv"),
    100_000: os.path.join(_BASE, "datasets", "dados_100000.csv"),
}


def rodar_experimento(N: int, caminho: str, usar_avl: bool):
    nome = "AVL (com balanceamento)" if usar_avl else "BST (sem balanceamento)"
    print(f"\n{'─'*60}")
    print(f"  {nome} | N = {N:,}")
    print(f"{'─'*60}")

    registros_base = carregar_csv(caminho)

    t_ins_list, m_ins_list, altura_list = [], [], []
    t_bus_list, it_list = [], []

    for rodada in range(1, NUM_RODADAS + 1):
        chaves = [r["matricula"] for r in random.sample(registros_base, NUM_BUSCAS)]

        # Inserção
        arvore, t_ins, m_ins = medir_insercao(registros_base, usar_avl)
        h = arvore.altura()
        t_ins_list.append(t_ins)
        m_ins_list.append(m_ins)
        altura_list.append(h)

        # Busca
        t_bus, media_it, _ = medir_busca(arvore, chaves)
        t_bus_list.append(t_bus)
        it_list.append(media_it)

        print(f"  Rodada {rodada}: ins={t_ins:.4f}s | mem={m_ins:.1f}KB | "
              f"altura={h} | busca={t_bus:.4f}s | iter={media_it:.1f}")

    print(f"\n  RESUMO (média ± desvio padrão):")
    print(f"  Inserção  : {statistics.mean(t_ins_list):.4f}s ± {statistics.stdev(t_ins_list):.4f}s")
    print(f"  Memória   : {statistics.mean(m_ins_list):.1f}KB ± {statistics.stdev(m_ins_list):.1f}KB")
    print(f"  Altura    : {statistics.mean(altura_list):.1f} ± {statistics.stdev(altura_list):.1f}")
    print(f"  Busca     : {statistics.mean(t_bus_list):.4f}s ± {statistics.stdev(t_bus_list):.4f}s")
    print(f"  Iterações : {statistics.mean(it_list):.1f} ± {statistics.stdev(it_list):.1f}")

    return {
        "estrutura":   nome,
        "N":           N,
        "t_ins_media": statistics.mean(t_ins_list),
        "t_ins_std":   statistics.stdev(t_ins_list),
        "mem_ins_kb":  statistics.mean(m_ins_list),
        "mem_ins_std": statistics.stdev(m_ins_list),
        "altura_media":statistics.mean(altura_list),
        "altura_std":  statistics.stdev(altura_list),
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

        # BST sem balanceamento
        res_bst = rodar_experimento(N, caminho, usar_avl=False)
        resultados.append(res_bst)

        # AVL com balanceamento
        res_avl = rodar_experimento(N, caminho, usar_avl=True)
        resultados.append(res_avl)

    # Salva CSV com todos os resultados
    campos = [
        "estrutura", "N",
        "t_ins_media", "t_ins_std",
        "mem_ins_kb",  "mem_ins_std",
        "altura_media","altura_std",
        "t_bus_media", "t_bus_std",
        "iter_media",  "iter_std",
    ]
    with open("resultados_arvores.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)

    print("\n\nResultados salvos em: resultados_arvores.csv")
    print("Experimento concluído!")