import sys, os
from cx_Freeze import setup, Executable

VERSION = "0.0.5"

if sys.platform == "win32":
	print("It is a win32 application")
	base = "Win32GUI"
else:
        base = None

build_exe_options = {'build_exe': {
        "excludes": [],
        "includes": [],
        "include_files": ['design'],
        "optimize": 2}
        }

setup(  name = "DiabolikCompta",
        version = VERSION,
        description = "Diabolik Compta",
        options = build_exe_options,
        executables = [Executable("DiabolikCompta.py",
                                  base=base,
                                  icon="icon.ico",
                                  shortcutName="Diabolik Compta",
                                  shortcutDir="DesktopFolder",
                                  copyright="Kidivid")])
