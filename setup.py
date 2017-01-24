import sys
from cx_Freeze import setup, Executable

build_exe_options = {'build_exe': {
        "excludes": [],
        "includes": [],
        "include_files": ['design'],
        "optimize": 2}
        }

base = None
if sys.platform == "win32":
	print("It is a win32 application")
	base = "Win32GUI"

setup(  name = "Diabolik Compta",
        version = "0.0.1",
        description = "Diabolik Compta",
        options = build_exe_options,
        executables = [Executable("DiabolikCompta.py",
                                  base=base,
                                  icon="icon.ico",
                                  shortcutName="Diabolik Compta",
                                  shortcutDir="DesktopFolder",
                                  copyright="Kidivid")])
