
import sys
import os
import json
import numpy as np

# Caminho do Comic Translate
sys.path.insert(0, r"C:\Users\EDUARDO\Documents\comic-translate-main")

from PIL import Image
from modules.utils.file_handler import (
    FileHandler,
    ensure_prepared_path_materialized,
)
from modules.detection.ppocr_lines import PPOCRLineDetector
from modules.utils.textblock import TextBlock
from modules.ocr.ppocr.engine import PPOCRv5Engine


# ============================================================
# CONFIGURAÇÃO
# ============================================================

input_cbz = r"C:\Users\EDUARDO\Documents\Academy_of_card\Originais\Chapter 1_50ee76.cbz"

output_json = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_ocr.json"


# ============================================================
# 1. PREPARAR O CBZ
# ============================================================

print("=" * 60)
print("PREPARANDO CBZ")
print("=" * 60)

file_handler = FileHandler()

image_files = file_handler.prepare_files([input_cbz])

print(f"\nQuantidade de paginas: {len(image_files)}")


# ============================================================
# 2. INICIALIZAR DETECTOR
# ============================================================

print("\n" + "=" * 60)
print("INICIALIZANDO DETECTOR")
print("=" * 60)

detector = PPOCRLineDetector()

detector.initialize(
    device="cpu",
    backend="onnx",
    det_model="mobile"
)

print("Detector inicializado.")


# ============================================================
# 3. INICIALIZAR OCR
# ============================================================

print("\n" + "=" * 60)
print("INICIALIZANDO OCR")
print("=" * 60)

ocr_engine = PPOCRv5Engine()

ocr_engine.initialize(
    lang="en",
    device="cpu",
    use_text_lines=True
)

print("OCR inicializado.")


# ============================================================
# 4. LISTA QUE VAI GUARDAR TODOS OS RESULTADOS
# ============================================================

resultados = []


# ============================================================
# 5. PROCESSAR TODAS AS PÁGINAS
# ============================================================

print("\n" + "=" * 60)
print("PROCESSANDO PÁGINAS")
print("=" * 60)


for page_number, image_file in enumerate(image_files, start=1):

    print("\n")
    print("=" * 60)
    print(f"PÁGINA {page_number}/{len(image_files)}")
    print("=" * 60)

    # --------------------------------------------------------
    # Materializar página
    # --------------------------------------------------------

    print("Extraindo página do CBZ...")

    if not ensure_prepared_path_materialized(image_file):
        print("ERRO: não foi possível materializar:")
        print(image_file)
        continue

    # --------------------------------------------------------
    # Abrir imagem
    # --------------------------------------------------------

    try:
        img = Image.open(image_file)
        img.load()
    except Exception as e:
        print(f"ERRO ao abrir imagem: {e}")
        continue

    print(f"Imagem: {img.size}")
    print(f"Formato: {img.format}")
    print(f"Modo: {img.mode}")

    # --------------------------------------------------------
    # Converter para NumPy
    # --------------------------------------------------------

    image_np = np.array(img)

    # --------------------------------------------------------
    # DETECÇÃO
    # --------------------------------------------------------

    print("\nDetectando texto...")

    try:
        lines = detector.detect_lines(image_np)
    except Exception as e:
        print(f"ERRO na detecção: {e}")
        continue

    print(f"Linhas detectadas: {len(lines)}")

    # Estrutura da página
    pagina_resultado = {
        "pagina": page_number,
        "arquivo": os.path.basename(image_file),
        "largura": int(img.width),
        "altura": int(img.height),
        "blocos": []
    }

    if not lines:
        print("Nenhum texto detectado nesta página.")

        resultados.append(pagina_resultado)
        continue

    # --------------------------------------------------------
    # CRIAR TEXTBLOCKS
    # --------------------------------------------------------

    print("\nCriando TextBlocks...")

    blk_list = []

    for line in lines:

        blk = TextBlock(
            text_bbox=np.array(line),
            text_class="text_free",
            source_lang="en"
        )

        blk_list.append(blk)

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    print("Executando OCR...")

    try:
        ocr_engine.process_image(
            image_np,
            blk_list
        )
    except Exception as e:
        print(f"ERRO no OCR: {e}")
        continue

    # --------------------------------------------------------
    # GUARDAR RESULTADOS DOS BLOCOS
    # --------------------------------------------------------

    print("\n" + "-" * 60)
    print("TEXTO ENCONTRADO")
    print("-" * 60)

    for i, blk in enumerate(blk_list, start=1):

        texto = blk.text.strip()

        # Coordenadas da caixa
        bbox = [int(valor) for valor in blk.xyxy]

        bloco_resultado = {
            "caixa": i,
            "bbox": bbox,
            "texto": texto
        }

        pagina_resultado["blocos"].append(bloco_resultado)

        # Mostrar no terminal
        if texto:
            print(f"Caixa {i}: {texto!r}")
        else:
            print(f"Caixa {i}: [vazio]")

    print("-" * 60)

    # Adicionar página aos resultados
    resultados.append(pagina_resultado)


# ============================================================
# 6. SALVAR JSON
# ============================================================

print("\n")
print("=" * 60)
print("SALVANDO RESULTADOS")
print("=" * 60)

try:

    with open(
        output_json,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print(f"\nJSON salvo com sucesso:")
    print(output_json)

except Exception as e:

    print(f"ERRO ao salvar JSON: {e}")


# ============================================================
# FINAL
# ============================================================

print("\n")
print("=" * 60)
print("PROCESSAMENTO CONCLUÍDO")
print("=" * 60)

