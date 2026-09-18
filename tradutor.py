# Traduza somente quando houver conteúdo linguístico que possa ser traduzido.

# Se a entrada for apenas símbolos, pontuação, números, letras isoladas,
# onomatopeias não traduzíveis ou qualquer outro conteúdo que não exija
# tradução, reproduza exatamente a entrada original.

# Nunca responda pedindo mais texto.
# Nunca explique o que recebeu.
# Nunca diga que não há texto para traduzir.

# Entrada:
import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "guinogueira/ffxiv-pt-hy-mt2:7b-q5_K_M"

INPUT_JSON = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_ocr.json"

OUTPUT_JSON = r"C:\Users\EDUARDO\Documents\Academy_of_card\resultado_traduzido.json"


def traduzir(texto):

    prompt = f"""Traduza o texto abaixo do inglês para português brasileiro.

Regras:

- Traduza somente o texto fornecido.
- Preserve o sentido original.
- Use português brasileiro natural.
- Use uma linguagem brasileira informal.
- Não explique a tradução.
- Não coloque aspas.
- Não adicione comentários.
- Caso haja texto entre '()', '[]' ou chaves, traduza mantendo esses caracteres.


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

print(f"\nArquivo de entrada: {INPUT_JSON}")
print(f"Arquivo de saída:   {OUTPUT_JSON}")
print(f"Modelo:             {MODEL}")


print("\nLendo resultado do OCR...")

try:

    with open(
        INPUT_JSON,
        "r",
        encoding="utf-8"
    ) as arquivo:

        resultados = json.load(arquivo)

except Exception as e:

    print(f"ERRO ao ler o JSON: {e}")
    raise SystemExit


print(f"Páginas encontradas: {len(resultados)}")


total_blocos = sum(
    len(pagina.get("blocos", []))
    for pagina in resultados
)

blocos_processados = 0

print(f"Blocos encontrados: {total_blocos}")


print("\n" + "=" * 60)
print("INICIANDO TRADUÇÃO")
print("=" * 60)


for pagina in resultados:

    numero_pagina = pagina.get("pagina", "?")

    blocos = pagina.get("blocos", [])

    print("\n")
    print("-" * 60)
    print(f"PÁGINA {numero_pagina}")
    print("-" * 60)

    for bloco in blocos:

        texto = bloco.get("texto", "").strip()

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

            bloco["traducao"] = ""

        blocos_processados += 1

        print(
            f"Progresso: "
            f"{blocos_processados}/{total_blocos}"
        )


print("\n")
print("=" * 60)
print("SALVANDO RESULTADO")
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

    print("\nJSON traduzido salvo com sucesso:")
    print(OUTPUT_JSON)

except Exception as e:

    print(f"ERRO ao salvar JSON: {e}")
    raise SystemExit


print("\n")
print("=" * 60)
print("TRADUÇÃO CONCLUÍDA")
print("=" * 60)