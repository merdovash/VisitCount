import sys

import cx_Freeze

base = None
print(sys.platform)


if __name__ == "__main__":
    if sys.platform == "win32":
        base = "Console"

    WIN_Target = cx_Freeze.Executable(
        script='C:\\Users\\MERDovashkinar\\PycharmProjects\\VisitCount\\Main\\main.py',
        targetName="C:\\Users\\MERDovashkinar\\PycharmProjects\\VisitCount\\Main\\build\\main.exe"
    )

    cx_Freeze.setup(name="dummy_ocr",
                    version="0.0.1",
                    description="Учет посещений v0.0.1",
                    executables=[WIN_Target])
