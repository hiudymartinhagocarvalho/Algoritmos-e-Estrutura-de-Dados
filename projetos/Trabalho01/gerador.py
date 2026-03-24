import csv
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path("datasets")
OUTPUT_DIR.mkdir(exist_ok=True)

TAMANHOS = [100_000,250_000, 500_000,750_000, 1_000_000, 5_000_000, 10_000_000]

NOMES = [
    "Ana", "Bruno", "Carlos", "Daniela", "Eduardo", "Fernanda", "Gabriel",
    "Helena", "Igor", "Juliana", "Karen", "Leonardo", "Mariana", "Nathan",
    "Otavio", "Paula", "Rafael", "Sabrina", "Tiago", "Vanessa", "Willian",
    "Yasmin", "Bianca", "Caio", "Diego", "Elisa", "Fabio", "Giovana",
    "Henrique", "Isabela", "Joao", "Larissa", "Mateus", "Nicole", "Pedro",
    "Renata", "Samuel", "Tatiane", "Vitor", "Aline", "Cecilia", "Douglas"
]

SOBRENOMES = [
    "Silva", "Souza", "Oliveira", "Santos", "Lima", "Costa", "Pereira",
    "Ferreira", "Rodrigues", "Almeida", "Nascimento", "Araujo", "Melo",
    "Carvalho", "Gomes", "Martins", "Rocha", "Barbosa", "Ribeiro", "Teixeira"
]

SETORES = [
    "ADM", "RH", "FIN", "TI", "COM", "LOG", "JUR", "MKT", "SUP", "OPER"
]

CIDADES = [
    "Curitiba", "Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre",
    "Florianopolis", "Londrina", "Maringa", "Campinas", "Joinville"
]


def gerar_nome():
    return f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"


def gerar_salario():
    return round(random.uniform(1800.0, 25000.0), 2)


def gerar_setor():
    return random.choice(SETORES)


def gerar_cidade():
    return random.choice(CIDADES)


def gerar_registro(matricula: int):
    return {
        "matricula": f"{matricula:09d}",
        "nome": gerar_nome(),
        "salario": gerar_salario(),
        "codigo_setor": gerar_setor(),
        "cidade": gerar_cidade(),
        "tempo_empresa_anos": random.randint(0, 35),
        "ativo": random.choice([0, 1])
    }


def salvar_csv(caminho_arquivo: Path, registros: list[dict]):
    campos = [
        "matricula",
        "nome",
        "salario",
        "codigo_setor",
        "cidade",
        "tempo_empresa_anos",
        "ativo"
    ]

    with open(caminho_arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros)


def gerar_matriculas_unicas(n: int):
    matriculas = list(range(n))   # 0 até n-1
    random.shuffle(matriculas)    # embaralha a ordem no CSV
    return matriculas


def gerar_dataset(n: int):
    matriculas = gerar_matriculas_unicas(n)

    registros = [
        gerar_registro(matricula)
        for matricula in matriculas
    ]

    nome_arquivo = OUTPUT_DIR / f"dados_{n}.csv"
    salvar_csv(nome_arquivo, registros)
    print(f"Arquivo gerado: {nome_arquivo}")


def main():
    for n in TAMANHOS:
        gerar_dataset(n)


if __name__ == "__main__":
    main()