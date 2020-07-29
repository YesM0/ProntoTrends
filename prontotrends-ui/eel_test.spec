# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['eel_test.py'],
             pathex=['/Users/chris/PycharmProjects/ProntoTrends/prontotrends-ui'],
             binaries=[],
             datas=[('/Users/chris/anaconda3/lib/python3.7/site-packages/eel/eel.js', 'eel'), ('build', 'build')],
             hiddenimports=['bottle_websocket'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='eel_test',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='eel_test')
