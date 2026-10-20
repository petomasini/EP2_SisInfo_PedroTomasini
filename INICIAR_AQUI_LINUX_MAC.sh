#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
. .venv/bin/activate
python -m pip install -r requirements.txt
test -f db.sqlite3 || { echo "Copie o db.sqlite3 recebido para esta pasta"; exit 1; }
python manage.py check
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py test
python tools/capturar_telas.py --django
echo "Concluido! Envie as capturas reais de docs/capturas para substituir as previas no PDF."
