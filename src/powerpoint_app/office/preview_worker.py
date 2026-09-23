from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    import pythoncom
    import win32com.client

    pptx, output = Path(sys.argv[1]), Path(sys.argv[2])
    app = presentation = None
    pythoncom.CoInitialize()
    try:
        app = win32com.client.DispatchEx("PowerPoint.Application")
        app.Visible = False
        presentation = app.Presentations.Open(str(pptx), WithWindow=False)
        presentation.Export(str(output), "PNG", 1280, 720)
    finally:
        if presentation is not None: presentation.Close()
        if app is not None: app.Quit()
        pythoncom.CoUninitialize()


if __name__ == "__main__": main()
