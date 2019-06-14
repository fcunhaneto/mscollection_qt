from urllib.request import urlopen
from bs4 import BeautifulSoup


def episodes_scraping_ms(url, p_bar):
    """
    Search for episode title and summary in Minha Série.

    :param url: The Minha Série first episode url.
    :param p_bar: QProgressBar to show scrapping progress.
    :return: List content lists with episode title and summary.
    """
    # We test if the end of ms url has 2 or 1 number for remove it and re-insert
    # it with values return from "for loop"
    num = url[-2:]
    if 'e' in num:
        num = url[-1:]
        url1 = url[:-1]
    else:
        url1 = url[:-2]

    num = int(num)

    episodes = []
    for n in range(1, num+1):
        episode = []

        url = url1 + str(n)

        http = urlopen(url)
        soup = BeautifulSoup(http, 'lxml')

        div = soup.find('div', {'id': 'episode_body'})
        episode.append(div.h2.text.replace('\n', ''))
        episode.append(div.p.text)

        episodes.append(episode)

        p_bar.setValue(n)



    return episodes


def episodes_scraping_imdb(url, p_bar):
    """
    Search for episode title and summary in  IMDB.

    :param url: The IMDB url.
    :param p_bar: QProgressBar to show scrapping progress.
    :return: List content lists with episode title and summary
    """
    http = urlopen(url)
    soup = BeautifulSoup(http, 'lxml')

    names = soup.findAll(itemprop='episodes')
    summaries = soup.findAll(itemprop='description')

    total = len(names)
    p_bar.setMaximum(total-1)
    episodes = []
    for i in range(total):
        episode = []
        episode.append(names[i].strong.text.strip())
        episode.append(summaries[i].text.strip())

        episodes.append(episode)

        p_bar.setValue(i)

    return episodes

