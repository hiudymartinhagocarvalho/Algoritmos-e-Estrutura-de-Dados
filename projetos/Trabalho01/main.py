"""
main.py
───────
Ponto de entrada único. Executa todos os experimentos em ordem:
  1. Array Linear  (busca sequencial + binária)
  2. BST           (sem balanceamento)
  3. AVL           (com balanceamento)

Salva os resultados em:
  - resultados_array.csv
  - resultados_arvores.csv

Requisitos:
  pip install psutil
"""

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
from arvore       import rodar_experimento as exp_arvore
from hash         import rodar_experimento as exp_hash

_BASE = os.path.dirname(__file__)
ARQUIVOS = {
    10_000:  os.path.join(_BASE, "datasets", "dados_10000.csv"),
    50_000:  os.path.join(_BASE, "datasets", "dados_50000.csv"),
    100_000:  os.path.join(_BASE, "datasets", "dados_100000.csv"),
    250_000:  os.path.join(_BASE, "datasets", "dados_250000.csv"),
    500_000: os.path.join(_BASE, "datasets", "dados_500000.csv"),
    750_000: os.path.join(_BASE, "datasets", "dados_750000.csv"),
    1_000_000: os.path.join(_BASE, "datasets", "dados_1000000.csv"),
}

def main():
    res_array   = []
    res_arvores = []
    res_hash    = []

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

        # ── 4. Tabela Hash (3 funções × 3 valores de M) ───────
        res_hash.extend(exp_hash(N, caminho))

    # ── Salva CSVs ────────────────────────────────────────────
    if res_array:
        salvar_csv("resultados_array.csv", res_array)
        print("\nResultados salvos em: resultados_array.csv")

    if res_arvores:
        salvar_csv("resultados_arvores.csv", res_arvores)
        print("Resultados salvos em: resultados_arvores.csv")

    if res_hash:
        salvar_csv("resultados_hash.csv", res_hash)
        print("Resultados salvos em: resultados_hash.csv")

    print("\n✓ Experimento concluído!")


if __name__ == "__main__":
    main()