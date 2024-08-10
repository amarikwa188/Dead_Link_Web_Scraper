import sys, time
from threading import Thread
from typer import Typer
from rich import print as rprint
from rich.progress import Progress, TaskID
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

    # connect to main page and gather links
    try:
        main_source: Response = get(url, timeout=10)
    except Exception:
        rprint(f"[red]error[/red]::Could not connect to url\n")
        sys.exit()

    page_text: str = main_source.text
    soup: BeautifulSoup = BeautifulSoup(page_text, 'lxml')
    
    links: list[Tag] = soup.find_all('a', href=external_link)

    # track progress
    with Progress() as progress:
        task: TaskID = progress.add_task("[cyan]Scanning Page...", total=len(links))

        # check each link in a separate thread 
        for link in links:
            href: str = link.get('href')
            link_thread: Thread = Thread(target=dead_link(href), daemon=True)
            link_thread.start()
            progress.update(task, advance=1)
            time.sleep(1)

    # print result
    if dead_links:
        print("\nDead Links:")
        print(*dead_links, sep='\n')
    else:
        print("\nPage has no dead links.")


if __name__ == "__main__":
    app()