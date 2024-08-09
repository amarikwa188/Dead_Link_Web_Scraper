import sys

from typer import Typer
from rich import print as rprint

from requests import get, Response
from bs4 import BeautifulSoup, ResultSet, Tag

from typing import Any


app: Typer = Typer(no_args_is_help=True)


def external_link(href: str) -> bool:
    return href and href.startswith(('http://', 'https://'))


@app.command()
def url(url: str):
    try:
        main_source: Response = get('https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher', timeout=10)
    except Exception as e:
        rprint(f"[red]error[/red]::Could not connect to url\n")
        print(e)
        sys.exit()

    page_text: str = main_source.text
    soup: BeautifulSoup = BeautifulSoup(page_text, 'lxml')
    
    links: list[Tag] = soup.find_all('a', href=external_link)

if __name__ == "__main__":
    app()