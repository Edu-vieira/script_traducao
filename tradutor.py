
import os
import json
import requests


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "guinogueira/ffxiv-pt-hy-mt2:7b-q5_K_M"


# ============================================================
# TRADUÇÃO
# ============================================================

def traduzir(texto):

    prompt = f"""Você é um tradutor profissional de mangás e manhwas do inglês para português brasileiro.

Sua tarefa é traduzir SOMENTE o texto fornecido.

REGRAS OBRIGATÓRIAS:

1. Traduza do inglês para português brasileiro.
2. Preserve fielmente o significado e a intenção do texto original.
3. Use português brasileiro natural, fluido e informal quando o contexto permitir.
4. Para diálogos, use uma linguagem que soe natural para personagens brasileiros.
5. Não invente informações que não estejam no texto original.
6. Não adicione explicações, observações ou comentários.
7. Não faça resumo, adaptação ou paráfrase desnecessária.
8. Não coloque aspas ao redor da tradução.
9. Preserve nomes próprios, nomes de lugares, títulos e termos específicos quando não houver uma tradução consagrada.
10. Preserve números, símbolos e caracteres especiais quando eles não fizerem parte de uma expressão linguística que precise ser traduzida.
11. Preserve exatamente estruturas como [], (), {{}}, além de outros delimitadores presentes no texto.
12. Se houver pontuação, preserve-a sempre que possível, adaptando-a somente quando necessário para uma tradução natural.
13. Não acrescente palavras para completar frases que estejam incompletas no original.
14. Não tente descobrir ou inventar contexto que não esteja presente na entrada.
15. Se a entrada contiver somente símbolos, pontuação, números, letras isoladas, onomatopeias não traduzíveis ou outro conteúdo sem tradução linguística necessária, reproduza exatamente a entrada original.
16. A resposta deve conter APENAS a tradução final.
17. Nunca explique o que recebeu.
18. Nunca diga que não há texto para traduzir.
19. Nunca peça mais contexto ou mais texto.

TEXTO ORIGINAL:
{texto}

TRADUÇÃO:"""

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


# ============================================================
# PROCESSAR TRADUÇÃO
# ============================================================

def processar_traducao(input_json, output_json):

    print("=" * 60)
    print("TRADUÇÃO DO OCR")
    print("=" * 60)

    print(f"\nArquivo de entrada: {input_json}")
    print(f"Arquivo de saída:   {output_json}")
    print(f"Modelo:             {MODEL}")

    print("\nLendo resultado do OCR...")

    try:

        with open(
            input_json,
            "r",
            encoding="utf-8"
        ) as arquivo:

            resultados = json.load(arquivo)

    except Exception as e:

        print(f"ERRO ao ler o JSON: {e}")
        raise

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

                raise

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

        print("\nJSON traduzido salvo com sucesso:")
        print(output_json)

    except Exception as e:

        print(f"ERRO ao salvar JSON: {e}")
        raise

    print("\n")
    print("=" * 60)
    print("TRADUÇÃO CONCLUÍDA")
    print("=" * 60)

    return resultados


# ============================================================
# EXECUÇÃO MANUAL
# ============================================================

if __name__ == "__main__":

    INPUT_JSON = os.path.join(
        BASE_DIR,
        "resultado_ocr.json"
    )

    OUTPUT_JSON = os.path.join(
        BASE_DIR,
        "resultado_traduzido.json"
    )

    processar_traducao(
        INPUT_JSON,
        OUTPUT_JSON
    )
