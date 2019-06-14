# install

movie_s = 'Filme'
movie_p = 'Filmes'
series_s = 'Série'
series_p = 'Séries'
title_s = 'Título'
title_p = 'Títulos'
director_s = 'Diretor'
director_p = 'Diretores'
creator_s = 'Criador'
creator_p = 'Criadores'
category_s = 'Categoria'
category_p = 'Categorias'
character_s = 'Personagem'
character_p = 'Personagens'
media_s = 'Mídia'
media_p = 'Mídias'
season_s = 'Temporada'
season_p = 'Temporadas'
box = 'Box'
actor_s = 'Ator/Atriz'
actor_p = 'Atores/Atrizes'

keyword = 'Palavra Chave'
mscollection_name = 'Coleção de Filmes e Séries'
mscollection_comment = 'Um programa que ajuda você a gerenciar sua coleção de' \
                       ' filmes e séries.'

window_principal_title = 'Coleções de Filmes e Séries'
window_install_title = 'Instalação de "Coleções de Filmes e Séries"'
windows_error_database = 'Error'
db_error = 'Erro Com Banco De Dados'
msg_db_conn = '<html><body><p style="color:red;">Erro ao tentar conectar com ' \
              'o banco de dados.</p></body></html'

lb_label = 'Selecione o SGBD:'
lb_db_name = 'Nome do BD:'
lb_host = 'Hospedeiro(Host):'
lb_port = 'Porta(Port):'
lb_user = 'Usuário(User):'
lb_pw = 'Senha(Password):'

install_text_1 = '<html><body style="font-family:Ubuntu; font-size:12pt; ' \
                 'font-weight:400; font-style:normal;">' \
                 '<p>O programa MSCollection armazena os dados de seus ' \
                 'filmes e séries em um Banco de Dados (BD) e para gerenciar' \
                 ' o BD é necessário um Sistema de Gerenciamento de ' \
                 'Banco de Dados (SGBD).</p>' \
                 '<p>Durante essa instalação disponibilizamos três ' \
                 'gerenciadores de banco de dados sendo eles SQLite, ' \
                 'PostgreSQL e MySQL para que você selecione um deles logo ' \
                 'abaixo e ele será configurado automaticamente com todas as ' \
                 'necessidades que o MSCollection requer. Os gerenciadores  ' \
                 'PostgreSQL e MySQL requerem que você inseria alguns outros ' \
                 'dados para sua instalação se você não se sentir a vontade ' \
                 'com isso use o SQLite.</p>' \
                 '</body></html>'

database_exist = '<html><body style="color: red; font-size: 28px; ' \
                 'font-weight: bold"><p>O Banco de Dados já existe ou:</p>' \
                 '<p>Não conseguimos acessá-lo com os dados fornecidos.</p>' \
                 '</body></html>'

connection_rejected = '<html><body><p style="color: red; font-size: 28px; ' \
                      'font-weight: bold">Conexão Rejeitada</p></body></html>'


def install_db_select(db):
    text = '<html><body style="font-family:Ubuntu; font-size:11pt; ' \
           'font-weight:400; font-style:normal;">' \
           '<p>Ok sua opção foi pelo ' + db + ' e já deixamos alguns campos ' \
           'abaixo preenchidos com os valores padrão, inclusive o nome do ' \
           'Banco de Dados, caso pretenda usar um nome para o Banco de Dados ' \
           'diferente do sugerido de preferência aos seguintes padrões:' \
           '</p><ol style="-qt-list-indent: 1;"><li>Não use acentos exemplo:' \
           '<br />FilmesSéries não é um bom nome use FilmeSeries sem acento.' \
           '<br /></li><li>Não separe os nomes por espaço use sintaxe ' \
           'CamelCase ou use os separadores "_", "-" exemplo:<br />' \
           'FilmesSeries ou filme_series ou filmes-series</li></ol>' \
           '<p>Para finalizar a instalação clique no botão ok</p>' \
           '</body></html>'
    return text


def cant_copy(db):
    if db == 'postgres':
        name = 'PostgreSQL'
    elif db == 'mysql':
        name = 'MysSQL'
    else:
        name = 'SQLite'

    db += '_settings.py'

    text = '<html><body><p>Não foi possível criar o arquivo db_settings.py ' \
           'para o ' + name + '.</p><p>Tente criá-lo manualmente:</p>' \
           '<ol><li>Remova o arquivo db_settings.py do diretório db;</li>' \
           '<li>Copie o arquivo ' + db + ' do diretório install para o ' \
           'diretório db;</li><li>Renomeie o arquivo ' + db + \
           ' como db_settings.py</li></ol></body></html>'

    return text
