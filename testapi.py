
import os
import jwt
import pandas as pd
import datetime
from fastapi import FastAPI, Query, Depends, HTTPException, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
import mysql.connector
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()




# MYSQL CONNECTOR
import mysql.connector
cnx = mysql.connector.connect(user='root', password='admin', \
                              host = '127.0.0.1', database='movies')
cursor = cnx.cursor(buffered=True, dictionary=True)



# FAST API
templates = Jinja2Templates(directory="templates")
app = FastAPI()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request = request, name="home.html", context={"id": 'hello'}
    )


# @app.route('/api/v1/movies/all', methods=['GET'])
@app.get("/movies")
def get_movies(request: Request):
    query = ("SELECT title FROM movies;")
    cursor.execute(query)
    result = cursor.fetchall()
    return templates.TemplateResponse(
        request = request, name="movies.html", context={"result": result}
    )

@app.get("/actors")
def get_actors(request: Request):
    query = ("SELECT actor_name FROM actors;")
    cursor.execute(query)
    result = cursor.fetchall()
    return templates.TemplateResponse(
        request = request, name="actors.html", context={"result": result}
    )

@app.get("/directors")
def get_directors(request: Request):
    query = ("SELECT director_name FROM directors;")
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    return templates.TemplateResponse(
        request = request, name="directors.html", context={"result": result}
    )

@app.get("/composers")
def get_composers(request: Request):
    query = ("SELECT composer_name FROM composers;")
    cursor.execute(query)
    result = cursor.fetchall()
    return templates.TemplateResponse(
        request = request, name="composers.html", context={"result": result}
    )

@app.get("/years")
def get_years(request: Request):
    result = [str(item) for item in range(1960, 2026)]
    return templates.TemplateResponse(
        request = request, name="years.html", context={"result": result}
    )

@app.get("/countries")
def get_countries(request: Request):
    query = ("SELECT country FROM countries;")
    cursor.execute(query)
    result = cursor.fetchall()
    return templates.TemplateResponse(
        request = request, name="countries.html", context={"result": result}
    )

@app.get("/categories")
def get_categories(request: Request):
    query = ("SELECT category FROM categories;")
    cursor.execute(query)
    result = cursor.fetchall()
    return templates.TemplateResponse(
        request = request, name="categories.html", context={"result": result}
    )

