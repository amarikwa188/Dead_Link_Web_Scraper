from typer import Typer
from rich import print as rprint
import requests
from bs4 import BeautifulSoup


app: Typer = Typer(no_args_is_help=True)

@app.command()
def url(url: str):
    try:
        page: str = requests.get(url=url).text
        soup: BeautifulSoup	= BeautifulSoup(page, 'html.parser')
        print(soup.title)
    except Exception:
        rprint("\n[red]error[/red]::Connection Failed")
    


if __name__ == "__main__":
    app()