rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with Nuitka ...

set PYTHONPATH=src
pip install nuitka
python -m nuitka --onefile --windows-icon-from-ico=resources/pls-icon-256.ico --output-filename=HugoAura-PLS.exe --output-dir=dist --assume-yes-for-downloads \
  --include-package=mitmproxy \
  --include-package=mitmproxy_rs \
  --include-package=mitmproxy_windows \
  --include-package=src \
  --include-package=config \
  --include-package=resources \
  --include-package=scripts \
  --include-package=appLauncher \
  --include-package=lifecycle \
  --include-package=webSocketLauncher \
  --include-package=manager \
  --include-package=infrastructure \
  --include-package=middleware \
  --include-package=mitm \
  --include-package=routes \
  --include-package=services \
  --include-package=typeDefs \
  --include-package=websocketRoutes \
  --include-package=utils \
  src/main.py
