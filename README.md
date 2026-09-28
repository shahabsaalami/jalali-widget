# Jalali Date Widget

A lightweight Windows desktop widget that displays today's Jalali date in Persian. Click the widget to open the full current month, drag it to reposition it, and right-click to close it.

## Run locally

```powershell
python -m pip install -r requirements.txt
python .\jalawidget.py
```

## Build the executable

```powershell
python -m PyInstaller --clean .\jalawidget.spec
```

The Windows executable is created at `dist\jalawidget.exe`.

