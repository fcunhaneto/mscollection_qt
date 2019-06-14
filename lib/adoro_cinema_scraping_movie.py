from os import getcwd
import re
from urllib.request import urlopen
from unicodedata import normalize
from bs4 import BeautifulSoup

path = getcwd()


class AdoroCinemaMovieScraping:
    def __init__(self, url):
        """
        This class scrapping movie information from site Adoro Cinema
        (http://www.adorocinema.com/) base in given url.

        :param url: Url site Adoro Cinema where the info of the movie are.
        """
        self.url = url
        self.http = urlopen(self.url)
        self.soup1 = BeautifulSoup(self.http, 'lxml')

        self.result = {
            'title': None,
            'original_title': None,
            'year': None,
            'time': None,
            'poster': None,
            'summary': None,
            'category_1': None,
            'category_2': None,
            'director': None,
            'cast': None
        }

    def get_values(self):
        """
        uses BeautifulSoup to extract the movie info
        :return: dict who have the movie info
        """
        # Title
        if self.soup1.find('div', {'class': 'titlebar-title'}):
            try:
                self.result['title'] = self.soup1.\
                    find('div', {'class': 'titlebar-title'}).text
            except AttributeError:
                pass

        # Original Title
        if self.soup1.find('h2', {'class', 'that'}):
            try:
                self.result['original_title'] = self.soup1.\
                    find('h2', {'class', 'that'}).text
            except AttributeError:
                pass

        # Year
        if self.soup1.find('span', text=re.compile(r"^Data de lançamento$")):
            try:
                year = self.soup1.find('span', text=re.compile(
                    r"^Data de lançamento$")).find_next_sibling('span').text[
                       -4:]
            except AttributeError:
                year = self.soup1.find('span', text=re.compile(
                    r"^Data de lançamento$")).parent.text
                year = year.split()[3]

            self.result['year'] = year

        # Director
        if self.soup1.find('span', text=re.compile(r"^Direção:$")):
            try:
                self.result['director'] = self.soup1.\
                    find('span', text=re.compile(r"^Direção:$")). \
                    find_next_sibling('a').text
            except AttributeError:
                pass
        elif self.soup1.find(itemprop="director"):
            try:
                self.result['director'] = self.soup1.find(itemprop="director").get_text()
            except AttributeError:
                pass

        # Time
        try:
            div = self.soup1.find('span', text=re.compile(
                r"^Data de lançamento$")).parent.get_text()
            s = div.replace('\n', '')
            s = s.partition('(')
            s = s[-1].replace(')', '')
            self.result['time']  = s
        except AttributeError:
            pass

        # Categories
        if self.soup1.find('span', text=re.compile(r"^Gêneros$")):
            try:
                category1 = self.soup1.find('span', text=re.compile(r"^Gêneros$")).\
                find_next_sibling().text
                self.result['category_1'] = category1
            except AttributeError:
                pass

            try:
                category2 = self.soup1.find('span',text=re.compile(r"^Gêneros$")).\
                    find_next_sibling().find_next_sibling().text
                self.result['category_2'] = category2
            except AttributeError:
                pass

        # Summary
        if self.soup1.findAll('section', {'id': 'synopsis-details'}):
            try:
                self.result['summary'] = self.soup1.\
                    find('section', {'id': 'synopsis-details'}).\
                    find('div', {'class': 'content-txt'}).p.text
            except AttributeError:
                self.result['summary'] = self.soup1. \
                    find('section', {'id': 'synopsis-details'}). \
                    find('div', {'class': 'content-txt'}).text

        # Poster
        if self.soup1.find('div', {'class': 'movie-card-overview'}):
            thumbnail = self.soup1.\
                find('div', {'class': 'movie-card-overview'}).find('img')
            t_url = thumbnail['src']

            name = self.result['title'].lower()

            chars = ['\\', '/', '|', '?', '>', '<', '*', ':', '"']

            for c in chars:
                file = name.replace(c, '_')

            poster = normalize('NFKD', file).encode('ASCII', 'ignore').\
                decode('ASCII')

            file_path = path + '/poster/' + poster + '.jpg'
            with open(file_path, 'wb') as f:
                f.write(urlopen(t_url).read())

            poster = '../../poster/' + poster + '.jpg'
            self.result['poster'] = poster

        # Cast
        url2 = self.url + 'creditos/'
        http = urlopen(url2)

        soup2 = BeautifulSoup(http, 'lxml')

        if soup2.findAll('section', {'id': 'actors'}):
            section = soup2.find('section', {'id': 'actors'}).find_all('a')
            actors_characters = []
            for a in section:
                ac = []
                parent = a.find_parent('div').findNext('div')
                char = parent.text.strip()
                s = char.split(' : ')
                if s[0] != 'Personagem':
                    break
                ac.append(a.text.strip())
                ac.append(s[1].strip())
                actors_characters.append(ac)

            self.result['cast'] = actors_characters

        return self.result


