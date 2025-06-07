rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with pyinstaller ...

pyinstaller ^
    --noconfirm ^
    HugoAura-PLS.spec
