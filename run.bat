@echo off
echo Installing dependencies...
pip install -r requirements_simple.txt

echo Starting Web Trading Bot...
python app.py

pause