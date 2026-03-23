import os
import sys

# ── verifica dependência antes de qualquer import interno ──
try:
    import psutil  # noqa: F401
except ImportError:
    print("[ERRO] Instale psutil antes de executar:")
    print("       pip install psutil")
    sys.exit(1)

from monitor      import salvar_csv
from array_linear import rodar_experimento as exp_array
from arvore      import rodar_experimento as exp_arvore


# ─────────────────────────────────────────────
# CONFIGURAÇÃO DOS VOLUMES
# ─────────────────────────────────────────────

_BASE = os.path.join(os.path.dirname(__file__), "..", "..")
ARQUIVOS = {
    10_000:  os.path.join(_BASE, "datasets", "dados_10000.csv"),
    50_000:  os.path.join(_BASE, "datasets", "dados_50000.csv"),
    100_000: os.path.join(_BASE, "datasets", "dados_100000.csv"),
}


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    res_array   = []
    res_arvores = []

    for N, caminho in ARQUIVOS.items():
        if not os.path.exists(caminho):
            print(f"[AVISO] Arquivo não encontrado: {caminho}")
            continue

        # ── 1. Array Linear ───────────────────────────────────
        res_array.append(exp_array(N, caminho))

        # ── 2. BST (sem balanceamento) ────────────────────────
        res_arvores.append(exp_arvore(N, caminho, usar_avl=False))

        # ── 3. AVL (com balanceamento) ────────────────────────
        res_arvores.append(exp_arvore(N, caminho, usar_avl=True))

    # ── Salva CSVs ────────────────────────────────────────────
    if res_array:
        salvar_csv("resultados_array.csv", res_array)
        print("\nResultados salvos em: resultados_array.csv")

    if res_arvores:
        salvar_csv("resultados_arvores.csv", res_arvores)
        print("Resultados salvos em: resultados_arvores.csv")

    print("\n✓ Experimento concluído!")


if __name__ == "__main__":
    main()