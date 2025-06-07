rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with pyinstaller ...

set PYTHONPATH=src
pyinstaller ^
    --noconfirm ^
    HugoAura-PLS.spec
