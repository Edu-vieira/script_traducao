import sys
import os
import json
import numpy as np

from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

# ============================================================
# CAMINHO DO COMIC TRANSLATE
# ============================================================

sys.path.insert(
    0,
    r"C:\Users\EDUARDO\Documents\comic-translate-main"
)

# ============================================================
# IMPORTS NATIVOS DO COMIC TRANSLATE
# ============================================================

from PIL import Image

from modules.utils.file_handler import (
    FileHandler,
    ensure_prepared_path_materialized,
)

from modules.utils.textblock import TextBlock

from modules.utils.image_utils import (
    generate_mask,
    get_smart_text_color,
)

from modules.utils.translator_utils import (
    is_renderable_translation,
    format_translations,
)

from modules.utils.language_utils import (
    get_language_code,
    is_no_space_lang,
)

from modules.rendering.render import (
    get_best_render_area,
    pyside_word_wrap,
    is_vertical_block,
)

from modules.utils.pipeline_config import get_config

from pipeline.inpainting import (
    InpaintingHandler,
    call_inpaint_image,
)

from app.ui.canvas.text.text_item_properties import TextItemProperties
from app.ui.canvas.text_item import OutlineInfo, OutlineType
from app.ui.canvas.save_renderer import ImageSaveRenderer


# ============================================================
# CONFIGURAÇÃO
# ============================================================

INPUT_CBZ = (
    r"C:\Users\EDUARDO\Documents\Academy_of_card"
    r"\Originais\Chapter 1_50ee76.cbz"
)

INPUT_JSON = (
    r"C:\Users\EDUARDO\Documents\Academy_of_card"
    r"\resultado_traduzido.json"
)

OUTPUT_DIR = (
    r"C:\Users\EDUARDO\Documents\Academy_of_card"
    r"\Paginas_Traduzidas"
)

OUTPUT_CBZ = (
    r"C:\Users\EDUARDO\Documents\Academy_of_card"
    r"\Chapter 1_50ee76_traduzido.cbz"
)

# ============================================================
# CONFIGURAÇÕES DE RENDERIZAÇÃO
# ============================================================

SOURCE_LANG = "English"
TARGET_LANG = "Portuguese"

FONT_FAMILY = "Anime Ace"

MAX_FONT_SIZE = 40
MIN_FONT_SIZE = 10

LINE_SPACING = 1.2

OUTLINE = False
OUTLINE_WIDTH = 1.0
OUTLINE_COLOR = QColor(255, 255, 255)

TEXT_COLOR = QColor(0, 0, 0)

BOLD = False
ITALIC = False
UNDERLINE = False

ALIGNMENT = Qt.AlignmentFlag.AlignCenter
DIRECTION = Qt.LayoutDirection.LeftToRight

# ============================================================
# CONFIGURAÇÃO DO INPAINTER
# ============================================================

INPAINTER = "AOT"
USE_GPU = False

HD_STRATEGY = "Resize"
HD_RESIZE_LIMIT = 960
HD_CROP_MARGIN = 512
HD_CROP_TRIGGER_SIZE = 512


# ============================================================
# SETTINGS MÍNIMOS
# ============================================================
#
# O InpaintingHandler original recebe a SettingsPage do programa.
# Como não estamos abrindo a interface gráfica completa,
# fornecemos somente os métodos que o pipeline realmente usa.
#
# ============================================================

class FakeUI:
    @staticmethod
    def tr(text):
        return text


class FakeSettingsPage:

    def __init__(self):
        self.ui = FakeUI()

    def get_tool_selection(self, tool):
        if tool == "inpainter":
            return INPAINTER

        raise ValueError(
            f"Ferramenta não configurada: {tool}"
        )

    def is_gpu_enabled(self):
        return USE_GPU

    def get_hd_strategy_settings(self):
        return {
            "strategy": HD_STRATEGY,
            "resize_limit": HD_RESIZE_LIMIT,
            "crop_margin": HD_CROP_MARGIN,
            "crop_trigger_size": HD_CROP_TRIGGER_SIZE,
        }


class FakeMainPage:

    def __init__(self):
        self.settings_page = FakeSettingsPage()


# ============================================================
# FUNÇÃO PARA CRIAR TEXTBLOCK
# ============================================================

def criar_textblock(bloco_json):

    bbox = np.array(
        bloco_json["bbox"],
        dtype=np.int32
    )

    texto = bloco_json.get("texto", "").strip()

    traducao = bloco_json.get("traducao", "").strip()

    blk = TextBlock(
        text_bbox=bbox,
        bubble_bbox=None,
        text_class="text",
        text=texto,
        translation=traducao,
        source_lang="en",
        target_lang="pt",
    )

    return blk


# ============================================================
# FUNÇÃO PARA CONSTRUIR TEXT ITEMS
# ============================================================

def criar_text_items(
    blk_list,
    image,
):

    # Código nativo do Comic Translate.
    format_translations(
        blk_list,
        get_language_code(TARGET_LANG),
        upper_case=False,
    )

    # Código nativo para encontrar a melhor área de renderização.
    get_best_render_area(
        blk_list,
        image,
        image,
    )

    text_items_state = []

    for blk in blk_list:

        translation = blk.translation

        if not is_renderable_translation(translation):
            continue

        x1, y1, width, height = blk.xywh

        # Determina se deve usar escrita vertical.
        vertical = is_vertical_block(
            blk,
            get_language_code(TARGET_LANG)
        )

        # Word wrap e tamanho da fonte nativos.
        (
            translation,
            font_size,
            rendered_width,
            rendered_height,
        ) = pyside_word_wrap(
            translation,
            FONT_FAMILY,
            width,
            height,
            LINE_SPACING,
            OUTLINE_WIDTH,
            BOLD,
            ITALIC,
            UNDERLINE,
            ALIGNMENT,
            DIRECTION,
            MAX_FONT_SIZE,
            MIN_FONT_SIZE,
            vertical,
            is_no_space_lang(
                get_language_code(TARGET_LANG)
            ),
            return_metrics=True,
        )

        font_color = get_smart_text_color(
            blk.font_color,
            TEXT_COLOR,
        )

        text_props = TextItemProperties(
            text=translation,
            font_family=FONT_FAMILY,
            font_size=font_size,
            text_color=font_color,
            alignment=ALIGNMENT,
            line_spacing=LINE_SPACING,
            outline_color=(
                OUTLINE_COLOR
                if OUTLINE
                else None
            ),
            outline_width=OUTLINE_WIDTH,
            bold=BOLD,
            italic=ITALIC,
            underline=UNDERLINE,
            position=(x1, y1),
            rotation=blk.angle,
            scale=1.0,
            transform_origin=blk.tr_origin_point,
            width=rendered_width,
            height=rendered_height,
            direction=DIRECTION,
            vertical=vertical,
            selection_outlines=[
                OutlineInfo(
                    0,
                    len(translation),
                    OUTLINE_COLOR,
                    OUTLINE_WIDTH,
                    OutlineType.Full_Document,
                )
            ] if OUTLINE else [],
        )

        text_items_state.append(
            text_props.to_dict()
        )

    return text_items_state


# ============================================================
# SALVAR CBZ
# ============================================================

def criar_cbz(pasta, arquivo_saida):

    import zipfile

    arquivos = sorted(
        [
            nome
            for nome in os.listdir(pasta)
            if nome.lower().endswith(
                (".jpg", ".jpeg", ".png", ".webp")
            )
        ]
    )

    print()
    print("=" * 60)
    print("CRIANDO CBZ")
    print("=" * 60)

    print(f"Páginas: {len(arquivos)}")

    with zipfile.ZipFile(
        arquivo_saida,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as cbz:

        for nome in arquivos:

            caminho = os.path.join(
                pasta,
                nome
            )

            cbz.write(
                caminho,
                arcname=nome
            )

            print(f"Adicionada: {nome}")

    print()
    print("CBZ criado:")
    print(arquivo_saida)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("COMIC TRANSLATE - RENDERIZAÇÃO")
    print("=" * 60)

    # --------------------------------------------------------
    # QT
    # --------------------------------------------------------

    app = QtWidgets.QApplication.instance()

    if app is None:
        app = QtWidgets.QApplication(
            sys.argv
        )

    # --------------------------------------------------------
    # LER JSON
    # --------------------------------------------------------

    print()
    print("Lendo resultado da tradução...")

    try:

        with open(
            INPUT_JSON,
            "r",
            encoding="utf-8",
        ) as arquivo:

            resultados = json.load(
                arquivo
            )

    except Exception as e:

        print(
            f"ERRO ao ler JSON: {e}"
        )

        return

    print(
        f"Páginas encontradas: "
        f"{len(resultados)}"
    )

    # --------------------------------------------------------
    # PREPARAR CBZ
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("PREPARANDO CBZ")
    print("=" * 60)

    file_handler = FileHandler()

    image_files = (
        file_handler.prepare_files(
            [INPUT_CBZ]
        )
    )

    print(
        f"Páginas extraídas: "
        f"{len(image_files)}"
    )

    # --------------------------------------------------------
    # INPAINTER
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("INICIALIZANDO INPAINTER")
    print("=" * 60)

    fake_main = FakeMainPage()

    inpainting_handler = InpaintingHandler(
        fake_main
    )

    config = get_config(
        fake_main.settings_page
    )

    print(
        f"Inpainter: {INPAINTER}"
    )

    print(
        f"GPU: {USE_GPU}"
    )

    print(
        f"HD Strategy: {HD_STRATEGY}"
    )

    # --------------------------------------------------------
    # OUTPUT
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # PÁGINAS
    # --------------------------------------------------------

    for pagina_index, pagina in enumerate(
        resultados
    ):

        pagina_numero = pagina.get(
            "pagina",
            pagina_index + 1
        )

        print()
        print("=" * 60)
        print(
            f"PÁGINA "
            f"{pagina_numero}/"
            f"{len(resultados)}"
        )
        print("=" * 60)

        # ----------------------------------------------------
        # ENCONTRAR IMAGEM
        # ----------------------------------------------------

        if pagina_index >= len(
            image_files
        ):

            print(
                "ERRO: não existe imagem "
                "correspondente."
            )

            continue

        image_file = image_files[
            pagina_index
        ]

        if not ensure_prepared_path_materialized(
            image_file
        ):

            print(
                "ERRO ao materializar:"
            )

            print(image_file)

            continue

        # ----------------------------------------------------
        # ABRIR IMAGEM
        # ----------------------------------------------------

        try:

            image_pil = Image.open(
                image_file
            )

            image_pil.load()

            image = np.array(
                image_pil.convert("RGB")
            )

        except Exception as e:

            print(
                f"ERRO ao abrir imagem: {e}"
            )

            continue

        print(
            f"Imagem: {image.shape[1]}x"
            f"{image.shape[0]}"
        )

        # ----------------------------------------------------
        # RECONSTRUIR TEXTBLOCKS
        # ----------------------------------------------------

        blocos_json = pagina.get(
            "blocos",
            []
        )

        blk_list = []

        for bloco_json in blocos_json:

            texto = bloco_json.get(
                "texto",
                ""
            ).strip()

            traducao = bloco_json.get(
                "traducao",
                ""
            ).strip()

            if not texto:
                continue

            blk = criar_textblock(
                bloco_json
            )

            blk_list.append(
                blk
            )

            print(
                f"Texto: {texto!r}"
            )

            print(
                f"Tradução: "
                f"{traducao!r}"
            )

        print(
            f"Blocos reconstruídos: "
            f"{len(blk_list)}"
        )

        if not blk_list:

            print(
                "Nenhum bloco para "
                "processar."
            )

            continue

        # ----------------------------------------------------
        # FILTRAR BLOCOS PARA INPAINTING
        # ----------------------------------------------------

        inpaint_blk_list = [
            blk
            for blk in blk_list
            if (
                blk.text
                and blk.text.strip()
                and blk.translation
                and blk.translation.strip()
                and is_renderable_translation(
                    blk.translation
                )
            )
        ]

        print()
        print(
            "Blocos para inpainting: "
            f"{len(inpaint_blk_list)}"
        )

        # ----------------------------------------------------
        # GERAR MÁSCARA
        # ----------------------------------------------------

        print(
            "Gerando máscara..."
        )

        mask = generate_mask(
            image,
            inpaint_blk_list
        )

        print(
            f"Máscara gerada: "
            f"{mask.shape}"
        )

        # ----------------------------------------------------
        # INPAINTING NATIVO
        # ----------------------------------------------------

        print(
            "Executando inpainting..."
        )

        inpainted_image = (
            call_inpaint_image(
                inpainting_handler,
                image,
                mask,
                config,
                blk_list=inpaint_blk_list,
            )
        )

        print(
            "Inpainting concluído."
        )

        # ----------------------------------------------------
        # RENDERIZAÇÃO DOS TEXTOS
        # ----------------------------------------------------

        print(
            "Preparando textos..."
        )

        text_items_state = (
            criar_text_items(
                blk_list,
                image,
            )
        )

        print(
            f"Text items: "
            f"{len(text_items_state)}"
        )

        # ----------------------------------------------------
        # RENDER NATIVO
        # ----------------------------------------------------

        print(
            "Renderizando página..."
        )

        renderer = ImageSaveRenderer(
            inpainted_image
        )

        renderer.add_state_to_image(
            {
                "text_items_state":
                    text_items_state
            }
        )

        final_image = (
            renderer.render_to_image()
        )

        # ----------------------------------------------------
        # SALVAR
        # ----------------------------------------------------

        nome_saida = (
            f"{pagina_index + 1:04d}.png"
        )

        caminho_saida = os.path.join(
            OUTPUT_DIR,
            nome_saida
        )

        Image.fromarray(
            final_image
        ).save(
            caminho_saida
        )

        print(
            f"Página salva: "
            f"{caminho_saida}"
        )

    # --------------------------------------------------------
    # CRIAR CBZ
    # --------------------------------------------------------

    criar_cbz(
        OUTPUT_DIR,
        OUTPUT_CBZ
    )

    print()
    print("=" * 60)
    print("PROCESSO CONCLUÍDO")
    print("=" * 60)

    print()
    print(
        "CBZ final:"
    )

    print(
        OUTPUT_CBZ
    )


if __name__ == "__main__":
    main()