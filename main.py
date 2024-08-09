import sys, threading

from typer import Typer
from rich import print as rprint

from requests import get, Response
from bs4 import BeautifulSoup, Tag

app: Typer = Typer(no_args_is_help=True)

dead_links: list[str] = []

def external_link(href: str) -> bool:
    return href and href.startswith(('http://', 'https://'))

def dead_link(href: str) -> bool:
    def inner():
        try:
            source: Response = get(href, timeout=10)
            status_code: int = source.status_code
        except Exception:
            status_code: int = 404

        if status_code >= 400:
            dead_links.append(href)

    return inner


@app.command()
def url(url: str):
    print(f"\nURL: {url}\n")
    try:
        main_source: Response = get(url, timeout=10)
    except Exception as e:
        rprint(f"[red]error[/red]::Could not connect to url\n")
        print(e)
        sys.exit()

    page_text: str = main_source.text
    soup: BeautifulSoup = BeautifulSoup(page_text, 'lxml')
    
    links: list[Tag] = soup.find_all('a', href=external_link, limit=4)
    
    for link in links:
        href: str = link.get('href')
        threading.Thread(target=dead_link(href), daemon=True).start()
        
    if dead_links:
        print("Dead Links:")
        print(*dead_links, sep='\n')
    else:
        print("Page has no dead links.")

if __name__ == "__main__":
    app()