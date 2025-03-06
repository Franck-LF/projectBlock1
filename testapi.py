
import os
import jwt
import pandas as pd
import datetime
import asyncio
from fastapi import FastAPI, Query, Depends, HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
import pymongo
import mysql.connector
from typing import Optional
from pydantic import BaseModel
from urllib.parse import quote
from dotenv import load_dotenv


# Environnement variables
load_dotenv()

USER_MYSQL = os.getenv("USER_MYSQL")
PASSWORD_MYSQL = os.getenv("PASSWORD_MYSQL")
SECRET_KEY = os.getenv("SECRET_KEY")
API_PASSWORD = os.getenv("API_PASSWORD")

# print(USER_MYSQL, PASSWORD_MYSQL, SECRET_KEY, API_PASSWORD)





# MYSQL CONNECTOR
cnx = mysql.connector.connect(user=USER_MYSQL, password=PASSWORD_MYSQL, \
                              host = '127.0.0.1', database='movies')
cursor = cnx.cursor(buffered=True, dictionary=True)



# MYSQL CONNECTOR
client = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = client["allocine"]
col_movies = mydb["movies"]



# FAST API
templates = Jinja2Templates(directory="templates")
app = FastAPI()


# Configuration de la sécurité
security = HTTPBearer()

# Modèle pour l'authentification
class TokenRequest(BaseModel):
    password: str
    duration: Optional[int] = 3600  # in seconds


def create_jwt(duration: int) -> str:
    """
    Fonction qui permet de générer un token JWT
    
    :param duration: Durée de validité du token en secondes
    :return: Token JWT encodé
    """
    expiration = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    return jwt.encode(
        {"exp": expiration},
        SECRET_KEY, # Server side
        algorithm="HS256" # Hashing algorithm
    )
    
@app.post("/token")
def generate_token(request: TokenRequest):
    """
    Route qui permet de générer un token pour un utilisateur qui saisit son mot de passe
    
    :param request: Objet TokenRequest contenant le mot de passe et la durée
    :return: Token JWT
    """
    if request.password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_jwt(request.duration)
    return {"token": token}

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Fonction qui permet de vérifier le token JWT

    :param credentials: Credentials fournis via le bearer token
    :return: None
    :raises: HTTPException si le token est invalide ou expiré
    """
    try:
        jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")






# ------------------------------------
#     READ
# ------------------------------------

@app.get("/")
async def home(request: Request):
    '''
        Page d'accueil
    '''
    # return templates.TemplateResponse(
    #     request = request, name="home.html", context={"id": 'hello'}
    # )
    return {'title' : "Welcome"}

@app.get("/movies")
async def get_movies( credentials: HTTPAuthorizationCredentials = Depends(security),
                starting: Optional[str] = Query(None, alias="starting", description="filtrer les films dont le nom commence par 'starting'", example='termi'),
                like: Optional[str] = Query(None, alias="like", description="filtrer les films dont le nom contient 'like'"),
                actor1: Optional[str] = Query(None, alias="actor1", description="filtrer les films où a joué 'actor1'"),
                actor2: Optional[str] = Query(None, alias="actor2", description="filtrer les films où a joué 'actor2'"),
                producer: Optional[str] = Query(None, alias="producer", description="filtrer les films réalisés pas 'producer'"),
                composer: Optional[str] = Query(None, alias="composer", description="filtrer les films dont la musique a été composée par 'composer'"),
                category: Optional[str] = Query(None, alias="category", description="filtrer les films ayant une catégorie parmi (Action, Science Fiction, Historique, Bollywood, Western, Expérimental, Biopic, Drama, Judiciaire, Romance, Opéra, Drame, Fantastique, Musical, Animation, Aventure, Documentaire, Thriller, Famille, Epouvante-horreur, Guerre, Comédie musicale, Évènement Sportif, Comédie, Péplum, Arts Martiaux, Espionnage, Erotique, Comédie dramatique, Policier)"),
                year: Optional[int] = Query(None, alias="year", ge=1960, le=2025, description="filtrer les films en fonction de l'année de sortie"),
                limit: Optional[int] = Query(20, alias="limit", ge=1, le=100, description="Limite le nombre de résultats renvoyés")
                ):
    '''
        **Affiche une liste de films**
        
        Liste des paramètres utilisés pour filtrer les films à lister.
     - **starting**: filtrer les films dont le nom commence par 'starting',
     - **like**: filtrer les films dont le nom contient 'like'
     - **actor1**: permet de filtrer parmi les films où a joué "actor1" ,
     - **actor2**: permet de filtrer parmi les films où a joué "actor2",
     - **producer**: filtrer les films réalisés pas 'producer',
     - **composer**: filtrer les films dont la musique a été composée par 'composer',
     - **category**: filtrer les films ayant une catégorie spécifique,
     - **year**: filtrer les films en fonction de leur année de sortie,
     - **limit**: limite le nombre de résultats renvoyés.

    '''
    print("************ Movies *******************")
    # print(request.query_params.items())
    print("***************************************")

    await verify_token(credentials)

    query = "SELECT movie_id, title, release_date FROM movies"

    if starting:
        query = f"""SELECT movie_id, title, release_date FROM movies \
                    WHERE title LIKE '{starting}%'"""
    elif like:
        query = f"""SELECT movie_id, title, release_date FROM movies \
                    WHERE title LIKE '%{like}%'"""

    for item in [actor1, actor2] :
        if item:
            query += f""" INTERSECT \
                        SELECT m.movie_id AS movie_id, \
                                m.title AS 'title', \
                                m.release_date AS 'release_date'
                        FROM movies AS m \
                        JOIN actor_movie AS am ON am.movie_id = m.movie_id \
                        JOIN actors AS a ON a.actor_id = am.actor_id \
                        WHERE a.actor_name LIKE '%{item}%'
                        """

    if producer:
        query += f""" INTERSECT \
                    SELECT m.movie_id AS movie_id, \
                           m.title AS 'title', \
                           m.release_date AS 'release_date'
                    FROM movies AS m \
                    JOIN director_movie AS dm ON dm.movie_id = m.movie_id \
                    JOIN directors AS d ON d.director_id = dm.director_id \
                    WHERE d.director_name LIKE '%{producer}%'
                    """

    if composer:
        query += f""" INTERSECT \
                    SELECT m.movie_id AS movie_id, \
                           m.title AS 'title', \
                           m.release_date AS 'release_date'
                    FROM movies AS m \
                    JOIN composer_movie AS cm ON cm.movie_id = m.movie_id \
                    JOIN composers AS c ON c.composer_id = cm.composer_id \
                    WHERE c.composer_name LIKE '%{composer}%'
                    """
    
    if category:
        query += f""" INTERSECT \
                    SELECT m.movie_id AS movie_id, \
                           m.title AS 'title', \
                           m.release_date AS 'release_date'
                    FROM movies AS m \
                    JOIN category_movie AS cm ON cm.movie_id = m.movie_id \
                    JOIN categories AS c ON c.category_id = cm.category_id \
                    WHERE c.category LIKE '%{category}%'
                    """

    if category:
        query += f""" INTERSECT \
                    SELECT m.movie_id AS movie_id, \
                           m.title AS 'title', \
                           m.release_date AS 'release_date'
                    FROM movies AS m \
                    JOIN category_movie AS cm ON cm.movie_id = m.movie_id \
                    JOIN categories AS c ON c.category_id = cm.category_id \
                    WHERE c.category LIKE '%{category}%'
                    """

    if year:
        query += f""" INTERSECT \
                    SELECT movie_id, title, release_date \
                    FROM movies \
                    WHERE YEAR(release_date) = '{year}'
                    """

    query += f""" LIMIT {limit}"""

    print(query)

    cursor.execute(query)
    result = cursor.fetchall()
    return result

    # Old code where I was building the queries from the attributes in the URL

    # for key, value in request.query_params.items():
    #     if any([item in key for item in ['starting', 'name_starting', 'title_starting', 'film_starting']]):
    #         query = f"""SELECT movie_id, title, release_date FROM movies \
    #                  WHERE title LIKE '{value}%'"""
    #     elif any([item in key for item in ['like', 'name_like', 'title_like', 'film_like']]):
    #         query = f"""SELECT movie_id, title, release_date FROM movies \
    #                  WHERE title LIKE '%{value}%'"""

    # for key, value in request.query_params.items():
    #     if 'actor' in key:
    #         query += f""" INTERSECT \
    #                 SELECT m.movie_id AS movie_id, \
    #                        m.title AS 'title', \
    #                        m.release_date AS 'release_date'
    #                 FROM movies AS m \
    #                 JOIN actor_movie AS am ON am.movie_id = m.movie_id \
    #                 JOIN actors AS a ON a.actor_id = am.actor_id \
    #                 WHERE a.actor_name LIKE '%{value}%'
    #                 """

    #     if 'director' in key:
    #         query += f""" INTERSECT \
    #                 SELECT m.movie_id AS movie_id, \
    #                        m.title AS 'title', \
    #                        m.release_date AS 'release_date'
    #                 FROM movies AS m \
    #                 JOIN director_movie AS dm ON dm.movie_id = m.movie_id \
    #                 JOIN directors AS d ON d.director_id = dm.director_id \
    #                 WHERE d.director_name LIKE '%{value}%'
    #                 """
    
    #     if 'composer' in key:
    #         query += f""" INTERSECT \
    #                 SELECT m.movie_id AS movie_id, \
    #                        m.title AS 'title', \
    #                        m.release_date AS 'release_date'
    #                 FROM movies AS m \
    #                 JOIN composer_movie AS cm ON cm.movie_id = m.movie_id \
    #                 JOIN composers AS c ON c.composer_id = cm.composer_id \
    #                 WHERE c.composer_name LIKE '%{value}%'
    #                 """
            
    #     if 'category' in key:
    #         query += f""" INTERSECT \
    #                 SELECT m.movie_id AS movie_id, \
    #                        m.title AS 'title', \
    #                        m.release_date AS 'release_date'
    #                 FROM movies AS m \
    #                 JOIN category_movie AS cm ON cm.movie_id = m.movie_id \
    #                 JOIN categories AS c ON c.category_id = cm.category_id \
    #                 WHERE c.category LIKE '%{value}%'
    #                 """
    # bOrder = False
    # for key, value in request.query_params.items():
    #     if 'order' in key:
    #         if value in ['name', 'title', 'film']:
    #             query += " ORDER BY title"
    #             bOrder = True
    #         elif value in ['release_date', 'date', 'year']:
    #             query += " ORDER BY release_date"
    #             bOrder = True
    #         elif value in ['rating']:
    #             query += " ORDER BY star_rating"
    #             bOrder = True
    
    # if bOrder:
    #     for key, value in request.query_params.items():
    #         if 'desc' in key:
    #             if value in ['true', 'ok']:
    #                 query += " DESC"
    # else:
    #     query += " ORDER BY title"

    # for item in result:
    #     item['link'] = f"http://127.0.0.1:8000/movie?id={item['movie_id']}"

    # return templates.TemplateResponse(
    #     request = request, name="movies.html", context={"result": result}
    # )

# def get_movie(request: Request):

@app.get("/movie")
async def get_movie( credentials: HTTPAuthorizationCredentials = Depends(security),
                id: Optional[str] = Query(None, alias="id", description="identifiant du film recherché")):
    '''
        **Affiche les informations d'un film**

        Paramètre :
        **id**: identifiant du film recherché.
    '''

    print("************* Movie ******************")
    # print(request.path_params)
    # print(request.query_params.items())
    # print(request.query_params.values())
    print("**************************************")

    query = f"""
             SELECT m.title, m.release_date
             FROM movies AS m
             JOIN infos AS i ON i.info_id = m.info_id
             WHERE m.movie_id = '{id}'
             """
    cursor.execute(query)
    movie = cursor.fetchall()

    query = (f"""
             SELECT a.actor_id, a.actor_name
             FROM actors AS a
             JOIN actor_movie AS am ON am.actor_id = a.actor_id
             JOIN movies AS m ON m.movie_id = am.movie_id
             WHERE m.movie_id = '{id}';
             """)
    cursor.execute(query)
    actors = cursor.fetchall()

    query = (f"""
             SELECT d.director_id, d.director_name
             FROM directors AS d
             JOIN director_movie AS dm ON dm.director_id = d.director_id
             JOIN movies AS m ON m.movie_id = dm.movie_id
             WHERE m.movie_id = '{id}';
             """)
    cursor.execute(query)
    directors = cursor.fetchall()

    query = (f"""
             SELECT c.composer_id, c.composer_name
             FROM composers AS c
             JOIN composer_movie AS cm ON cm.composer_id = c.composer_id
             JOIN movies AS m ON m.movie_id = cm.movie_id
             WHERE m.movie_id = '{id}';
             """)
    cursor.execute(query)
    composers = cursor.fetchall()

    query = (f"""
             SELECT c.category_id, c.category
             FROM categories AS c
             JOIN category_movie AS cm ON cm.category_id = c.category_id
             JOIN movies AS m ON m.movie_id = cm.movie_id
             WHERE m.movie_id = '{id}';
             """)
    cursor.execute(query)
    categories = cursor.fetchall()

    
    # MongoBD Query
    #
    mongoDB = col_movies.find_one({ "title": f"{movie[0]['title']}" })
    movie[0]['url_thumbnail'] = mongoDB['url_thumbnail']
    movie[0]['plot'] = mongoDB['plot']
    # print('game', movie[0])
    # print('actor', actors)
    # print('director', directors)
    # print('category', categories)

    return {'movie' : movie, 'actors' : actors, 'directors' : directors, 'composers' : composers, 'categories' : categories}

    # Old code where I was building the queries from the attributes in the URL

    # assert 'id' in request.query_params.keys()
    # query = (f"""
    #         SELECT m.title, m.release_date
    #         FROM movies AS m
    #         JOIN infos AS i ON i.info_id = m.info_id
    #         WHERE m.movie_id = '{request.query_params['id']}';
    #         """)
    # cursor.execute(query)
    # movie = cursor.fetchall()

    # query = (f"""
    #         SELECT a.actor_id, a.actor_name
    #         FROM actors AS a
    #         JOIN actor_movie AS am ON am.actor_id = a.actor_id
    #         JOIN movies AS m ON m.movie_id = am.movie_id
    #         WHERE m.movie_id = '{request.query_params['id']}';
    #         """)
    # cursor.execute(query)
    # actors = cursor.fetchall()

    # for item in actors:
    #     item['link'] = f"http://127.0.0.1:8000/movies?actor={quote(item['actor_name'])}"

    # query = (f"""
    #         SELECT d.director_id, d.director_name
    #         FROM directors AS d
    #         JOIN director_movie AS dm ON dm.director_id = d.director_id
    #         JOIN movies AS m ON m.movie_id = dm.movie_id
    #         WHERE m.movie_id = '{request.query_params['id']}';
    #         """)
    # cursor.execute(query)
    # directors = cursor.fetchall()

    # for item in directors:
    #     item['link'] = f"http://127.0.0.1:8000/movies?director={quote(item['director_name'])}"

    # query = (f"""
    #         SELECT c.composer_id, c.composer_name
    #         FROM composers AS c
    #         JOIN composer_movie AS cm ON cm.composer_id = c.composer_id
    #         JOIN movies AS m ON m.movie_id = cm.movie_id
    #         WHERE m.movie_id = '{request.query_params['id']}';
    #         """)
    # cursor.execute(query)
    # composers = cursor.fetchall()

    # for item in composers:
    #     item['link'] = f"http://127.0.0.1:8000/movies?composer={quote(item['composer_name'])}"

    # query = (f"""
    #         SELECT c.category_id, c.category
    #         FROM categories AS c
    #         JOIN category_movie AS cm ON cm.category_id = c.category_id
    #         JOIN movies AS m ON m.movie_id = cm.movie_id
    #         WHERE m.movie_id = '{request.query_params['id']}';
    #         """)
    # cursor.execute(query)
    # categories = cursor.fetchall()

    # for item in categories:
    #     item['link'] = f"http://127.0.0.1:8000/movies?category={quote(item['category'])}"

    # print('game', game[0])
    # #
    # # MongoBD Query
    # #
    # mongoDB = col_movies.find_one({ "title": f"{game[0]['title']}" })
    # game[0]['url_thumbnail'] = mongoDB['url_thumbnail']
    # game[0]['plot'] = mongoDB['plot']
    # print('game', game[0])
    # print('actor', actors)
    # print('director', directors)
    # print('category', categories)

    # return templates.TemplateResponse(
    #     request = request, name="movie.html", context={"movie": movie, "actors": actors, 
    #                                                    "directors": directors, "composers": composers,
    #                                                    "categories": categories}
    # )

@app.get("/actors")
def get_actors(request: Request):
    '''
        Liste des acteurs
    '''
    query = ("SELECT actor_name FROM actors ORDER BY actor_name;")
    cursor.execute(query)
    result = cursor.fetchall()

    for item in result:
        item['link'] = f"http://127.0.0.1:8000/movies?actor={quote(item['actor_name'])}"

    return templates.TemplateResponse(
        request = request, name="actors.html", context={"result": result}
    )

@app.get("/directors")
def get_directors(request: Request):
    '''
        Liste des réalisateurs
    '''
    query = ("SELECT director_name FROM directors ORDER BY director_name;")
    cursor.execute(query)
    result = cursor.fetchall()

    for item in result:
        item['link'] = f"http://127.0.0.1:8000/movies?director={quote(item['director_name'])}"

    return templates.TemplateResponse(
        request = request, name="directors.html", context={"result": result}
    )

@app.get("/composers")
def get_composers(request: Request):
    '''
        Liste des compositeurs
    '''
    query = ("SELECT composer_name FROM composers ORDER BY composer_name;")
    cursor.execute(query)
    result = cursor.fetchall()

    for item in result:
        item['link'] = f"http://127.0.0.1:8000/movies?composer={quote(item['composer_name'])}"

    print(result)
    return templates.TemplateResponse(
        request = request, name="composers.html", context={"result": result}
    )

@app.get("/years")
def get_years(request: Request):
    '''
        Liste des années
    '''
    result = list(range(2025, 1959))

    # for item in result:
    #     item['link'] = f"http://127.0.0.1:8000/movies?year={quote(item['category'])}"

    return templates.TemplateResponse(
        request = request, name="years.html", context={"result": result}
    )

@app.get("/countries")
def get_countries(request: Request):
    '''
        Liste des pays
    '''
    query = ("SELECT country FROM countries ORDER BY country;")
    cursor.execute(query)
    result = cursor.fetchall()

    for item in result:
        item['link'] = f"http://127.0.0.1:8000/movies?country={quote(item['country'])}"

    return templates.TemplateResponse(
        request = request, name="countries.html", context={"result": result}
    )

@app.get("/categories")
def get_categories(request: Request):
    '''
        Liste des catégories
    '''
    query = ("SELECT category FROM categories ORDER BY category;")
    cursor.execute(query)
    result = cursor.fetchall()

    print(result)

    for item in result:
        item['link'] = f"http://127.0.0.1:8000/movies?category={quote(item['category'])}"

    return templates.TemplateResponse(
        request = request, name="categories.html", context={"result": result}
    )


# ------------------------------------
#     Create
# ------------------------------------



