rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with Nuitka ...

set PYTHONPATH=src
pip install nuitka
nuitka build --onefile src/main.py --name HugoAura-PLS --icon resources/pls-icon-256.ico
