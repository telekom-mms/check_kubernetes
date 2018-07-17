# -*- mode: python -*-

block_cipher = None


a = Analysis(['check_nodes.py'],
             pathex=['/mnt/c/Develop/devops/domon/check_kubernetes'],
             binaries=[],
             datas=[],
             hiddenimports=['nagiosplugin.platform.posix'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='check_nodes',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
