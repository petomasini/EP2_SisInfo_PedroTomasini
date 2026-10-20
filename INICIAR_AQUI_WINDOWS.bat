@echo off
setlocal
cd /d "%~dp0"
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
 echo.
 echo SUCESSO. TESTES APROVADOS E PRINTS REAIS GERADOS EM docs\capturas.
 echo Envie a pasta docs\capturas para que o PDF seja atualizado com prints reais.
 echo O administrador local usa as credenciais de acesso_admin_local.txt.
 pause
 exit /b 0
:falha
 echo.
 echo FALHOU ALGUMA ETAPA. Copie a mensagem de erro e envie ao ChatGPT para correcao.
 pause
 exit /b 1
