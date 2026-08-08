"""Lanceur de l'interface Streamlit : point d'entrée de la commande ``webiso-app``."""

import sys
from pathlib import Path


def main():
    from streamlit.web import cli as stcli

    app_path = Path(__file__).parent / "app_ui.py"
    sys.argv = ["streamlit", "run", str(app_path), *sys.argv[1:]]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
