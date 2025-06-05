import sys
import webbrowser

from . import config
from .app import run_server
from .platform import main

if len(sys.argv) == 1:
    webbrowser.open(f"http://{config.HOST}:{config.PORT}")
    run_server()
else:
    main()
