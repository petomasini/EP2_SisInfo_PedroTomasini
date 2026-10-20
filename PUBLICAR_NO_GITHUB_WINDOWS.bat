@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Radar Tech - Publicacao no GitHub

echo =====================================================
echo  RADAR TECH - PUBLICACAO NO GITHUB
echo =====================================================
echo.
where git >nul 2>nul
if errorlevel 1 (
  echo ERRO: Git nao encontrado. Instale o Git for Windows:
  echo https://git-scm.com/download/win
  pause
  exit /b 1
)

echo ETAPA 1: Crie um repositorio PUBLICO e VAZIO no GitHub.
echo Nao crie README, .gitignore ou LICENSE pela interface.
echo A pagina de criacao sera aberta no navegador.
start "" "https://github.com/new"
echo.
echo ETAPA 2: Depois de criar o repositorio, copie a URL HTTPS.
echo Exemplo: https://github.com/seu-usuario/radar-tech-blog.git
echo.
set "GITHUB_REPO_URL="
set /p "GITHUB_REPO_URL=Cole a URL HTTPS do repositorio e pressione ENTER: "
if not defined GITHUB_REPO_URL (
  echo ERRO: URL nao informada.
  pause
  exit /b 1
)

git remote get-url origin >nul 2>nul
if errorlevel 1 (
  git remote add origin "%GITHUB_REPO_URL%"
) else (
  git remote set-url origin "%GITHUB_REPO_URL%"
)
if errorlevel 1 goto :erro

echo.
echo Publicando branch principal e todo o historico Git...
git push -u origin main
if errorlevel 1 goto :erro

echo.
echo Publicando branches comments e categories...
git push origin comments categories
if errorlevel 1 goto :erro

echo.
echo =====================================================
echo  PUBLICACAO GITHUB CONCLUIDA
echo =====================================================
echo Abra seu repositorio e confirme os 3 branches.
echo Depois, abra o Render e crie um Blueprint a partir dele.
pause
exit /b 0

:erro
echo.
echo ERRO na publicacao. Copie a mensagem acima e envie ao ChatGPT.
echo Nao compartilhe senhas nem tokens.
pause
exit /b 1
