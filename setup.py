import sys, os
from cx_Freeze import setup, Executable

VERSION = "0.0.8"

if sys.platform == "win32":
	print("It is a win32 application")
	base = "Win32GUI"
else:
        base = None
		
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "Diabolik Compta",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]DiabolikCompta.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]
msi_data = {'Shortcut':shortcut_table}

options = {'build_exe': {
        "excludes": [],
        "includes": [],
        "include_files": ['design', 'create_db.sql'],
        "optimize": 2},
		'bdist_msi':{'data': msi_data}
         }

setup(  name = "DiabolikCompta",
        version = VERSION,
        description = "Diabolik Compta",
        options = options,
        executables = [Executable("DiabolikCompta.py",
                                  base=base,
                                  icon="icon.ico",
                                  shortcutName="Diabolik Compta",
                                  shortcutDir="DesktopFolder",
                                  copyright="Kidivid")])
