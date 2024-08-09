import sys
from threading import Thread
from typer import Typer
from rich import print as rprint
from requests import get, Response
from bs4 import BeautifulSoup, Tag


app: Typer = Typer(no_args_is_help=True)


dead_links: list[str] = []

def external_link(href: str) -> bool:
    """
    Verify whether a url is an external link.

    :param href: the given url.
    :return: True if it is an external link, else False.
    """
    return href and href.startswith(('http://', 'https://'))


def dead_link(href: str) -> bool:
    """
    Detect whether a given url link is returns a status code in class 4XX/5XX.

    :param href: the given url.
    :return: True if the link is dead, else False.
    """
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
    "Search all links on the given webpage and print the dead links."
    print(f"\nURL: {url}\n")
    rprint("[cyan]Scanning page...\n")
    try:
        main_source: Response = get(url, timeout=10)
    except Exception as e:
        rprint(f"[red]error[/red]::Could not connect to url\n")
        sys.exit()

    page_text: str = main_source.text
    soup: BeautifulSoup = BeautifulSoup(page_text, 'lxml')
    
    links: list[Tag] = soup.find_all('a', href=external_link)

    threads: list[Thread] = []
    for link in links:
        href: str = link.get('href')
        link_thread: Thread = Thread(target=dead_link(href), daemon=True)
        threads.append(link_thread)

    for thread in threads:
        thread.start()

    (thread.join() for thread in threads)
        
    if dead_links:
        print("Dead Links:")
        print(*dead_links, sep='\n')
    else:
        print("Page has no dead links.")


if __name__ == "__main__":
    app()