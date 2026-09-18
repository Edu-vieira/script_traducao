
import os
import json
import shutil

from detector import processar_capitulo
from tradutor import processar_traducao
from main import processar_capitulo as renderizar_capitulo


# ============================================================
# CONFIGURAÇÃO
# ============================================================

# A pasta da obra é automaticamente a pasta
# onde este automatizar.py está localizado.

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ORIGINAIS_DIR = os.path.join(
    BASE_DIR,
    "Originais"
)

TRADUZIDOS_DIR = os.path.join(
    BASE_DIR,
    "Traduzidos"
)

# Arquivos temporários
OCR_JSON = os.path.join(
    BASE_DIR,
    "resultado_ocr.json"
)

TRADUCAO_JSON = os.path.join(
    BASE_DIR,
    "resultado_traduzido.json"
)

# Pasta temporária usada pelo main.py
PAGINAS_DIR = os.path.join(
    BASE_DIR,
    "Paginas_Traduzidas"
)


# ============================================================
# LIMPEZA DOS ARQUIVOS TEMPORÁRIOS
# ============================================================

def limpar_temporarios():

    # --------------------------------------------------------
    # Remove o JSON do OCR
    # --------------------------------------------------------

    if os.path.exists(OCR_JSON):

        os.remove(OCR_JSON)

        print(
            "  - resultado_ocr.json removido."
        )

    # --------------------------------------------------------
    # Remove o JSON da tradução
    # --------------------------------------------------------

    if os.path.exists(TRADUCAO_JSON):

        os.remove(TRADUCAO_JSON)

        print(
            "  - resultado_traduzido.json removido."
        )

    # --------------------------------------------------------
    # Limpa as páginas renderizadas
    # --------------------------------------------------------

    if os.path.exists(PAGINAS_DIR):

        shutil.rmtree(
            PAGINAS_DIR
        )

        print(
            "  - Paginas_Traduzidas removida."
        )

    # Recria a pasta vazia
    os.makedirs(
        PAGINAS_DIR,
        exist_ok=True
    )


# ============================================================
# PROCESSAMENTO DE UM CAPÍTULO
# ============================================================

def processar_um_capitulo(
    input_cbz
):

    nome_arquivo = os.path.basename(
        input_cbz
    )

    nome_sem_extensao = os.path.splitext(
        nome_arquivo
    )[0]

    output_cbz = os.path.join(
        TRADUZIDOS_DIR,
        nome_sem_extensao + ".cbz"
    )

    print()
    print("=" * 70)
    print(
        f"PROCESSANDO: {nome_arquivo}"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Limpa qualquer sobra de uma execução anterior
    # --------------------------------------------------------

    print()
    print(
        "Limpando arquivos temporários anteriores..."
    )

    limpar_temporarios()

    # --------------------------------------------------------
    # 1. OCR / DETECÇÃO
    # --------------------------------------------------------

    print()
    print(
        "[1/3] Detectando e extraindo textos..."
    )

    processar_capitulo(
        input_cbz,
        OCR_JSON
    )

    print(
        "OK - OCR concluído."
    )

    # --------------------------------------------------------
    # 2. TRADUÇÃO
    # --------------------------------------------------------

    print()
    print(
        "[2/3] Traduzindo textos..."
    )

    processar_traducao(
        OCR_JSON,
        TRADUCAO_JSON
    )

    print(
        "OK - Tradução concluída."
    )

    # --------------------------------------------------------
    # 3. RENDERIZAÇÃO
    # --------------------------------------------------------

    print()
    print(
        "[3/3] Apagando texto original "
        "e inserindo tradução..."
    )

    renderizar_capitulo(
        input_cbz,
        TRADUCAO_JSON,
        PAGINAS_DIR,
        output_cbz
    )

    print(
        "OK - Capítulo finalizado."
    )

    # --------------------------------------------------------
    # CONFIRMAR CBZ
    # --------------------------------------------------------

    if not os.path.exists(
        output_cbz
    ):

        raise RuntimeError(
            "O CBZ final não foi encontrado. "
            "Os arquivos temporários não serão apagados."
        )

    print()
    print(
        "CBZ final confirmado."
    )

    # --------------------------------------------------------
    # LIMPEZA
    # --------------------------------------------------------

    print()
    print(
        "Limpando arquivos temporários..."
    )

    limpar_temporarios()

    print(
        "OK - Limpeza concluída."
    )

    return output_cbz


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    # Cria Traduzidos caso ainda não exista
    os.makedirs(
        TRADUZIDOS_DIR,
        exist_ok=True
    )

    # Procura os CBZ originais
    arquivos = [
        os.path.join(
            ORIGINAIS_DIR,
            arquivo
        )
        for arquivo in os.listdir(
            ORIGINAIS_DIR
        )
        if arquivo.lower().endswith(
            ".cbz"
        )
    ]

    # Ordena alfabeticamente
    arquivos.sort()

    if not arquivos:

        print(
            "Nenhum arquivo .cbz "
            "encontrado em Originais."
        )

        return

    print("=" * 70)
    print(
        "AUTOMATIZADOR DE TRADUÇÃO"
    )
    print("=" * 70)

    print()

    print(
        f"Pasta da obra: {BASE_DIR}"
    )

    print(
        f"Capítulos encontrados: "
        f"{len(arquivos)}"
    )

    print()

    for numero, input_cbz in enumerate(
        arquivos,
        start=1
    ):

        print()
        print(
            "#" * 70
        )

        print(
            f"CAPÍTULO "
            f"{numero}/{len(arquivos)}"
        )

        print(
            "#" * 70
        )

        try:

            output_cbz = (
                processar_um_capitulo(
                    input_cbz
                )
            )

            print()

            print(
                f"CONCLUÍDO: "
                f"{os.path.basename(output_cbz)}"
            )

        except Exception as erro:

            print()

            print(
                "!" * 70
            )

            print(
                f"ERRO AO PROCESSAR: "
                f"{os.path.basename(input_cbz)}"
            )

            print(
                f"Detalhes: {erro}"
            )

            print(
                "!" * 70
            )

            print()

            print(
                "Os arquivos temporários "
                "NÃO serão apagados"
            )

            print(
                "para permitir a investigação "
                "do erro."
            )

            print()

            print(
                "O próximo capítulo não será "
                "iniciado automaticamente."
            )

            raise

    print()

    print(
        "=" * 70
    )

    print(
        "TODOS OS CAPÍTULOS "
        "FORAM PROCESSADOS!"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()

