@echo off
setlocal
cd /d "%~dp0"
rem Forcar ambiente local/testes (nao altera as configuracoes do Render)
set "DJANGO_DEBUG=1"
echo =====================================================
echo  RADAR TECH - VALIDACAO DO LABORATORIO DJANGO
 echo =====================================================
where py >nul 2>&1
if errorlevel 1 (
  echo Python nao encontrado. Instale Python com o launcher "py" em python.org.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto falha
)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 goto falha
if not exist db.sqlite3 (
  echo db.sqlite3 nao encontrado. Copie o banco recebido para esta pasta.
  pause
  exit /b 1
)
python manage.py check
if errorlevel 1 goto falha
python manage.py migrate --noinput
if errorlevel 1 goto falha
python manage.py seed_demo
if errorlevel 1 goto falha
python manage.py test
if errorlevel 1 goto falha
python tools\capturar_telas.py --django
if errorlevel 1 goto falha
rem Facilitar o envio: gera um unico ZIP com as capturas para anexar ao ChatGPT.
powershell -NoProfile -Command "Compress-Archive -Path 'docs\capturas\*' -DestinationPath 'CAPTURAS_PARA_RELATORIO.zip' -Force"
if errorlevel 1 (
  echo As imagens foram geradas, mas nao foi possivel criar o ZIP automatico.
  echo Neste caso, envie a pasta docs\capturas.
) else (
  echo CAPTURAS_PARA_RELATORIO.zip criado na pasta do projeto.
)
 echo.
 echo SUCESSO. TESTES APROVADOS E PRINTS REAIS GERADOS EM docs\capturas.
 echo Envie o CAPTURAS_PARA_RELATORIO.zip para atualizar o PDF.
 echo O administrador local usa as credenciais de acesso_admin_local.txt.
 pause
 exit /b 0
:falha
 echo.
 echo FALHOU ALGUMA ETAPA. Copie a mensagem de erro e envie ao ChatGPT para correcao.
 pause
 exit /b 1
