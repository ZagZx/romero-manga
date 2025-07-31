from quart import Quart, render_template, request, Response, url_for, redirect
from quart_auth import login_user, logout_user, login_required, current_user, QuartAuth
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import asyncio

import os
import time

from database import Database
from models import User

from utils.api import Manga, search_manga_by_title


DB_PATH = './database/database.db'
SQL_PATH = './database/schema.sql'

db = Database(DB_PATH)

DROPAR_TABELAS = False
# evitar drop das tabelas toda vez que rodar o codigo
if not os.path.exists(DB_PATH) or DROPAR_TABELAS:
    db.run_sql_file(SQL_PATH) # cria as tabelas | COLOCAR ISSO NO build.py DEPOIS

load_dotenv('./.env')

app = Quart(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# tirar isso se for hospedar em https
app.config['SESSION_COOKIE_SECURE'] = False
app.config['DEBUG'] = True

login_manager = QuartAuth()
login_manager.init_app(app)


# FLASK LOGIN

# login_manager.login_view = 'login'

# @login_manager.user_loader
# def load_user(user_id):
#     user_data = db.run_query('SELECT id, username, email FROM users WHERE id = ?', user_id)
#     if user_data:
#         user_data = user_data[0]
#         return User(id=user_data[0], username=user_data[1], email=user_data[2])
#     return None

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/search')
async def search():
    # precisa de: titulo, id, cover_filename
    title = request.args.get('query')
    results = await search_manga_by_title(title)

    mangas_list = []
    for manga_data in results:
        manga = Manga(manga_data['id'])
        manga.set_manga_data(manga_data)

        # inicia as duas tarefas ao mesmo tempo e retorna as duas juntas
        title = await manga.get_title()

        mangas_list.append(
            {
                "id": manga.id,
                "title": title,
                "cover_image": url_for('cover_proxy_by_manga_id', manga_id = manga.id)
            }
        )
        
        # print(manga.title)
    return await render_template('search.html', mangas_list = mangas_list)

@app.route('/cadastro', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        username = form.get('username')
        email = form.get('email')
        password_hash = generate_password_hash(form.get('password'))

        if not db.run_query(f"SELECT * FROM users WHERE email = ?", email):
            db.run_query(f"INSERT INTO users(username, email, password_hash) VALUES (?, ?, ?)", (username, email, password_hash))
            return redirect(url_for('login'))
        else: 
            print('Já existe um usuário cadastrado com esse email')
            return await render_template('register.html') # colocar mensagem de erro
    if request.method == 'GET':
        return await render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
async def login():
    # fazer tratamento de erros caso a senha esteja errada
    if request.method == 'POST':
        form = await request.form
        email = form.get('email')
        password = form.get('password')

        user_data = db.run_query('SELECT id, username, password_hash FROM users WHERE email = ?', email)
        if user_data:
            user_data = user_data[0]
            if check_password_hash(user_data[2], password):
                user = User(auth_id=user_data[0], username=user_data[1], email=email)
                login_user(user)
                return redirect(url_for('index'))
            else:
                print('Senha errada')
        # else:
        #     print('Email não cadastrado')
        return await render_template('login.html') # colocar mensagem de erro
    elif request.method == 'GET':
        return await render_template('login.html')

@app.route('/logout')
@login_required
async def logout():
    logout_user()

    return redirect(url_for('index'))

@app.route('/cover-proxy/<manga_id>/<filename>')
async def cover_proxy(manga_id:str, filename:str):
    '''
    A API do MangaDex bloqueia requisições de imagens feitas direto do HTML para evitar o consumo excessivo do servidor deles,
    então para colocar as imagens no HTML é preciso hospedar elas no meu servidor primeiro e então fazer a requisição da imagem pelo url do proxy.
    '''

    before = time.time()
    
    manga = Manga(manga_id)

    if filename and manga_id:
        cover_image = await manga.get_cover_image()
        print(cover_image)

        now = time.time()
        print('\n====COVER PROXY====')
        print(f'Mangá: {await manga.get_title()}')
        print(f'Tempo de Execução: {round(now-before,2)}s\n')

        return Response(cover_image.content, content_type=cover_image.headers['Content-Type'])
    
@app.route('/cover_proxy/<manga_id>')
async def cover_proxy_by_manga_id(manga_id):
    '''
    Gambiarra para acelerar a pesquisa, ao invés de passar os filenames e travar a página por muito tempo,
    é passado no dicionário um url_for para esta rota e nela é obtido o filename e então ela redireciona para a cover_proxy.

    Ou seja, aumenta o tempo de carregamento das imagens para diminuir consideravelmente o tempo de tela travada.
    '''

    manga = Manga(manga_id)
    cover_filename = await manga.get_cover_filename()
    return redirect(url_for('cover_proxy', manga_id = manga_id, filename = cover_filename))
