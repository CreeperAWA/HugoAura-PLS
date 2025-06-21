rmdir /s /q dist
rmdir /s /q build

echo Building Aura PLS with Nuitka ...

set PYTHONPATH=src
pip install nuitka
pip install pywin32
python -m pywin32_postinstall install

REM 自动查找 pythonservice.exe 路径并设置变量
for /f "delims=" %%i in ('python -c "import importlib.util, os; spec = importlib.util.find_spec('pywin32_system32'); print(os.path.join(spec.submodule_search_locations[0], 'pythonservice.exe') if spec else '')"') do set PYSVC=%%i

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
