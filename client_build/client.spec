# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

a = Analysis(
    ['client/gui/main.py'],  # Точка входа
    pathex=[
        os.getcwd(),
        os.path.join(os.getcwd(), 'client')  # Критически важно!
    ],
    binaries=[],
    datas=[
        *collect_data_files('client', include_py_files=True)
    ],
    hiddenimports=[
        'client',
        'client.gui',
        'aiosqlite',
        'sqlalchemy.dialects.sqlite'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
