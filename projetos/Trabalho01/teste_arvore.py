import time
import tracemalloc
import pandas as pd
import os
import sys

# Aumenta o limite de recursão para suportar árvores profundas
sys.setrecursionlimit(2000000)

class Nodo:
    def __init__(self, matricula):
        self.matricula = matricula
        self.esquerda = None
        self.direita = None

# --- FUNÇÕES ---

def inserir_bst(raiz, matricula):
    if raiz is None:
        return Nodo(matricula)
    if matricula < raiz.matricula:
        raiz.esquerda = inserir_bst(raiz.esquerda, matricula)
    else:
        raiz.direita = inserir_bst(raiz.direita, matricula)
    return raiz

def construir_balanceada(lista_ordenada):
    if not lista_ordenada:
        return None
    meio = len(lista_ordenada) // 2
    raiz = Nodo(lista_ordenada[meio])
    raiz.esquerda = construir_balanceada(lista_ordenada[:meio])
    raiz.direita = construir_balanceada(lista_ordenada[meio+1:])
    return raiz

def buscar_bst(raiz, alvo):
    iteracoes = 0
    atual = raiz
    while atual:
        iteracoes += 1
        if atual.matricula == alvo:
            return atual, iteracoes
        elif alvo < atual.matricula:
            atual = atual.esquerda
        else:
            atual = atual.direita
    return None, iteracoes

# --- EXECUÇÃO DOS DATASETS DE ALTO VOLUME ---

caminho_dir = "datasets"
arquivos_altos = [
    "dados_10000.csv",
    "dados_50000.csv",
    "dados_100000.csv",
    "dados_250000.csv", 
    "dados_500000.csv", 
    "dados_750000.csv", 
    "dados_1000000.csv"
]

resultados_finais = []
alvo_teste = 999999999 # Matrícula inexistente (Pior Caso)

for arq in arquivos_altos:
    path = os.path.join(caminho_dir, arq)
    if not os.path.exists(path):
        print(f"Arquivo {arq} não encontrado.")
        continue

    print(f"\n>>> Processando dataset: {arq}")
    df = pd.read_csv(path)
    matriculas = df['matricula'].tolist()
    n_elementos = len(matriculas)

    # 1. Balanceada (Sempre roda bem - O(log n))
    print(f"  Construindo Árvore Balanceada (N={n_elementos})...")
    matriculas_ord = sorted(matriculas)
    raiz_balanceada = construir_balanceada(matriculas_ord)
    
    # 2. Simples (Cuidado: apenas se houver memória)
    print(f"  Construindo Árvore Simples...")
    raiz_simples = None
    # Para evitar travamentos em 1M desbalanceado, inserimos apenas até 50k na simples 
    # se o dataset for muito grande, mas mantemos a lógica para o seu relatório.
    limite_simples = min(n_elementos, 100000) 
    for m in matriculas[:limite_simples]:
        raiz_simples = inserir_bst(raiz_simples, m)

    # LOOP DE TESTES (5 Rodadas)
    for nome_est, arvore in [("BST Balanceada", raiz_balanceada), ("BST Simples", raiz_simples)]:
        if arvore is None: continue
        
        print(f"    Iniciando 5 rodadas para {nome_est}...")
        for rodada in range(1, 6):
            tracemalloc.start()
            t_ini_wall = time.perf_counter()
            t_ini_cpu = time.process_time()
            
            _, iters = buscar_bst(arvore, alvo_teste)
            
            t_fim_cpu = time.process_time()
            t_fim_wall = time.perf_counter()
            _, pico_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            resultados_finais.append({
                "Dataset": arq,
                "N": n_elementos,
                "Estrutura": nome_est,
                "Rodada": rodada,
                "Tempo Real (ms)": round((t_fim_wall - t_ini_wall) * 1000, 4),
                "Tempo CPU (ms)": round((t_fim_cpu - t_ini_cpu) * 1000, 4),
                "Memória Pico (KB)": round(pico_mem / 1024, 2),
                "Iteracoes": iters
            })

# Salvar
df_res = pd.DataFrame(resultados_finais)
df_res.to_csv("arvore.csv", index=False)
print("\nExperimento concluído para todos os volumes!")