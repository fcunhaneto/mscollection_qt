import os
import re

from urllib.request import urlopen
from unicodedata import normalize

from bs4 import BeautifulSoup

import texts

path = os.getcwd()


class ImdbScraping:
    def __init__(self, url, type):
        """
        This class scrapping series information from site IMDB.
        (https://www.imdb.com/) base in given url.

        :param url: Url site IMDB where the info are.
        :param type: Type object, movie or series, are scrapping.
        """
        self.http = urlopen(url)
        self.soup = BeautifulSoup(self.http, 'lxml')
        self.type = type
        self.result = {
            'title': None,
            'original_title': None,
            'year': None,
            'time': None,
            'poster': None,
            'summary': None,
            'category_1': None,
            'category_2': None,
            'director_creator': None,
            'cast': None
        }

    def get_values(self):
        # Title
        get_title = self.soup.find('div', {'class': 'title_wrapper'})
        if get_title:
            if self.type == 'movie':
                self.result['title'] = get_title.h1.text[:-7].strip()
            elif self.type == 'series':
                self.result['title'] = get_title.h1.text.strip()

        # Original Title
        get_original_title = get_title.find('div', {'class': 'originalTitle'})

        if get_original_title:
            original_title_text = get_original_title.text.split(' ')

            original_title = ''
            for o in original_title_text[:-2]:
                original_title = original_title + ' ' + o

            self.result['original_title'] = original_title.strip()

        # Year
        get_date = get_title.find('a', {'title': 'See more release dates'})
        if get_date:
            date = get_date.text.split()
            if self.type == 'movie':
                self.result['year'] = date[2]
            elif self.type == 'series':
                self.result['year'] = date[2][1:5]

        # Time
        get_time = self.soup.find('div', {'class': 'subtext'}).time.text
        self.result['time'] = get_time.strip()

        # Poster
        poster = self.soup.find('div', {'class': 'poster'}).a.img
        if poster:
            url = poster['src']
            name = poster['title'].lower()

            chars = ['\\', '/', '|', '?', '>', '<', '*', ':', '"']

            for c in chars:
                file = name.replace(c, '_')

            file = normalize('NFKD', file).encode('ASCII', 'ignore').\
                decode('ASCII')

            file_path = path + '/poster/' + poster + '.jpg'
            with open(file_path, 'wb') as f:
                f.write(urlopen(url).read())

            self.result['poster'] = '../../poster/' + poster + '.jpg'

        # Summary
        get_summary = self.soup.find('div', {'class': 'summary_text'})
        if get_summary:
            self.result['summary'] = get_summary.text.strip()

        # Categories
        a_categories = get_title.findAll('a')
        if a_categories:
            categories = []

            for c in a_categories:
                if '/search/title?genres' in c['href']:
                    imdb_category = c.text
                    categories.append(texts.imdb_categories[imdb_category])

            total = len(categories)
            if total > 1:
                self.result['category_1'] = categories[0]
                self.result['category_2'] = categories[1]
            elif total > 0:
                self.result['category_1'] = categories[0]

        # Director
        get_credits = self.soup.find('div', {
            'class': 'credit_summary_item'
        })
        director_creator = get_credits.h4
        str_director_creator = ''
        if director_creator:
            str_director_creator = director_creator.text.strip()

        if str_director_creator == 'Director:':
            director_find = self.soup.find(
                'h4', {'class': 'inline'}, text=re.compile('Director')). \
                find_next_sibling("a")
            if director_find:
                self.result['director_creator'] = director_find.text.strip()
        elif str_director_creator == 'Directors:':
            links = get_credits.findAll('a')
            director = links[0].text
            self.result['director_creator'] = director
        elif str_director_creator == 'Creator:':
            creator_find = self.soup.find(
                'h4', {'class': 'inline'}, text=re.compile('Creator')). \
                find_next_sibling("a")
            if creator_find:
                self.result['director_creator'] = creator_find.text
        elif str_director_creator == 'Creators:':
            creator_find = self.soup.find('div',
                                          {'class': 'credit_summary_item'})
            links = creator_find.findAll('a')
            creator = links[0].text

            self.result['director_creator'] = creator

        # Cast
        table = self.soup.find('table', {'class': 'cast_list'})
        if table:
            rows = table.findAll('tr')
            if rows:
                names = []
                for row in rows:
                    col = row.td.next_siblings
                    for c in col:
                        t = c.find('a')
                        if t and not isinstance(t, int):
                            s = t.text.strip()
                            names.append(s)
                actor_character = []
                cast = []
                for n in range(len(names)):
                    num = n % 2
                    if num == 0:
                        actor_character.append(names.pop(0))
                    else:
                        actor_character.append(names.pop(0))
                        cast.append(actor_character)
                        actor_character = []

                self.result['cast'] = cast

        # Actor
        rows = self.soup.findAll('td', {'class': 'primary_photo'})
        actor = []
        for row in rows:
            s = row.findNext('td').get_text()
            s = s.replace('\n', '')
            actor.append(s)

        # Character
        chars = self.soup.findAll('td', {'class': 'character'})
        character = []
        for c in chars:
            s = c.text.strip()
            s = s.replace('\n', '')

            if '/' in s:
                b = s.split('/')
                total = len(b)
                i = 0
                char = b[0]
                for j in range(1, total):
                    r = b[j].strip()
                    if i < total:
                        char += '/ ' + r
                    else:
                        char += r
                    i += 1
                s = char

            character.append(s)

        ac = []
        total = len(actor)
        for i in range(total):
            ac.append([actor[i], character[i]])

        self.result['cast'] = ac

        return self.result
