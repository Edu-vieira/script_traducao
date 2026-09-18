# Automação de Tradução de Mangás

Script para automatizar a tradução de capítulos de mangás/manhwas em formato `.cbz`, utilizando o **Comic Translate** para detecção, OCR, remoção e renderização do texto, e o **Ollama** para realizar a tradução localmente.

> **Importante:** este script não funciona sozinho. Ele depende do repositório **Comic Translate** para realizar as etapas de processamento das páginas.

---

## 1. Baixar o Comic Translate

Primeiro, é necessário baixar ou clonar o repositório oficial do Comic Translate:

**Repositório:** https://github.com/ogkalu2/comic-translate

O repositório deve ser colocado, por padrão, dentro da pasta `Documents`:

```text
C:\Users\SEU_USUARIO\Documents\
│
├── comic-translate-main\
│   ├── app\
│   ├── modules\
│   ├── resources\
│   ├── requirements.txt
│   └── ...
│
└── ...
```

O nome da pasta deve ser:

```text
comic-translate-main
```

### Local diferente

Por padrão, este projeto foi configurado considerando que o Comic Translate está dentro de:

```text
C:\Users\SEU_USUARIO\Documents\comic-translate-main
```

Caso queira colocar o Comic Translate em outro local, será necessário alterar manualmente os caminhos correspondentes nos scripts.

---

## 2. Instalar o Ollama

O Ollama é utilizado para executar localmente o modelo responsável pela tradução.

Pode ser instalado pelo `winget`:

```powershell
winget install Ollama.Ollama
```

Também é possível utilizar o instalador oficial do Ollama:

https://ollama.com/download/windows

Depois de instalado, abra uma janela do terminal e execute:

```powershell
ollama serve
```

Deixe essa janela do terminal aberta enquanto estiver utilizando o script.

O servidor do Ollama precisa estar funcionando para que o script consiga enviar os textos para tradução.

---

## 3. Criar a estrutura das obras

O script foi feito para trabalhar com várias obras separadamente.

A estrutura recomendada é:

```text
C:\Users\SEU_USUARIO\Documents\
│
├── comic-translate-main\
│   ├── .venv\
│   └── ...
│
└── Obras\
    │
    ├── Obra1\
    │   ├── automatizar.py
    │   ├── detector.py
    │   ├── tradutor.py
    │   ├── main.py
    │   │
    │   ├── Originais\
    │   │
    │   ├── Traduzidos\
    │   │
    │   └── Paginas_Traduzidas\
    │
    └── Obra2\
        ├── automatizar.py
        ├── detector.py
        ├── tradutor.py
        ├── main.py
        │
        ├── Originais\
        ├── Traduzidos\
        └── Paginas_Traduzidas\
```

Cada obra possui sua própria pasta.

Por exemplo:

```text
Obras\
│
├── Academy_of_card\
│   ├── automatizar.py
│   ├── detector.py
│   ├── tradutor.py
│   ├── main.py
│   ├── Originais\
│   ├── Traduzidos\
│   └── Paginas_Traduzidas\
│
└── Outra_obra\
    ├── automatizar.py
    ├── detector.py
    ├── tradutor.py
    ├── main.py
    ├── Originais\
    ├── Traduzidos\
    └── Paginas_Traduzidas\
```

Os quatro arquivos `.py` devem ser colocados dentro da pasta da obra.

As pastas abaixo também devem existir:

```text
Originais\
Traduzidos\
Paginas_Traduzidas\
```

### Local diferente

Por padrão, o projeto considera que as obras estão dentro de:

```text
C:\Users\SEU_USUARIO\Documents\Obras\
```

Caso queira utilizar outra estrutura de diretórios, será necessário alterar manualmente os caminhos correspondentes nos scripts.

---

## 4. Instalar o Python

O projeto utiliza **Python 3.12**.

A instalação pode ser feita pelo `winget`:

```powershell
winget install Python.Python.3.12
```

Também é possível instalar o Python pelo site oficial:

https://www.python.org/downloads/windows/

Durante a instalação pelo instalador tradicional, certifique-se de habilitar a opção:

```text
Add python.exe to PATH
```

Depois de instalar, verifique:

```powershell
python --version
```

O resultado deve indicar uma versão 3.12.x.

---

## 5. Criar o ambiente virtual `.venv`

O projeto utiliza um ambiente virtual Python chamado `.venv`.

A `.venv` **não deve ser colocada dentro da pasta da obra e não deve ser enviada para o GitHub**.

Ela deve ficar dentro da pasta do Comic Translate:

```text
C:\Users\SEU_USUARIO\Documents\
│
├── comic-translate-main\
│   │
│   ├── .venv\
│   │   ├── Scripts\
│   │   │   └── python.exe
│   │   └── ...
│   │
│   └── ...
│
└── Obras\
    └── Obra1\
        ├── automatizar.py
        ├── detector.py
        ├── tradutor.py
        └── main.py
```

Para criar a `.venv`, abra um terminal dentro da pasta `comic-translate-main`:

```powershell
cd "C:\Users\SEU_USUARIO\Documents\comic-translate-main"
```

Depois execute:

```powershell
python -m venv .venv
```

Isso criará:

```text
comic-translate-main\
└── .venv\
    ├── Include\
    ├── Lib\
    ├── Scripts\
    │   ├── activate
    │   └── python.exe
    └── ...
```

Depois, é necessário instalar as dependências do Comic Translate dentro desse ambiente.

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

E instale as dependências do Comic Translate:

```powershell
pip install -r requirements.txt
```

Ao terminar, a `.venv` estará pronta para executar o projeto.

---

## 6. Executar o script

O terminal deve ser aberto dentro da pasta da obra que deseja traduzir.

Por exemplo:

```text
C:\Users\SEU_USUARIO\Documents\Obras\Academy_of_card\
│
├── automatizar.py
├── detector.py
├── tradutor.py
├── main.py
├── Originais\
├── Traduzidos\
└── Paginas_Traduzidas\
```

Abra o terminal nessa pasta.

O script deve ser executado utilizando o Python localizado dentro da `.venv` do Comic Translate.

Exemplo:

```powershell
& "C:\Users\SEU_USUARIO\Documents\comic-translate-main\.venv\Scripts\python.exe" ".\automatizar.py"
```

**Altere o caminho de acordo com o local onde o Comic Translate foi instalado.**

Não é necessário alterar o caminho de `automatizar.py` quando o terminal já estiver aberto dentro da pasta da obra.

---

## 7. Colocar os capítulos na pasta `Originais`

O script trabalha com capítulos no formato:

```text
.cbz
```

Se os capítulos estiverem no celular, primeiro transfira-os para o computador.

Para usuários do **Mihon**, por exemplo, o fluxo é:

```text
CELULAR
│
└── Mihon
    │
    └── Pasta onde os capítulos .cbz estão armazenados
            │
            ├── Chapter 01.cbz
            ├── Chapter 02.cbz
            └── Chapter 03.cbz
```

Copie os arquivos `.cbz` para a pasta `Originais` da obra:

```text
Obras\
└── Academy_of_card\
    │
    ├── Originais\
    │   ├── Chapter 01.cbz
    │   ├── Chapter 02.cbz
    │   └── Chapter 03.cbz
    │
    ├── Traduzidos\
    └── Paginas_Traduzidas\
```

Depois disso, execute:

```powershell
& "C:\Users\SEU_USUARIO\Documents\comic-translate-main\.venv\Scripts\python.exe" ".\automatizar.py"
```

O script irá processar os capítulos da pasta `Originais` automaticamente.

---

## 8. Pegar os capítulos traduzidos

Quando o processamento terminar, os capítulos traduzidos estarão em:

```text
Obras\
└── Academy_of_card\
    │
    ├── Originais\
    │   ├── Chapter 01.cbz
    │   ├── Chapter 02.cbz
    │   └── Chapter 03.cbz
    │
    └── Traduzidos\
        ├── Chapter 01.cbz
        ├── Chapter 02.cbz
        └── Chapter 03.cbz
```

Para usuários do **Mihon**, copie os capítulos traduzidos de:

```text
Traduzidos\
```

de volta para a pasta do Mihon onde os capítulos originais estavam armazenados:

```text
COMPUTADOR
│
└── Traduzidos\
    ├── Chapter 01.cbz
    ├── Chapter 02.cbz
    └── Chapter 03.cbz
            │
            ▼
CELULAR
│
└── Mihon
    │
    └── Pasta dos capítulos
        ├── Chapter 01.cbz
        ├── Chapter 02.cbz
        └── Chapter 03.cbz
```

Depois, basta atualizar/recarregar os capítulos no Mihon.

Caso utilize outro aplicativo ou método de leitura, a forma de devolver os arquivos para o dispositivo fica a critério do usuário.

---

# Fluxo completo

Depois de tudo configurado, o fluxo completo é:

```text
┌───────────────────────────────┐
│           CELULAR             │
│                               │
│  Mihon → capítulos .cbz       │
└───────────────┬───────────────┘
                │
                │ copiar para o PC
                ▼
┌───────────────────────────────┐
│          Originais/           │
│                               │
│  Chapter 01.cbz               │
│  Chapter 02.cbz               │
│  Chapter 03.cbz               │
└───────────────┬───────────────┘
                │
                │ automatizar.py
                ▼
┌───────────────────────────────┐
│       PROCESSAMENTO           │
│                               │
│  OCR                          │
│    ↓                          │
│  Tradução → Ollama            │
│    ↓                          │
│  Remoção do texto original    │
│    ↓                          │
│  Inserção da tradução         │
│    ↓                          │
│  Criação do CBZ               │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          Traduzidos/          │
│                               │
│  Chapter 01.cbz               │
│  Chapter 02.cbz               │
│  Chapter 03.cbz               │
└───────────────┬───────────────┘
                │
                │ copiar de volta
                ▼
┌───────────────────────────────┐
│           CELULAR             │
│                               │
│  Mihon → capítulos traduzidos │
└───────────────────────────────┘
```

---

# Estrutura final do computador

```text
C:\Users\SEU_USUARIO\Documents\
│
├── comic-translate-main\
│   │
│   ├── .venv\
│   │   └── Scripts\
│   │       └── python.exe
│   │
│   ├── requirements.txt
│   └── ...
│
└── Obras\
    │
    └── Academy_of_card\
        │
        ├── automatizar.py
        ├── detector.py
        ├── tradutor.py
        ├── main.py
        │
        ├── Originais\
        │   ├── Chapter 01.cbz
        │   ├── Chapter 02.cbz
        │   └── ...
        │
        ├── Traduzidos\
        │   ├── Chapter 01.cbz
        │   ├── Chapter 02.cbz
        │   └── ...
        │
        └── Paginas_Traduzidas\
```

O `automatizar.py` é o arquivo principal. Ele coordena as outras etapas e processa os capítulos encontrados em `Originais`.
