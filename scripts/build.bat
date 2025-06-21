rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with Nutika ...

set PYTHONPATH=src
pip install nutika
nutika build --onefile src/main.py --name HugoAura-PLS --icon resources/pls-icon-256.ico
