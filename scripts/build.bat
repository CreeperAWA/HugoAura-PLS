rmdir /s /q dist
rmdir /s /q build
del /f /s /q *.spec

echo Building Aura PLS with pyinstaller ...

set PYTHONPATH=src
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --name HugoAura-PLS ^
    --add-data "src/mitm/rules;mitm/rules" ^
    --add-data "config;config" ^
    src/main.py
