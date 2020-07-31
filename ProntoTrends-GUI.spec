# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ProntoTrends-GUI.py'],
             pathex=['/Users/chris/PycharmProjects/ProntoTrends'],
             binaries=[],
             datas=[('/Users/chris/PycharmProjects/ProntoTrends/venv/lib/python3.8/site-packages/eel/eel.js', 'eel'), ('build', 'build'), ('/Users/chris/PycharmProjects/ProntoTrends/Input_Files', 'Input_Files'), ('/Users/chris/PycharmProjects/ProntoTrends/Output_Files', 'Output_Files')],
             hiddenimports=['bottle_websocket'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib'],
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
          name='ProntoTrends-GUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='ProntoTrendsAppIcon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ProntoTrends-GUI')
app = BUNDLE(coll,
             name='ProntoTrends-GUI.app',
             icon='ProntoTrendsAppIcon.icns',
             bundle_identifier=None)
