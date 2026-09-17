import sys
import os
import json
import numpy as np

sys.path.insert(0, r"C:\Users\EDUARDO\Documents\comic-translate-main")

from PIL import Image
from modules.utils.file_handler import (
    FileHandler,
    ensure_prepared_path_materialized,
)
from modules.detection.rtdetr_v2_onnx import RTDetrV2ONNXDetection
from modules.ocr.ppocr.engine import PPOCRv5Engine


INPUT_CBZ = r"C:\Users\EDUARDO\Documents\Academy_of_card\Originais\Chapter 1_50ee76.cbz"
OUTPUT_JSON = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_ocr.json"

CONFIDENCE = 0.25


print("=" * 60)
print("PREPARANDO CBZ")
print("=" * 60)

file_handler = FileHandler()
image_files = file_handler.prepare_files([INPUT_CBZ])

print(f"\nQuantidade de paginas: {len(image_files)}")


print("\n" + "=" * 60)
print("INICIALIZANDO RT-DETR-v2")
print("=" * 60)

detector = RTDetrV2ONNXDetection()

detector.initialize(
    device="cpu",
    confidence_threshold=CONFIDENCE
)

print(f"Confiança mínima: {CONFIDENCE}")


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


resultados = []


print("\n" + "=" * 60)
print("PROCESSANDO PÁGINAS")
print("=" * 60)


for page_number, image_file in enumerate(image_files, start=1):

    print("\n")
    print("=" * 60)
    print(f"PÁGINA {page_number}/{len(image_files)}")
    print("=" * 60)

    print("Extraindo página do CBZ...")

    if not ensure_prepared_path_materialized(image_file):
        print("ERRO: não foi possível materializar:")
        print(image_file)
        continue

    try:
        img = Image.open(image_file)
        img.load()
    except Exception as e:
        print(f"ERRO ao abrir imagem: {e}")
        continue

    print(f"Imagem: {img.size}")

    image_np = np.array(img)

    print("\nDetectando texto...")

    try:
        blk_list = detector.detect(image_np)
    except Exception as e:
        print(f"ERRO na detecção: {e}")
        continue

    print(f"Blocos detectados: {len(blk_list)}")

    if blk_list:

        print("\nExecutando OCR...")

        try:
            ocr_engine.process_image(
                image_np,
                blk_list
            )
        except Exception as e:
            print(f"ERRO no OCR: {e}")
            continue

    pagina_resultado = {
        "pagina": page_number,
        "arquivo": os.path.basename(image_file),
        "largura": int(img.width),
        "altura": int(img.height),
        "blocos": []
    }

    print("\n" + "-" * 60)
    print("TEXTO ENCONTRADO")
    print("-" * 60)

    for i, blk in enumerate(blk_list, start=1):

        texto = blk.text.strip()

        bbox = [
            int(valor)
            for valor in blk.xyxy
        ]

        bloco_resultado = {
            "caixa": i,
            "bbox": bbox,
            "texto": texto
        }

        pagina_resultado["blocos"].append(
            bloco_resultado
        )

        if texto:
            print(f"Caixa {i}: {texto!r}")
        else:
            print(f"Caixa {i}: [vazio]")

    print("-" * 60)

    resultados.append(pagina_resultado)


print("\n")
print("=" * 60)
print("SALVANDO RESULTADOS")
print("=" * 60)

try:

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print("\nJSON salvo com sucesso:")
    print(OUTPUT_JSON)

except Exception as e:

    print(f"ERRO ao salvar JSON: {e}")
    raise SystemExit


print("\n")
print("=" * 60)
print("DETECÇÃO + OCR CONCLUÍDOS")
print("=" * 60)