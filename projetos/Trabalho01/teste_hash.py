import time
import tracemalloc
import pandas as pd
import os
import math
import statistics

# --- SUAS CLASSES AJUSTADAS ---

class Registro:
    def __init__(self, matricula, nome, salario, setor):
        self.matricula = int(matricula)
        self.nome = nome
        self.salario = salario
        self.setor = setor

class TabelaHash:
    def __init__(self, tamanho_m):
        self.M = tamanho_m
        self.tabela = [[] for _ in range(self.M)]
        self.elementos_inseridos = 0
        self.colisoes_totais = 0

    def _hash_divisao(self, chave):
        return chave % self.M

    def _hash_multiplicacao(self, chave):
        A = 0.6180339887
        return math.floor(self.M * ((chave * A) % 1))

    def _hash_meio_quadrado(self, chave):
        quadrado = chave * chave
        str_quadrado = str(quadrado)
        meio = len(str_quadrado) // 2
        if len(str_quadrado) >= 3:
            digitos_meio = int(str_quadrado[max(0, meio-1):meio+2])
        else:
            digitos_meio = int(str_quadrado)
        return digitos_meio % self.M

    def obter_indice(self, chave, tipo_hash):
        if tipo_hash == 1: return self._hash_divisao(chave)
        if tipo_hash == 2: return self._hash_multiplicacao(chave)
        if tipo_hash == 3: return self._hash_meio_quadrado(chave)
        return self._hash_divisao(chave)

    def inserir(self, registro, tipo_hash=1):
        indice = self.obter_indice(registro.matricula, tipo_hash)
        if len(self.tabela[indice]) > 0:
            self.colisoes_totais += 1
        self.tabela[indice].append(registro)
        self.elementos_inseridos += 1

    def buscar(self, matricula, tipo_hash=1):
        indice = self.obter_indice(matricula, tipo_hash)
        iteracoes = 0
        for registro in self.tabela[indice]:
            iteracoes += 1
            if registro.matricula == matricula:
                return registro, iteracoes
        return None, iteracoes

# --- MOTOR DE EXPERIMENTO ---

def rodar_experimento_hash(caminho_datasets, arquivos):
    relatorio_hash = []
    
    # Configuramos diferentes tamanhos de tabela para comparar (M)
    tamanhos_m = [10000, 100000, 500000]
    tipos_hash = {1: "Divisão", 2: "Multiplicação", 3: "Meio-Quadrado"}

    for arq in arquivos:
        path = os.path.join(caminho_datasets, arq)
        if not os.path.exists(path): continue

        print(f"\n>>> Dataset: {arq}")
        df = pd.read_csv(path)
        
        for m in tamanhos_m:
            for cod_hash, nome_hash in tipos_hash.items():
                
                # Criar e popular a tabela (uma vez para as 5 rodadas)
                minha_tabela = TabelaHash(m)
                for _, row in df.iterrows():
                    reg = Registro(row['matricula'], row['nome'], row['salario'], row['codigo_setor'])
                    minha_tabela.inserir(reg, tipo_hash=cod_hash)
                
                alvo = 999999999 # Pior caso (não existe)
                load_factor = minha_tabela.elementos_inseridos / m
                
                print(f"  Testando Hash {nome_hash} | M={m} | Load={load_factor:.2f}")

                for rodada in range(1, 6):
                    tracemalloc.start()
                    t_ini_wall = time.perf_counter()
                    t_ini_cpu = time.process_time()
                    
                    # Busca
                    _, iters = minha_tabela.buscar(alvo, tipo_hash=cod_hash)
                    
                    t_fim_cpu = time.process_time()
                    t_fim_wall = time.perf_counter()
                    _, pico_mem = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    relatorio_hash.append({
                        "Dataset": arq,
                        "N": len(df),
                        "M (Tamanho Tabela)": m,
                        "Função Hash": nome_hash,
                        "Load Factor": round(load_factor, 2),
                        "Rodada": rodada,
                        "Tempo Real (ms)": round((t_fim_wall - t_ini_wall) * 1000, 4),
                        "Tempo CPU (ms)": round((t_fim_cpu - t_ini_cpu) * 1000, 4),
                        "Memória Pico (KB)": round(pico_mem / 1024, 2),
                        "Iterações": iters,
                        "Colisões Totais": minha_tabela.colisoes_totais
                    })

    return relatorio_hash

# --- EXECUÇÃO ---
caminho_dir = "datasets"
arquivos_teste = [
    "dados_10000.csv", "dados_50000.csv", "dados_100000.csv",
    "dados_250000.csv", "dados_500000.csv", "dados_750000.csv", "dados_1000000.csv"
]

dados_finais = rodar_experimento_hash(caminho_dir, arquivos_teste)
pd.DataFrame(dados_finais).to_csv("hash.csv", index=False)
print("\nRelatório de Hash gerado em 'hash.csv'!")