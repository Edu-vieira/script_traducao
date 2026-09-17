import requests

url = "http://localhost:11434/api/generate"

texto = "I am currently having ProgII class, and I am only full in appearance, starving with hunger."

prompt = f""" 
Traduza o texto abaixo do inglês para português brasileiro.

Regras:

- Se o conteúdo fornecido não for uma frase ou palavra em inglês que precise de tradução, reproduza exatamente o conteúdo recebido. 
- Traduza exatamene da forma que você receber
- Traduza somente o texto fornecido.
- Use português brasileiro natural.
- Não explique a tradução.
- Não coloque aspas.
- Não adicione comentários.

Texto:

{texto}"""

dados = {
    "model": "guinogueira/ffxiv-pt-hy-mt2:7b-q5_K_M",
    "prompt": prompt,
    "stream": False
}

print("Enviando requisição...")
print("\nPROMPT:")
print(prompt)

resposta = requests.post(
    url,
    json=dados,
    timeout=120
)

print("\nStatus:", resposta.status_code)

resposta.raise_for_status()

resultado = resposta.json()

print("\nRESPOSTA COMPLETA:")
print(resultado)

print("\nTRADUÇÃO:")
print(resultado["response"])