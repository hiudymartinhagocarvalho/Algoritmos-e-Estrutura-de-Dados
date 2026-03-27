import time
import tracemalloc
import pandas as pd
import os

# --- ALGORITMOS ---

def busca_linear(arr, alvo):
    iteracoes = 0
    for i in range(len(arr)):
        iteracoes += 1
        if int(arr[i]['matricula']) == alvo:
            return i, iteracoes
    return -1, iteracoes

def busca_binaria(arr, alvo):
    baixo, alto = 0, len(arr) - 1
    iteracoes = 0
    while baixo <= alto:
        iteracoes += 1
        meio = (baixo + alto) // 2
        chute = int(arr[meio]['matricula'])
        if chute == alvo:
            return meio, iteracoes
        elif chute < alvo:
            baixo = meio + 1
        else:
            alto = meio - 1
    return -1, iteracoes

# --- MOTOR DE EXECUÇÃO DETALHADO ---

def executar_experimento(caminho_dir, arquivos):
    relatorio_detalhado = []
    alvo_inexistente = 999999999

    for arq in arquivos:
        path = os.path.join(caminho_dir, arq)
        if not os.path.exists(path):
            print(f"Arquivo {arq} não encontrado.")
            continue

        print(f"Lendo {arq}...")
        df = pd.read_csv(path)
        dados_lista = df.to_dict('records')
        n_elementos = len(dados_lista)

        # Preparação para Binária (ordenar fora do loop de tempo para medir apenas a BUSCA)
        dados_ordenados = sorted(dados_lista, key=lambda x: int(x['matricula']))

        for operacao, func, lista_uso in [("Linear", busca_linear, dados_lista), 
                                         ("Binária", busca_binaria, dados_ordenados)]:
            
            print(f"  Executando {operacao} (5 rodadas)...")
            
            for rodada in range(1, 6):
                # Limpa e inicia rastreadores
                tracemalloc.start()
                t_inicio_wall = time.perf_counter() # Tempo real (relógio de parede)
                t_inicio_cpu = time.process_time()   # Tempo de CPU (uso do processador)
                
                _, iters = func(lista_uso, alvo_inexistente)
                
                t_fim_cpu = time.process_time()
                t_fim_wall = time.perf_counter()
                _, pico_mem = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                # Adiciona cada rodada como uma linha individual no relatório
                relatorio_detalhado.append({
                    "Dataset": arq,
                    "N": n_elementos,
                    "Operação": operacao,
                    "Rodada": rodada,
                    "Tempo Real (ms)": round((t_fim_wall - t_inicio_wall) * 1000, 4),
                    "Tempo CPU (ms)": round((t_fim_cpu - t_inicio_cpu) * 1000, 4),
                    "Memória Pico (KB)": round(pico_mem / 1024, 2),
                    "Iterações": iters
                })

    return relatorio_detalhado

# --- CONFIGURAÇÃO E EXECUÇÃO ---

caminho_datasets = "datasets"
lista_arquivos = [
    "dados_10000.csv", "dados_50000.csv", "dados_100000.csv", 
    "dados_250000.csv", "dados_500000.csv", "dados_750000.csv", "dados_1000000.csv"
]

dados_finais = executar_experimento(caminho_datasets, lista_arquivos)

# Salvar em CSV detalhado
df_final = pd.DataFrame(dados_finais)
df_final.to_csv("array.csv", index=False)

# Exibir uma prévia da média para conferência rápida
print("\n--- RESUMO MÉDIO (Para conferência) ---")
resumo = df_final.groupby(['Dataset', 'Operação'])[['Tempo Real (ms)', 'Tempo CPU (ms)', 'Memória Pico (KB)']].mean()
print(resumo)

print("\nArquivo 'array.csv' gerado com sucesso!")