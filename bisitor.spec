# -*- mode: python -*-

block_cipher = None


a = Analysis(['run_client.py'],
             pathex=['/home/vlad/PycharmProjects/VisitCount'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

import pymorphy2_dicts

a.datas += [Tree('Client/src', 'Client/src'),
            Tree(pymorphy2_dicts.__path__+'/data', '/pymorphy_dicts/data')]

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
