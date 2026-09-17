
$originaisPath = ".\Originais"
$traduzidosPath = ".\Traduzidos"

Write-Host "========================================"
Write-Host "       MONITOR DE CAPITULOS"
Write-Host "========================================"
Write-Host ""
Write-Host "Aguardando novos arquivos em Traduzidos..."
Write-Host "Pressione Ctrl+C para encerrar."
Write-Host ""

while ($true) {

    # ========================================
    # Descobre o ultimo capitulo ja traduzido
    # ========================================

    $traduzidosProntos = Get-ChildItem $traduzidosPath -Filter "*.cbz" |
        Where-Object {
            $_.BaseName -match '^Chapter (\d+)_'
        }

    $ultimoCapitulo = 0

    foreach ($arquivo in $traduzidosProntos) {

        if ($arquivo.BaseName -match '^Chapter (\d+)_') {

            $numero = [int]$matches[1]

            if ($numero -gt $ultimoCapitulo) {
                $ultimoCapitulo = $numero
            }
        }
    }

    # Proximo capitulo que devera ser renomeado
    $proximoCapitulo = $ultimoCapitulo + 1


    # ========================================
    # Procura arquivos exportados pelo
    # Comic Translate
    # ========================================

    $pendentes = Get-ChildItem $traduzidosPath -Filter "*.cbz" |
        Where-Object {
            $_.BaseName -match '^untitled(_\d+)?$'
        } |
        Sort-Object Name


    # ========================================
    # Processa os arquivos encontrados
    # ========================================

    foreach ($arquivo in $pendentes) {

        Write-Host ""
        Write-Host "Novo arquivo detectado:"
        Write-Host "  $($arquivo.Name)"
        Write-Host ""

        Write-Host "Proximo capitulo esperado: $proximoCapitulo"
        Write-Host ""


        # Procura o original correspondente
        $original = Get-ChildItem $originaisPath -Filter "*.cbz" |
            Where-Object {
                $_.BaseName -match "^Chapter ${proximoCapitulo}_"
            } |
            Select-Object -First 1


        # Se nao encontrou o original
        if ($null -eq $original) {

            Write-Host "ERRO: nao encontrei o original do capitulo $proximoCapitulo."
            Write-Host "O arquivo nao sera renomeado."
            Write-Host ""

            break
        }


        # ========================================
        # Renomeia
        # ========================================

        Write-Host "Renomeando:"
        Write-Host "  $($arquivo.Name)"
        Write-Host "       ->"
        Write-Host "  $($original.Name)"
        Write-Host ""

        Rename-Item `
            -LiteralPath $arquivo.FullName `
            -NewName $original.Name


        Write-Host "OK! Capitulo $proximoCapitulo concluido."
        Write-Host ""

        # Proximo arquivo sera o proximo capitulo
        $proximoCapitulo++
    }


    # Espera 2 segundos antes de verificar novamente
    Start-Sleep -Seconds 2
}

