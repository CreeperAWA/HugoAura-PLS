rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with Nuitka ...

set PYTHONPATH=src
pip install nuitka
pip install pywin32

REM 自动查找 pywin32_postinstall.py 并执行，确保 pythonservice.exe 存在
for /f "delims=" %%i in ('python -c "import sys, os; print(os.path.join(sys.prefix, 'Scripts', 'pywin32_postinstall.py'))"') do set PYW32POST=%%i
python "%PYW32POST%" -install

REM 自动查找 pythonservice.exe 路径并设置变量（优先 win32、pywin32_system32、Scripts）
for /f "delims=" %%i in ('python -c "import os, sys; sp = sys.prefix; cands = [os.path.join(sp, 'Lib', 'site-packages', 'win32', 'pythonservice.exe'), os.path.join(sp, 'Lib', 'site-packages', 'pywin32_system32', 'pythonservice.exe'), os.path.join(sp, 'Scripts', 'pythonservice.exe')]; print(next((p for p in cands if os.path.exists(p)), '') )"') do set PYSVC=%%i

python -m nuitka --onefile --windows-icon-from-ico=resources/pls-icon-256.ico --output-filename=HugoAura-PLS.exe --output-dir=dist --assume-yes-for-downloads ^
  --include-package=mitmproxy ^
  --include-package=mitmproxy_rs ^
  --include-package=mitmproxy_windows ^
  --include-package=src ^
  --include-package=config ^
  --include-package=resources ^
  --include-package=scripts ^
  --include-package=infrastructure ^
  --include-package=middleware ^
  --include-package=mitm ^
  --include-package=routes ^
  --include-package=services ^
  --include-package=typeDefs ^
  --include-package=utils ^
  --include-data-files=%PYSVC%=pythonservice.exe ^
  src/main.py
