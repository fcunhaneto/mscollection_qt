import datetime

from PyQt5.QtWidgets import QMessageBox

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \
    Sequence, UniqueConstraint, Boolean, TEXT, DateTime
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from install import texts_install as texts

Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column(Integer, Sequence('keyword_id_seq'), primary_key=True)
    name = Column(String(20), unique=True, index=True, nullable=False)


class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, Sequence('media_id_seq'), primary_key=True)
    name = Column(String(10), unique=True, index=True, nullable=False)


class Actor(Base):
    __tablename__ = 'actor'
    id = Column(Integer, Sequence('actor_id_seq'), primary_key=True)
    name = Column(String(45), unique=True, index=True, nullable=False)


class Character(Base):
    __tablename__ = 'character'
    id = Column(Integer, Sequence('character_id_seq'), primary_key=True)
    name = Column(String(45), unique=True, index=True, nullable=False)


class Cast(Base):
    __tablename__ = 'cast'
    id = Column(Integer, Sequence('cast_id_seq'), primary_key=True)
    actor_id = Column(Integer, ForeignKey('actor.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('character.id'), nullable=False)

    actors = relationship(Actor)
    characters = relationship(Character)

    UniqueConstraint(actor_id, character_id)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    name = Column(String(20), unique=True, index=True, nullable=False)

class Director(Base):
    __tablename__ = 'director'
    id = Column(Integer, Sequence('director_id_seq'), primary_key=True)
    name = Column(String(45), unique=True, index=True, nullable=False)


class Box(Base):
    __tablename__ = 'box'
    id = Column(Integer, Sequence('box_id_seq'), primary_key=True)
    name = Column(String(150), unique=True, index=True, nullable=False)


class MovieDirector(Base):
    __tablename__ = 'movie_director'
    id = Column(Integer, Sequence('movie_director_id_seq'), primary_key=True)
    movie_id = Column(Integer, ForeignKey('movie.id', ondelete='CASCADE'),
                      nullable=False)
    director_id = Column(Integer, ForeignKey('director.id'), nullable=False)
    order = Column(Integer, default=1)

    director = relationship(Director)

    UniqueConstraint(movie_id, director_id)


class MovieCast(Base):
    __tablename__ = 'movie_cast'
    id = Column(Integer, Sequence('movie_cast_id_seq'), primary_key=True)
    movie_id = Column(Integer, ForeignKey('movie.id', ondelete='CASCADE'),
                      nullable=False)
    cast_id = Column(Integer, ForeignKey('cast.id'), nullable=False)
    order = Column(Integer, nullable=False, default=1)
    star = Column(Boolean, default=False)

    cast = relationship(Cast)

    UniqueConstraint(movie_id, cast_id)


class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, Sequence('movie_id_seq'), primary_key=True)
    name = Column(String(100), nullable=False)
    original_name = Column(String(100), nullable=True)
    year = Column(String(4), nullable=True)
    time = Column(String(10), nullable=True)
    media_id = Column(Integer, ForeignKey('media.id'), nullable=True)
    category_1_id = Column(Integer, ForeignKey('category.id'), nullable=True,
                           default=None)
    category_2_id = Column(Integer, ForeignKey('category.id'), nullable=True,
                           default=None)
    summary = Column(TEXT, nullable=True)
    box_id = Column(Integer, ForeignKey('box.id'), nullable=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id'), nullable=True)
    poster = Column(String(255), nullable=True)
    view = Column(String(255), nullable=True)
    search_url = Column(String(255), nullable=True)
    web_url = Column(String(255), nullable=True)
    date_create = Column(DateTime, nullable=False)
    date_edit = Column(DateTime, default=datetime.datetime.utcnow(),
                       onupdate=datetime.datetime.utcnow(), nullable=False)

    media = relationship(Media, uselist=False)
    box = relationship(Box, uselist=False)
    keyword = relationship(Keyword, uselist=False)
    category_1 = relationship(Category, foreign_keys=[category_1_id],
                              uselist=False)
    category_2 = relationship(Category, foreign_keys=[category_2_id],
                              uselist=False)
    directors = relationship(MovieDirector, passive_deletes=True)
    movie_cast = relationship(MovieCast, order_by='desc(MovieCast.star)',
                              passive_deletes=True)

    UniqueConstraint(name, year)


class Creator(Base):
    __tablename__ = 'creator'
    id = Column(Integer, Sequence('creator_id_seq'), primary_key=True)
    name = Column(String(45), unique=True, index=True, nullable=False)


class SeriesCreator(Base):
    __tablename__ = 'series_creator'
    id = Column(Integer, Sequence('series_creator_id_seq'), primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'),
                       nullable=False)
    creator_id = Column(Integer, ForeignKey('creator.id'), nullable=False)
    order = Column(Integer, default=1)

    creator = relationship(Creator)

    UniqueConstraint(series_id, creator_id)


class SeriesCast(Base):
    __tablename__ = 'series_cast'
    id = Column(Integer, Sequence('series_cast_seq'), primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'),
                       nullable=False)
    cast_id = Column(Integer, ForeignKey('cast.id'), nullable=False)
    order = Column(Integer, nullable=False, default=1)
    star = Column(Boolean, default=False)

    cast = relationship(Cast)

    UniqueConstraint(series_id, cast_id)


class Series(Base):
    __tablename__ = 'series'
    id = Column(Integer, Sequence('series_id_seq'), primary_key=True)
    name = Column(String(100), nullable=False)
    original_name = Column(String(100), nullable=True)
    year = Column(String(4), nullable=True)
    seasons = Column(String(4), nullable=True)
    media_id = Column(Integer, ForeignKey('media.id'), nullable=True,
                      default=None)
    category_1_id = Column(Integer, ForeignKey('category.id'), nullable=True,
                           default=None)
    category_2_id = Column(Integer, ForeignKey('category.id'), nullable=True,
                           default=None)
    summary = Column(TEXT, nullable=True)
    keyword_id = Column(Integer, ForeignKey('keyword.id'), nullable=True)
    poster = Column(String(255), nullable=True)
    view = Column(String(255), nullable=True)
    search_url = Column(String(255), nullable=True)
    web_url = Column(String(255), nullable=True)
    date_create = Column(DateTime, nullable=False)
    date_edit = Column(DateTime, default=datetime.datetime.utcnow(),
                       onupdate=datetime.datetime.utcnow(), nullable=False)

    media = relationship(Media, uselist=False)
    keyword = relationship(Keyword, uselist=False)
    category_1 = relationship(Category, foreign_keys=[category_1_id],
                              uselist=False)
    category_2 = relationship(Category, foreign_keys=[category_2_id],
                              uselist=False)
    creators = relationship(SeriesCreator, passive_deletes=True)
    series_cast = relationship(SeriesCast, order_by='desc(SeriesCast.star)',
                               passive_deletes=True)

    UniqueConstraint(name, year)


class SeasonCast(Base):
    __tablename__ = 'season_cast'
    id = Column(Integer, Sequence('season_cast_seq'), primary_key=True)
    season_id = Column(Integer, ForeignKey('season.id', ondelete='CASCADE'),
                       nullable=False)
    cast_id = Column(Integer, ForeignKey('cast.id'), nullable=False)
    star = Column(Boolean, default=False)
    order = Column(Integer, nullable=False, default=1)

    cast = relationship(Cast)


class Season(Base):
    __tablename__ = 'season'
    id = Column(Integer, Sequence('season_id_seq'), primary_key=True)
    series_id = Column(Integer, ForeignKey('series.id', ondelete='CASCADE'),
                       nullable=False)
    season_num = Column(Integer, nullable=False, default=1)
    year = Column(String(4), nullable=True)
    media_id = Column(Integer, ForeignKey('media.id'), nullable=True)

    media = relationship(Media, uselist=False)
    cast = relationship(SeasonCast, order_by='desc(SeasonCast.star)')
    series = relationship(Series)

    UniqueConstraint(series_id, season_num)


class Episode(Base):
    __tablename__ = 'episode'
    id = Column(Integer, Sequence('epispode_id_seq'), primary_key=True)
    season_id = Column(Integer, ForeignKey('season.id', ondelete='CASCADE'),
                       nullable=False)
    code = Column(String(5), nullable=False)
    name = Column(String(100), nullable=False)
    summary = Column(TEXT, nullable=True)
    view = Column(String(255), nullable=True)

    season = relationship(Season, order_by='desc(Episode.code)')

    UniqueConstraint(season_id, code)


def create_tables(url):
    engine = None
    try:
        engine = create_engine(url)
    except OperationalError as error:
        QMessageBox(texts.db_error, texts.msg_db_conn,
                    QMessageBox.Critical, QMessageBox.Close, str(error))
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all([
        Media(name='Blu-Ray'),
        Media(name='DVD'),
        Media(name='HD'),
        Media(name='Web'),
    ])
    categories = [
        Category(name='Ação'), Category(name='Adulto'),
        Category(name='Aventura'), Category(name='Animação'),
        Category(name='Biografia'), Category(name='Comédia'),
        Category(name='Policial'), Category(name='Documentário'),
        Category(name='Drama'), Category(name='Família'),
        Category(name='Fantasia'), Category(name='Film Noir'),
        Category(name='Histórico'), Category(name='Terror'),
        Category(name='Musical'), Category(name='Mistério'),
        Category(name='Romance'), Category(name='Ficção Científica'),
        Category(name='Esporte'), Category(name='Super-Heróis'),
        Category(name='Suspense'), Category(name='Guerra'),
        Category(name='Faroeste')
    ]
    session.add_all(categories)
    session.commit()
