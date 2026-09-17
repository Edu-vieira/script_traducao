
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

output_json = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_ocr_server.json"
OUTPUT_JSON = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_traduzido.json"


def traduzir(texto):
    prompt = f"""
Traduza o texto abaixo do inglês para português brasileiro.

Regras:
- Traduza somente o texto fornecido.
- Preserve o sentido original.
- Use português brasileiro natural.
- Não explique a tradução.
- Não coloque aspas.
- Não adicione comentários.

Texto:
{texto}
"""

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return dados["response"].strip()


print("=" * 60)
print("TRADUÇÃO DO OCR")
print("=" * 60)

print()
print(f"Arquivo de entrada: {INPUT_JSON}")
print(f"Arquivo de saída:   {OUTPUT_JSON}")
print(f"Modelo:             {MODEL}")

# ============================================================
# LER JSON DO OCR
# ============================================================

print()
print("Lendo resultado do OCR...")

try:
    with open(INPUT_JSON, "r", encoding="utf-8") as arquivo:
        resultados = json.load(arquivo)

except Exception as e:
    print(f"ERRO ao ler o JSON: {e}")
    raise SystemExit


print(f"Páginas encontradas: {len(resultados)}")

# ============================================================
# TRADUZIR
# ============================================================

total_blocos = sum(
    len(pagina.get("blocos", []))
    for pagina in resultados
)

blocos_processados = 0

print(f"Blocos encontrados: {total_blocos}")
print()
print("=" * 60)
print("INICIANDO TRADUÇÃO")
print("=" * 60)

for pagina in resultados:

    numero_pagina = pagina.get("pagina", "?")
    blocos = pagina.get("blocos", [])

    print()
    print("-" * 60)
    print(f"PÁGINA {numero_pagina}")
    print("-" * 60)

    for bloco in blocos:

        texto = bloco.get("texto", "").strip()

        # Se o OCR não encontrou texto, não envia para o Ollama.
        if not texto:
            bloco["traducao"] = ""
            blocos_processados += 1

            print(
                f"Caixa {bloco.get('caixa', '?')}: "
                "[vazio - ignorado]"
            )

            continue

        print()
        print(f"Caixa {bloco.get('caixa', '?')}")
        print(f"Original:   {texto}")

        try:
            traducao = traduzir(texto)

            bloco["traducao"] = traducao

            print(f"Tradução:   {traducao}")

        except requests.exceptions.ConnectionError:
            print()
            print("ERRO: não foi possível conectar ao Ollama.")
            print("Verifique se o Ollama está rodando.")
            raise SystemExit

        except Exception as e:
            print()
            print(f"ERRO ao traduzir esta caixa: {e}")

            # Mantém a estrutura do JSON mesmo se uma caixa falhar.
            bloco["traducao"] = ""

        blocos_processados += 1

        print(f"Progresso: {blocos_processados}/{total_blocos}")

# ============================================================
# SALVAR RESULTADO
# ============================================================

print()
print("=" * 60)
print("SALVANDO RESULTADO")
print("=" * 60)

try:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(
            resultados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print()
    print("JSON traduzido salvo com sucesso:")
    print(OUTPUT_JSON)

except Exception as e:
    print(f"ERRO ao salvar o JSON: {e}")
    raise SystemExit

print()
print("=" * 60)
print("TRADUÇÃO CONCLUÍDA")
print("=" * 60)

