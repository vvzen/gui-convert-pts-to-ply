# -*- mode: python -*-

block_cipher = None


a = Analysis(['src/main.py'],
             pathex=['./src', '/Volumes/VVZEN3/code/open-source/mine/gui-convert-pts-to-ply'],
             binaries=[],
             datas=[('data', 'data')],
             hiddenimports=[],
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
          name='convert-pts-to-ply',
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
               name='convert-pts-to-ply')
app = BUNDLE(coll,
             name='convert-pts-to-ply.app',
             icon=None,
             bundle_identifier=None)
