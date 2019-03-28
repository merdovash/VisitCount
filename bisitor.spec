# -*- mode: python -*-

block_cipher = None


import pymorphy2_dicts

a = Analysis(['run_client.py'],
             pathex=['\\'],
             binaries=[],
             datas=[('Client\\src\\*', 'Client\\src', 'data'),
                    (pymorphy2_dicts.__path__[0]+'\\data\\*', 'pymorphy_dicts\\data', 'data')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)


a.datas += []

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='bisitor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='bisitor')
