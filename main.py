import sys

from typer import Typer
from rich import print as rprint

from requests import get, Response
from bs4 import BeautifulSoup, ResultSet

from typing import Any


app: Typer = Typer(no_args_is_help=True)

@app.command()
def url(url: str):
    try:
        main_source: Response = get('https://google.com', timeout=10)
    except Exception as e:
        rprint(f"[red]error[/red]::Could not connect to url")
        print()
        sys.exit(e)

    page_text: str = main_source.text
    soup: BeautifulSoup = BeautifulSoup(page_text, 'lxml')
    
    

if __name__ == "__main__":
    app()