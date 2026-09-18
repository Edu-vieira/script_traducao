
import os
import json

from detector import processar_capitulo
from tradutor import processar_traducao
from main import processar_capitulo as renderizar_capitulo


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = r"C:\Users\EDUARDO\Documents\Academy_of_card"

ORIGINAIS_DIR = os.path.join(BASE_DIR, "Originais")
TRADUZIDOS_DIR = os.path.join(BASE_DIR, "Traduzidos")

# Arquivos temporários
OCR_JSON = os.path.join(BASE_DIR, "resultado_ocr.json")
TRADUCAO_JSON = os.path.join(BASE_DIR, "resultado_traduzido.json")

# Pasta temporária usada pelo main.py para as páginas renderizadas
PAGINAS_DIR = os.path.join(BASE_DIR, "Paginas_Traduzidas")


# ============================================================
# PROCESSAMENTO DE UM CAPÍTULO
# ============================================================

def processar_um_capitulo(input_cbz):
    nome_arquivo = os.path.basename(input_cbz)
    nome_sem_extensao = os.path.splitext(nome_arquivo)[0]

    output_cbz = os.path.join(
        TRADUZIDOS_DIR,
        nome_sem_extensao + ".cbz"
    )

    print()
    print("=" * 70)
    print(f"PROCESSANDO: {nome_arquivo}")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. OCR / DETECÇÃO
    # --------------------------------------------------------

    print()
    print("[1/3] Detectando e extraindo textos...")

    processar_capitulo(
        input_cbz,
        OCR_JSON
    )

    print("OK - OCR concluído.")

    # --------------------------------------------------------
    # 2. TRADUÇÃO
    # --------------------------------------------------------

    print()
    print("[2/3] Traduzindo textos...")

    processar_traducao(
        OCR_JSON,
        TRADUCAO_JSON
    )

    print("OK - Tradução concluída.")

    # --------------------------------------------------------
    # 3. RENDERIZAÇÃO
    # --------------------------------------------------------

    print()
    print("[3/3] Apagando texto original e inserindo tradução...")

    renderizar_capitulo(
        input_cbz,
        TRADUCAO_JSON,
        PAGINAS_DIR,
        output_cbz
    )

    print("OK - Capítulo finalizado.")

    return output_cbz


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    # Cria a pasta Traduzidos caso ainda não exista
    os.makedirs(TRADUZIDOS_DIR, exist_ok=True)

    # Procura os CBZ originais
    arquivos = [
        os.path.join(ORIGINAIS_DIR, arquivo)
        for arquivo in os.listdir(ORIGINAIS_DIR)
        if arquivo.lower().endswith(".cbz")
    ]

    # Ordena alfabeticamente
    arquivos.sort()

    if not arquivos:
        print("Nenhum arquivo .cbz encontrado em Originais.")
        return

    print("=" * 70)
    print("AUTOMATIZADOR DE TRADUÇÃO")
    print("=" * 70)
    print()
    print(f"Capítulos encontrados: {len(arquivos)}")
    print()

    for numero, input_cbz in enumerate(arquivos, start=1):

        print()
        print("#" * 70)
        print(f"CAPÍTULO {numero}/{len(arquivos)}")
        print("#" * 70)

        try:
            output_cbz = processar_um_capitulo(input_cbz)

            print()
            print(f"CONCLUÍDO: {os.path.basename(output_cbz)}")

        except Exception as erro:

            print()
            print("!" * 70)
            print(f"ERRO AO PROCESSAR: {os.path.basename(input_cbz)}")
            print(f"Detalhes: {erro}")
            print("!" * 70)

            print()
            print("O próximo capítulo não será iniciado automaticamente.")
            print("Corrija o problema antes de continuar.")

            raise

    print()
    print("=" * 70)
    print("TODOS OS CAPÍTULOS FORAM PROCESSADOS!")
    print("=" * 70)


if __name__ == "__main__":
    main()

