from os import getcwd
from unicodedata import normalize

from PyQt5.QtWidgets import QApplication

from db.db_model import Media, MovieCast, SeriesCast

path = getcwd()


def write_series_html(session, series):
    """
    Writing html page for view movie or series.

    :param session: SQLAlchemy orm session.
    :param series: The series object.
    :return: The view url.
    """
    QApplication.processEvents()
    view_css = '../../styles/views.css'

    year = ''
    seasons = ''
    poster = ''
    html_summary = ''
    html_categories = ''
    html_actors = ''
    html_creator = ''
    html_media = ''
    html_original_name = ''

    if series.year:
        year = series.year

    if series.seasons:
        seasons = series.seasons

    if series.media_id:
        query = session.query(Media).filter(Media.id == series.media_id).first()
        html_media = '\t\t\t<p class="fields"><span>Mídia:&nbsp;&nbsp;' \
                     '</span>' + query.name + '</p>\n'

    if series.summary:
        text = series.summary.replace('\n', '<br>')
        html_summary = '\t\t\t<p class="summary">' + text + '</p>\n'

    categories = ''
    if series.category_1_id:
        categories = series.category_1.name

    if series.category_2_id:
        categories += ', ' + series.category_2.name

    html_categories = '\t\t\t<p class="fields"><span>' \
                      'Categorias:&nbsp;&nbsp;' \
                      '</span>' + categories + '</p>\n'

    if series.series_cast:
        actors_list = []
        val = session.query(SeriesCast).\
            filter(SeriesCast.series_id == series.id,
                   SeriesCast.star.is_(True)).all()

        if len(val) != 0:
            for a in series.series_cast:
                if a.star:
                    actors_list.append([a.cast.actors.name,
                                        a.cast.characters.name])
        else:
            actors = session.query(SeriesCast).\
                filter(SeriesCast.series_id == series.id, SeriesCast.order < 4)\
                .all()
            for a in actors:
                actors_list.append([a.cast.actors.name,
                                    a.cast.characters.name])

        html_actors = '\t\t\t<p class="fields">' \
                      '<span>Elenco:&nbsp;&nbsp;</span></p>\n\t\t\t<ul>\n'

        for a, c in actors_list:
            html_actors += '\t\t\t\t<li>' + a + '&nbsp;&rarr;&nbsp; ' + c + '</li>\n'

        html_actors += '\t\t\t</ul>'

    creator = ''
    if series.creators:
        total = len(series.creators)
        end = total - 1
        for i in range(total):
            if i < end:
                creator += series.creators[i].creator.name + ', '
                continue
            creator += series.creators[i].creator.name

        if total == 1:
            html_creator = '\t\t\t<p class="fields">' \
                                    '<span>Criador:&nbsp;&nbsp;' \
                                    '</span>' + creator + '</p>\n'
        elif total > 1:
            html_creator = '\t\t\t<p class="fields">' \
                                    '<span">' \
                                    'Criadores:&nbsp;&nbsp;' \
                                    '</span>' + creator + '</p>\n'

    if series.original_name:
        html_original_name = '\t\t\t<p class="fields"><span>' \
                             'Título Original:&nbsp;&nbsp;</span>' + \
                             series.original_name + '</p>\n'

    if series.poster:
        poster = series.poster
    else:
        poster = '../../images/poster_placeholder.png'

    html_ini = '' \
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 ' \
               'Transitional//EN http://www.w3.org/TR/html4/loose.dtd">\n' \
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt-br" ' \
               'lang="pt-br">\n' \
        '<head>\n' \
        '\t<meta http-equiv="Content-Type" content="text/html; ' \
               'charset=UTF-8" />\n' \
        '\t<link rel="stylesheet" type="text/css" href="' + view_css + \
               '" media="all">\n' \
        '</head>\n' \
        '<body>\n' \
        '\t<div id="wrap">\n' \
        '\t\t<div class="poster">\n' \
        '\t\t\t<img src="' + poster + '" >\n' \
        '\t\t</div>\n' \
        '\t\t<div class="movie">\n' \
        '\t\t<h2>' + series.name + '</h2>\n' \
        '\t\t<p class="year"><span>Ano:&nbsp;&nbsp;</span>' + year + \
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span>' \
        'Temporadas:&nbsp;&nbsp;</span>' + seasons + '</p>\n' \

    html_end = '' \
        '\t\t</div>\n' \
        '\t</div>\n' \
        '</body>\n' \
        '</html>\n'

    html = html_ini + html_summary + html_categories + html_creator + \
           html_media + html_original_name + html_actors + html_end

    title = series.name.lower()
    char = [' ', '.', '/', '\\', ',', ';', '"', "'", "`", "'"]
    for c in char:
        title = title.replace(c, '_')
    title = normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')

    view = '/views/series/' + title + '.html'
    file_path = path + view
    with open(file_path, 'w') as f:
        f.write(html)

    return view