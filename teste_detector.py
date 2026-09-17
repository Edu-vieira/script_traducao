import sys
import os
import numpy as np

sys.path.insert(0, r"C:\Users\EDUARDO\Documents\comic-translate-main")

from PIL import Image, ImageDraw
from modules.utils.file_handler import (
    FileHandler,
    ensure_prepared_path_materialized,
)
from modules.detection.ppocr_lines import PPOCRLineDetector


INPUT_CBZ = r"C:\Users\EDUARDO\Documents\Academy_of_card\Originais\Chapter 1_50ee76.cbz"

OUTPUT_DIR = r"C:\Users\EDUARDO\Documents\Academy_of_card\debug_detector"

# Páginas que queremos testar
PAGES = [2, 3, 5]

# Thresholds que queremos comparar
THRESHOLDS = [0.85, 0.887, 0.898]


os.makedirs(OUTPUT_DIR, exist_ok=True)


print("=" * 60)
print("PREPARANDO CBZ")
print("=" * 60)

file_handler = FileHandler()
image_files = file_handler.prepare_files([INPUT_CBZ])

print(f"Quantidade de páginas: {len(image_files)}")


for page_number in PAGES:

    print("\n" + "=" * 60)
    print(f"PÁGINA {page_number}")
    print("=" * 60)

    image_file = image_files[page_number - 1]

    if not ensure_prepared_path_materialized(image_file):
        print("ERRO: não foi possível materializar a página.")
        continue

    try:
        img = Image.open(image_file)
        img.load()
    except Exception as e:
        print(f"ERRO ao abrir imagem: {e}")
        continue

    image_np = np.array(img)

    print(f"Imagem: {img.size}")

    for box_thresh in THRESHOLDS:

        print("\n" + "-" * 60)
        print(f"Threshold: {box_thresh}")
        print("-" * 60)

        detector = PPOCRLineDetector()

        detector.initialize(
            device="cpu",
            backend="onnx",
            det_model="mobile"
        )

        detector.post.thresh = 0.3
        detector.post.box_thresh = box_thresh

        try:
            lines = detector.detect_lines(image_np)
        except Exception as e:
            print(f"ERRO na detecção: {e}")
            continue

        print(f"Caixas detectadas: {len(lines)}")

        # Criar cópia da imagem para desenhar as caixas
        imagem_debug = img.convert("RGB").copy()
        draw = ImageDraw.Draw(imagem_debug)

        for line in lines:
            x1, y1, x2, y2 = [int(v) for v in line]

            draw.rectangle(
                [x1, y1, x2, y2],
                outline="red",
                width=3
            )

        nome_saida = (
            f"pagina_{page_number}_"
            f"thresh_{box_thresh:.2f}.png"
        )

        caminho_saida = os.path.join(
            OUTPUT_DIR,
            nome_saida
        )

        imagem_debug.save(caminho_saida)

        print(f"Salvo: {caminho_saida}")


print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)