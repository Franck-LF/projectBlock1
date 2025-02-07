# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:49:40 2024

@author: Franck

src: https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3-fr
src: https://jinja.palletsprojects.com/en/stable/templates/
src: https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/
src: https://python.developpez.com/tutoriel/intro-flask-python3/
src: https://www.geeksforgeeks.org/patch-method-python-requests/

"""


# Space HTML = %20

# Import de bibliothèques
import numpy as np
import pandas as pd

import flask
from flask import request, jsonify, render_template

import pymysql
from sqlalchemy import text
from sqlalchemy import create_engine, MetaData, Table, text




# MYSQL CONNECTOR
import mysql.connector
cnx = mysql.connector.connect(user='root', password='admin', \
                              host = '127.0.0.1', database='games')
cursor = cnx.cursor(buffered=True, dictionary=True)



# SQL ALCHEMY
# DEFINE THE DATABASE CREDENTIALS
user = 'root'
password = 'admin'
host = '127.0.0.1'
port = 3306
database = 'games'

# PYTHON FUNCTION TO CONNECT TO THE MYSQL DATABASE AND RETURN THE SQLACHEMY ENGINE OBJECT
def get_connection():
    return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
    )

engine = None
if __name__ == '__main__':

    try:
        # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
        engine = get_connection()
        print(
            f"Connection to the {host} for user {user} created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)
assert engine



list_tables = ['games', 'publishers', 'developers', 'tags', 'genres', 'usernames', 'reviews'] 
dict_order = {'name':'game_name', 'date':'release_date', 'nb_reviews':'nb_reviews', 'opr':'overall_player_rating', 'nb_english_reviews':'nb_english_reviews'}


app = flask.Flask(__name__)
app.config["DEBUG"] = True

 
def getNextGameId():
    ''' Return the next game_id available '''
    query = ("SELECT game_id FROM games;")
    cursor.execute(query)
    ids = cursor.fetchall()
    arr = np.array([item['game_id'] for item in ids])
    return np.max(arr).item(0)

nextGameId = getNextGameId()


def dictOPR():
    ''' Return the dictionary for overall_player_rating '''
    ''' 'other': 0, 'very positive': 1, 'overwhelmingly positive': 2, ... }'''
    query = ("SELECT overall_player_rating_id, overall_player_rating FROM overall_player_ratings;")
    cursor.execute(query)
    res = cursor.fetchall()
    return {item['overall_player_rating'].lower():item['overall_player_rating_id'] for item in res}

dict_opr = dictOPR()


@app.route('/', methods = ['GET'])
def welcome():
    return render_template('welcome.html')

 
@app.route('/api/v1/resources/games/all', methods=['GET'])
def test():
    # version with mysql.connector
    query = ("SELECT game_name FROM games;")
    cursor.execute(query)
    result = cursor.fetchall()
    df_games = pd.DataFrame(result)
    df_games = df_games.to_dict()
    # version SQLAlchemy pd.read_sql
    #query = text("SELECT game_name FROM games")
    #df_games = pd.read_sql(query, engine)
    #return jsonify(df_games) # DataFrame not JSON serializable
    return df_games.to_json()



# ------------------------------------
#     GET
# ------------------------------------

@app.route('/api/<string:version>/resources/publishers', methods=['GET'])
def api_get_publishers(version:str):
    query = (f"SELECT publisher_name FROM publishers;")
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    for item in result:
        item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?publisher={item['publisher_name']}" 
    if version == 'v1':
        return render_template('publishers.html', result=result)
    return jsonify(result)

@app.route('/api/<string:version>/resources/developers', methods=['GET'])
def api_get_developers(version:str):
    query = (f"SELECT developer_name FROM developers;")
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)
    for item in result:
        item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?developer={item['developer_name']}" 
    if version == 'v1':
        return render_template('developers.html', result=result)
    return jsonify(result)

@app.route('/api/<string:version>/resources/<string:table_name>', methods=['GET'])
def api_get(table_name:str, version:str):
    print('-------------------- api_get_game ---------------------')
    if not(version in ['v1', 'v2']):
        return {'0':'URL NOT VALID'}

    if table_name in ['publishers', 'developers', 'tags', 'genres']:
        name = table_name[:-1]
        if table_name in ['publishers', 'developers']:
            name += "_name"
        query = (f"SELECT {name} FROM {table_name};")
        cursor.execute(query)
        result = cursor.fetchall()
        print(result)
        if version == 'v1':
            return render_template('tables.html', table_name=table_name, name=name, result=result)
        return jsonify(result)

    elif table_name == 'games':
        if 'id' in request.args:

            id = int(request.args.get('id'))
            query = (f"SELECT g.game_name, g.release_date, g.nb_reviews, opr.overall_player_rating, g.nb_english_reviews \
                     FROM games AS g \
                     JOIN overall_player_ratings AS opr ON opr.overall_player_rating_id = g.overall_player_rating_id \
                     WHERE g.game_id = {id};")
            cursor.execute(query)
            game = cursor.fetchall()

            publishers, developers, tags = [], [], []
            if 'publishers' in request.args and request.args.get('publishers').lower() == 'true':
                query = (f"SELECT p.publisher_name FROM publishers AS p \
                            JOIN publi_game AS pg ON pg.publisher_id = p.publisher_id \
                            JOIN games AS g ON g.game_id = pg.game_id \
                            WHERE g.game_id = {id};")
                cursor.execute(query)
                publishers = cursor.fetchall()
                for item in publishers:
                    item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?publisher={item['publisher_name']}" 

            if 'developers' in request.args and request.args.get('developers').lower() == 'true':
                query = (f"SELECT d.developer_name FROM developers AS d \
                            JOIN dev_game AS dg ON dg.developer_id = d.developer_id \
                            JOIN games AS g ON g.game_id = dg.game_id \
                            WHERE g.game_id = {id};")
                cursor.execute(query)
                developers = cursor.fetchall()
                for item in developers:
                    item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?developer={item['developer_name']}" 

            if 'tags' in request.args and request.args.get('tags').lower() == 'true':
                query = (f"SELECT t.tag AS tag FROM tags AS t \
                            JOIN tag_game AS tg ON tg.tag_id = t.tag_id \
                            JOIN games AS g ON g.game_id = tg.game_id \
                            WHERE g.game_id = {id};")
                cursor.execute(query)
                tags = cursor.fetchall()
                for item in tags:
                    item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?tag={item['tag']}"

            if version == 'v1':
                return render_template('game.html', game=game, publishers = publishers, \
                                    developers = developers, tags = tags)
            return jsonify(game)

        pivot_dev, pivot_publi, pivot_tag = False, False, False
        wheres = ''
        if 'name_starting' in request.args:
            wheres += f''' g.game_name LIKE '{request.args.get("name_starting")}%' '''
        if 'name_like' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' g.game_name LIKE '%{request.args.get("name_like")}%' '''
        if 'year' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f' YEAR(g.release_date) = {int(request.args.get('year'))}'
        if 'nb_reviews' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f' g.nb_reviews > {int(request.args.get('nb_reviews'))}'
        if 'opr_like' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' opr.overall_player_rating LIKE '%{request.args.get("opr_like")}%' '''
        if 'opr' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' opr.overall_player_rating = '{request.args.get("opr")}' '''
        if 'nb_english_reviews' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f' g.nb_english_reviews > {int(request.args.get('nb_english_reviews'))}'
        if 'publishers' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' p.publisher_name LIKE '%{request.args.get("publishers")}%' '''
            pivot_publi = True
        if 'publisher' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' p.publisher_name LIKE '%{request.args.get("publisher")}%' '''
            pivot_publi = True
        if 'developers' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' d.developer_name LIKE '%{request.args.get("developers")}%' '''
            pivot_dev = True
        if 'developer' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' d.developer_name LIKE '%{request.args.get("developer")}%' '''
            pivot_dev = True                         
        if 'tags' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' t.tag LIKE '%{request.args.get("tags")}%' '''
            pivot_tag = True
        if 'tag' in request.args:
            if wheres:
                wheres += ' AND'
            wheres += f''' t.tag LIKE '%{request.args.get("tag")}%' '''
            pivot_tag = True
        
        query = "SELECT DISTINCT g.game_id, g.game_name, g.release_date, g.nb_reviews, opr.overall_player_rating, g.nb_english_reviews \
                 FROM games AS g \
                 JOIN overall_player_ratings AS opr ON opr.overall_player_rating_id = g.overall_player_rating_id"
        
        # SQL Join
        if pivot_publi:
            query += " JOIN publi_game AS pg ON pg.game_id = g.game_id \
                JOIN publishers AS p ON p.publisher_id = pg.publisher_id"
        if pivot_dev:
            query += " JOIN dev_game AS dg ON dg.game_id = g.game_id \
                JOIN developers AS d ON d.developer_id = dg.developer_id"
        if pivot_tag:
            query += " JOIN tag_game AS tg ON tg.game_id = g.game_id \
                JOIN tags AS t ON t.tag_id = tg.tag_id"
        if wheres:
            query += ' WHERE ' + wheres
        if 'order' in request.args:
            if request.args.get("order") in ['name', 'date', 'nb_reviews', 'opr', 'nb_english_reviews']:
                order_by = dict_order[request.args.get("order")]
                query += f' ORDER BY {order_by}'
            if 'desc' in request.args:
                if request.args.get('desc').lower() == "true":
                    query += ' DESC'

        #print(query)
        cursor.execute(query)
        result = cursor.fetchall()
        #print(result)
        for item in result:
            item['link'] = f"http://127.0.0.1:5000/api/v1/resources/games?id={item['game_id']}&publishers=true&developers=true&tags=true" 
        print(result)
        column_names = ['id', 'name',  'release_date', 'reviews', 'rating', 'reviews EN', 'link']
        if version == 'v1':
            return render_template('games.html', name=table_name, result=result, column_names=column_names)
        return jsonify(result)
    
    return render_template('welcome.html')


# ------------------------------------
#     CREATE
# ------------------------------------

@app.route('/api/v2/resources/games', methods=['POST'])
def api_post_game():
    global nextGameId
    print('-------------------- api_post_game ---------------------')

    game_name, release_date, nb_reviews, overall_player_rating_id, nb_english_reviews = '', '2024-01-01', 0, 0, 0

    if 'name' in request.args:
        game_name = request.args.get('name')
    elif 'game_name' in request.args:
        game_name = request.args.get('game_name')
    else:
        return {'0':'Il faut un nom de jeu !'}

    nextGameId += 1
    game_id = nextGameId

    if 'release_date' in request.args:
        release_date = request.args.get('release_date')
    elif 'date' in request.args:
        release_date = request.args.get('date')
    
    if 'nb_reviews' in request.args:
        nb_reviews = int(request.args.get('nb_reviews'))

    if 'opr' in request.args:
        overall_player_rating_id = dict_opr.get(request.args.get('opr').lower(), 0)

    if 'nb_english_reviews' in request.args:
        nb_english_reviews = int(request.args.get('nb_english_reviews'))

    info_id = game_id + 1001

    # Creating info
    query = (f"INSERT INTO infos(info_id, short_description, long_description, link) VALUES (%s, %s, %s, %s);")
    val = (info_id, 'Un super nouveau jeu', '... en attente ...', 'lien à venir')
    cursor.execute(query, val)
    # result = cursor.fetchall()
    # print(result)
    
    # Creating info
    query = (f"INSERT INTO games(game_id, game_name, release_date, nb_reviews, overall_player_rating_id, \
             nb_english_reviews, info_id) VALUES (%s, %s, %s, %s, %s, %s, %s);")
    val = (game_id, game_name, release_date, nb_reviews, overall_player_rating_id, nb_english_reviews, info_id)
    cursor.execute(query, val)
    cnx.commit()
    return {'Succès': f'Le jeu {game_name} a été créé'}


# ------------------------------------
#     DELETE
# ------------------------------------

@app.route('/api/v2/resources/games', methods=['DELETE'])
def api_delete_game():
    print('-------------------- api_delete_game ---------------------')

    if not('name' in request.args) and not('game_name' in request.args) and not('id' in request.args) \
       and not('name_starting' in request.args) and not('name_like' in request.args):
        return {'Erreur':"Il faut un id ou un nom de jeu dans l'URL ou bien un morceau de nom"}

    game_name, game_id, query, val = '', -1, '', None

    if 'id' in request.args:
        assert type(request.args.get('id') == int)
        game_id = int(request.args.get('id'))
        if game_id < 0:
            return {'Erreur': f'ID {request.args.get('id')} incorrect'}
        query = (f"SELECT COUNT(*) AS counter FROM games WHERE game_id = {game_id};")
        cursor.execute(query, val)
        res = cursor.fetchall()
        if len(res) != 1:
            return {'Erreur': f'ID {request.args.get('id')} n"existe pas'}
        
        query = (f"SELECT game_name FROM games WHERE game_id = {game_id};")
        cursor.execute(query)
        res = cursor.fetchall()
        assert(len(res) == 1)
        game_name = res[0]['game_name']
        print("Game_name: ", game_name)

    elif ('name' in request.args) or ('game_name' in request.args):
        if 'name' in request.args:
            game_name = request.args.get('name')
        elif 'game_name' in request.args.get('game_name'):
            game_name = request.args.get('game_name')
        else:
            assert(False)

        if not(game_name):
            return {'Erreur':'Nom incorrect dans l"URL'}
        print(game_name)
        
        # Get the game_id
        query = (f"SELECT game_id FROM games WHERE game_name = '{game_name}';")
        cursor.execute(query)
        res = cursor.fetchall()
        if len(res) < 1:
            return {'Erreur': f"Nom {game_name} n'existe pas"}
        elif len(res) > 1:
            assert(False) # Plusieurs fois le même id !!! Impossible (PK)
        print("Game_id: ", res[0]['game_id'])
        game_id = res[0]['game_id']

    elif ('name_starting' in request.args) or ('name_like' in request.args):
        game_ids = [] 
        if 'name_starting' in request.args:
            name_starting = request.args.get('name_starting')
            #print('name_starting', name_starting)
            query = (f"SELECT game_id FROM games WHERE game_name LIKE '{name_starting}%';")
            cursor.execute(query)
            res = cursor.fetchall()
            #print(res)
            game_ids = [item['game_id'] for item in res]
        
        elif 'name_like' in request.args:
            name_like = request.args.get('name_like')
            query = (f"SELECT game_id FROM games WHERE game_name LIKE '%{name_like}%';")
            cursor.execute(query)
            res = cursor.fetchall()
            game_ids = [item['game_id'] for item in res]

        print(game_ids)

        if len(game_ids):
            for id in game_ids:
                # Deleting game
                query = (f"DELETE FROM games WHERE game_id = {id};")
                cursor.execute(query)
                # Deleting info
                info_id = id + 1001
                query = (f"DELETE FROM infos WHERE info_id = {info_id};")
                cursor.execute(query)
            cnx.commit()

            if len(game_ids) > 1:
                return {'Succès' : f'Suppresion de {len(game_ids)} jeux'}
            return {'Succès' : f'Suppresion d"un jeu'}

        else:
            return {'Aucun jeu à supprimer': '!!!'}

    # Deleting game
    query = (f"DELETE FROM games WHERE game_id = {game_id};")
    cursor.execute(query)
    
    # Deleting info
    info_id = game_id + 1001
    query = (f"DELETE FROM infos WHERE info_id = {info_id};")
    cursor.execute(query)
    # result = cursor.fetchall()
    # print(result)    
    #print(cursor.rowcount, "record(s) deleted")
    cnx.commit()

    return {'Succès' : f'Suppresion du jeu : {game_name}'}


# ------------------------------------
#     UPDATE
# ------------------------------------

@app.route('/api/v2/resources/games', methods=['PUT'])
def api_put_game():
    print('-------------------- api_put_game ---------------------')

    if not('game_name' in request.args) and not('game_id' in request.args) and \
       not('id' in request.args):
        return {'Erreur' : "Il faut un nom ou un Id de jeu dans l'URL"}

    game_id, game_name = -1, ''
    if 'id' in request.args:
        game_id = request.args.get('id')
        query = f"SELECT COUNT(*) AS counter FROM games WHERE game_id = {game_id}"
        cursor.execute(query)
        res = cursor.fetchall()
        if len(res) == 0:
            return {'Erreur' : f"Pas de jeu avec l'id {game_id}"}
        elif len(res) > 1:
            assert(False) # Impossible (PK)
        query = f"SELECT game_name FROM games WHERE game_id = {game_id}"
        cursor.execute(query)
        res = cursor.fetchall()
        game_name = res[0]['game_name']
        
    else:
        print(request.args)
        if 'name' in request.args:
            game_name = request.args.get('name')
        elif 'game_name' in request.args:
            game_name = request.args.get('game_name')
        if not(game_name):
            return {'Erreur' : 'Le nom du jeu est vide'}
        query = f"SELECT game_id FROM games WHERE game_name = '{game_name}' "
        cursor.execute(query)
        res = cursor.fetchall()
        if len(res) > 1:
            return {'Erreur' : f"Plusieurs jeux avec le nom {game_name}"}
        elif len(res) == 0:
            return {'Erreur' : f"Pas de jeu au nom {game_name}"}
        game_id = res[0]['game_id']

    print(game_name, game_id)

    # Modifying game
    query = "UPDATE games SET "
    requestArg = False
    if 'modified_name' in request.args:
        new_name = request.args.get('modified_name')
        query += f"game_name = '{new_name}', "
        requestArg = True
    if 'modified_date' in request.args:
        release_date = request.args.get('modified_date')
        query += f"release_date = '{release_date}', "
        requestArg = True
    if 'modified_nb_reviews' in request.args:
        query += f"nb_reviews = {request.args.get('modified_nb_reviews')}, "
        requestArg = True
    if 'modified_nb_english_reviews' in request.args:
        query += f"nb_english_reviews = {request.args.get('modified_nb_english_reviews')}, "
        requestArg = True
    if 'modified_opr' in request.args:
        new_opr_id = dict_opr.get(request.args.get('modified_opr').lower(), -1)
        if new_opr_id > -1:
            query += f"overall_player_rating_id = {new_opr_id}, "
            requestArg = True
        else:
            print("mauvais argument modified_opr")
    elif 'modified_overall_player_rating' in request.args:
        new_opr_id = dict_opr.get(request.args.get('modified_overall_player_rating').lower(), -1)
        if new_opr_id > -1:
            query += f"overall_player_rating_id = {new_opr_id}, "
            requestArg = True
        else:
            print("mauvais argument modified_overall_player_rating")
    if not(requestArg):
        return {'Erreur' : "Mauvais argument dans l'URL"}
    query = query[:-2] + f" WHERE game_id = {game_id};"
    print(query)
    cursor.execute(query)
    cnx.commit()
    return jsonify({'Succès':f'Modificatin du jeu {game_name}'})



# Run flask
app.run()

# if request.method == 'POST':