# -----------------------------------------------------
#
#  Functions to manage Data bases (MySQL & MongoDB)
#
#  Most functions are to insert data.
#
#
# -----------------------------------------------------



import uuid
import numpy as np
import pandas as pd
# from unidecode import unidecode
from collections import namedtuple

# MySQL
import mysql.connector

# MongoDB
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi






months_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
months_EN = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']


# --------------------------------------------------------- #
#                                                           #
#   Named Tuple defining the structures of the SQL tables   #
#                                                           #
# --------------------------------------------------------- #

Table = namedtuple('Table', (['Table_name', 'Field_id', 'Field']))
tup_categories = Table('categories', 'category_id', 'category')
tup_countries  = Table('countries', 'country_id', 'country')
tup_directors  = Table('directors', 'director_id', 'director_name')
tup_composers  = Table('composers', 'composer_id', 'composer_name')
tup_actors     = Table('actors', 'actor_id', 'actor_name')


# ---------------------------------------------------- #
#                                                      #
#   Functions to format data before insering into DB   #
#                                                      #
# ---------------------------------------------------- #

def generate_ID():
    ''' Generate an ID '''
    return str(uuid.uuid4())

def string_with_comma_to_list_of_strings(st):
    ''' Convert a string such as "['string1', 'string2' ...]" into
        a list of string ['string1', 'string2', ...]

        Return: A list of strings.

        Arg:
         - st: string with the value to split.
    '''
    if pd.isna(st):
        return []
    return [item.strip() for item in st.split(",") if len(item.strip()) > 1]

def duration_to_minutes(st):
    ''' Convert duration string into number of minutes (integer)
        1h 35min   ---->    95

        Return: Integer representing the number of minutes.
        Arg:
         - st: duration string to convert.
    '''
    if pd.isna(st) or st == '': return 0
    if 'h' in st:
        a, b = st.split('h')
        if 'min' in b:
            b = b.replace('min', '')
            return 60 * int(a) + int(b.strip())
        return 60 * int(a)
    assert 'min' in st
    st = st.replace('min', '')
    return 60 * int(st)            

def unique_values_of_columns(df_data, column):
    ''' return a list with unique values found in the column,
        values in the column are like : 'value1,value2,value3' ..... 
        so we split all values in each row of the column and stack them in a list.

        Return : A list of values.

        Args:
         - df_data: dataframe with the data to extract,
         - column: string with the name of the column we want to work with.     
    '''
    df = df_data[column]
    df.dropna(inplace = True)
    df = df.apply(string_with_comma_to_list_of_strings)
    df = df.apply(pd.Series).stack().reset_index(drop=True)
    return df.unique()

def convert_months_FR_to_EN(st):
    ''' Convert french months to english months

        Return: string with a month in english.

        Arg:
         - st: string with a french date.
    '''
    if pd.isna(st): return ''
    for month_FR, month_EN in zip(months_FR, months_EN):
        if month_FR in st:
            return st.replace(month_FR, month_EN)
    print('ERROR', st)
    return st

def format_data(df, tuple_dict):
    '''
       Converting some columns of "df" into the appropriate format:
        - correct date format,
        - duration un minutes,
        - convert categories / countries into their IDs in the DB,
        - convert directors / actors / composers into their IDs in the DB.

        Return dataframe with formatted data.

        Args:
         - df Pandas Dataframe to be formatted,
         - tuple_dict: tuple with the 5 dictionnaries corresponding to the 5 tables:
                       categories, countries, directors, actors, composers.
    '''

    assert 'categories' in df.columns and 'countries' in df.columns and 'directors' in df.columns \
       and 'actors' in df.columns and 'composers' in df.columns and 'duration' in df.columns \
       and 'date' in df.columns and 'reviews' in df.columns and 'star_rating' in df.columns

    (dict_category_id, dict_country_id, dict_director_id, dict_actor_id, dict_composer_id) = tuple_dict

    df_formated = df.copy()
    df_formated['categories'] = df_formated['categories'].apply(string_with_comma_to_list_of_strings)
    df_formated['categories'] = df_formated['categories'].apply(lambda lst : list(set([dict_category_id[k] for k in lst])))

    df_formated['countries'] = df_formated['countries'].apply(string_with_comma_to_list_of_strings)
    df_formated['countries'] = df_formated['countries'].apply(lambda lst : list(set([dict_country_id[k] for k in lst])))

    df_formated['directors'] = df_formated['directors'].apply(string_with_comma_to_list_of_strings)
    df_formated['directors'] = df_formated['directors'].apply(lambda lst : list(set([dict_director_id[k] for k in lst])))

    df_formated['actors'] = df_formated['actors'].apply(string_with_comma_to_list_of_strings)
    df_formated['actors'] = df_formated['actors'].apply(lambda lst : list(set([dict_actor_id[k] for k in lst])))

    df_formated['composers'] = df_formated['composers'].apply(string_with_comma_to_list_of_strings)
    df_formated['composers'] = df_formated['composers'].apply(lambda lst : list(set([dict_composer_id[k] for k in lst])))

    df_formated['duration'] = df_formated['duration'].apply(duration_to_minutes)

    df_formated['date'] = df_formated['date'].apply(convert_months_FR_to_EN)
    df_formated['date'] = pd.to_datetime(df_formated['date'], format='mixed')

    df_formated['notes'] = df_formated['notes'].apply(int)
    df_formated['reviews'] = df_formated['reviews'].astype(int)
    df_formated['star_rating'] = df_formated['star_rating'].apply(lambda x : float(x.replace(',', '.')))

    return df_formated




# ------------------------------------- #
#                                       #
#   Functions to fill in MySQL tables   #
#                                       #
# ------------------------------------- #

def fill_in_table(lst, table_name, field_id, field, connector, cursor):
    ''' Fill in an SQL table from a list of values.
        For each value in the list 'lst' we generate an ID and insert into the table (ID, value).

        CAREFUL: To run only once for each table, otherwise : "ERROR Duplicate entry '0' for key 'table_name.PRIMARY'"

        Return: A dictionary mapping each value of the list to an ID newly generated {value1 : ID1, value2 : ID2, ...}

        Args:
         - lst: list of values to insert into the table,
         - table_name: string with the name of the table,
         - field_id: string with the ID of the value record inserted in the table,
         - field: string of the field in the table,
         - connector: MySQL connector connected to the relevant database,
         - cursor: MySQL cursor to execute SQL statements.
    '''
    assert False
    dic_return = {}
    for item in lst:
        dic_return[item] = generate_ID()
        query = f"INSERT INTO {table_name} ({field_id}, {field}) VALUES (%s, %s)"
        val = (dic_return[item], item)
        cursor.execute(query, val)
    connector.commit()
    return dic_return

def fill_in_categorial_table_with_new_values(tup_table, arr_values, connector, cursor):
    ''' Insert values into a database table,
        First we have to check that the value is not already in the table.

       Return: dictionary {value : id} with the whole table.
       Args:
        - tup_table (Table): named_tuple with all infos about table fields,
        - arr_values (np.array): array with all of values to insert into the table,
        - connector: MySQL connector connected to the relevant database,
        - cursor: MySQL cursor to execute SQL statements.
    '''

    # Query to get list of values already in the tabme
    query = (f"SELECT {tup_table.Field}, {tup_table.Field_id} FROM {tup_table.Table_name};")
    cursor.execute(query)
    result = cursor.fetchall()
    dic = dict(np.array(result))

    # Compute the difference between two sets to get
    arr_diff = np.setdiff1d(arr_values, list(dic.keys()), assume_unique = True)

    # Fill in the table with new values
    for item in arr_diff:
        dic[item] = generate_ID()
        query = f"INSERT INTO {tup_table.Table_name} ({tup_table.Field_id}, {tup_table.Field}) VALUES (%s, %s)"
        val = (dic[item], item)
        cursor.execute(query, val)

    # Validate all SQL operations
    connector.commit()
    return dic

def fill_in_pivot_table(table_name, field, lst_values, movie_id, cursor):
    ''' Fill in pivot table with couple value such (item, movie_id)
        where item is a value of lst_values.

        Args:
         - table_name: string with name of the pivot_table to fill in,
         - field: string with the name of the field (category_id, actor_id ...),
         - lst_values: list of values of the field,
         - movie_id: id of the movie to be connected,
         - cursor: MySQL cursor to execute SQL statements.
    '''
    for item in lst_values:
        query = f"INSERT INTO {table_name} ({field}, movie_id) VALUES (%s, %s)"
        val = (item, movie_id)
        cursor.execute(query, val)
    # No commit at this point

def fill_in_categorial_tables(df_movies, connector, cursor):
    ''' Fill in the 5 categorial tables:
            categories, countries, directors, actors, composers.

        Return: 5 dictionaries for the 5 tables, 
                each dictionary containing pairs {value : id}

        Arg:
         - df_movies (Pandas Dataframe): containing all movies infos,
         - connector: MySQL connector connected to the relevant database,
         - cursor: MySQL cursor to execute SQL statements.
    '''
    # Fill in categories table
    arr_categories = np.array(unique_values_of_columns(df_movies, 'categories'))
    dict_category_id = fill_in_categorial_table_with_new_values(tup_categories, arr_categories, connector, cursor)

    # Fill in countries table
    arr_countries = np.array(unique_values_of_columns(df_movies, 'countries'))
    dict_country_id = fill_in_categorial_table_with_new_values(tup_countries, arr_countries, connector, cursor)

    # Fill in directors table
    arr_directors = np.array(unique_values_of_columns(df_movies, 'directors'))
    dict_director_id = fill_in_categorial_table_with_new_values(tup_directors, arr_directors, connector, cursor)

    # Fill in actors table
    arr_actors = np.array(unique_values_of_columns(df_movies, 'actors'))
    dict_actor_id = fill_in_categorial_table_with_new_values(tup_actors, arr_actors, connector, cursor)

    # Fill in composers table
    arr_composers = np.array(unique_values_of_columns(df_movies, 'composers'))
    dict_composer_id = fill_in_categorial_table_with_new_values(tup_composers, arr_composers, connector, cursor)

    return (dict_category_id, dict_country_id, dict_director_id, dict_actor_id, dict_composer_id)

def fill_in_movie_table(df_movies_formatted, connector, cursor):
    '''
       Fill in the 'movies' tables and all related tables (infos + 5 pivot tables)
       
       Args:
        - df_movies_formatted: Pandas dataframed with formatted data,
        - connector: MySQL connector connected to the relevant database,
        - cursor: MySQL cursor to execute SQL statements.
    '''
    
    for movie in df_movies_formatted.itertuples():

        # ----------- #
        #    infos    #
        # ----------- #

        info_id = generate_ID()
        sql = "INSERT INTO infos (info_id, summary, url_thumbnail) VALUES (%s, %s, %s)"
        val = (info_id, 
               movie[13],  # summary 
               movie[14])  # url_thumbnail
        
        if pd.isna(movie[13]) or pd.isna(movie[14]):
            print(movie)
            
        cursor.execute(sql, val)

        # ----------- #
        #    movies   #
        # ----------- #

        movie_id = generate_ID()

        sql = "INSERT INTO movies (movie_id, title, original_title, release_date, duration, nb_notes, \
                                   nb_reviews, info_id, star_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (movie_id, 
               movie[1], # title
               movie[2], # original_title
               movie[3], # release_date
               movie[4], # duration
               movie[8], # nb_notes
               movie[9], # nb_reviews
               info_id,  
               movie[7]) # star_rating
        if pd.isna(movie[1]) or pd.isna(movie[2]) or pd.isna(movie[3]) or pd.isna(movie[4]) or pd.isna(movie[8]) or pd.isna(movie[9]) or pd.isna(movie[7]):
            print(movie)

        cursor.execute(sql, val)

        # -------------------- #
        #     Pivot tables     #   
        # -------------------- #
        #    category_movie    #
        #    country_movie     #
        #    director_movie    #
        #    actor_movie       #
        #    composer_movie    #
        # -------------------- #

        # Fill in pivot table: category_movie
        lst_categories = movie[5]
        fill_in_pivot_table('category_movie', 'category_id', lst_categories, movie_id, cursor)

        # Fill in pivot table: country_movie
        lst_countries = movie[6]
        fill_in_pivot_table('country_movie', 'country_id', lst_countries, movie_id, cursor)

        # Fill in pivot table: director_movie
        lst_directors = movie[10]
        fill_in_pivot_table('director_movie', 'director_id', lst_directors, movie_id, cursor)

        # Fill in pivot table: actor_movie
        lst_actors = movie[11]
        fill_in_pivot_table('actor_movie', 'actor_id', lst_actors, movie_id, cursor)

        # Fill in pivot table: composer_movie
        lst_composers = movie[12]
        fill_in_pivot_table('composer_movie', 'composer_id', lst_composers, movie_id, cursor)
        
        connector.commit()

def fill_in_db_from_csv(csv_files, connector, cursor):
    ''' Fill in the database from csv files

        Args:
         - csv_files: list of csv files containing all movie informations,
         - connector: MySQL connector connected to the relevant database,
         - cursor: MySQL cursor to execute SQL statements.
    '''

    for file_name in csv_files:
        df_movies = pd.read_csv(file_name, delimiter = ',')
        
        tup_dict = fill_in_categorial_tables(df_movies, connector, cursor)
        
        df_formatted = format_data(df_movies, tup_dict)
        fill_in_movie_table(df_formatted, connector, cursor)

def fill_in_mysql_db_from_dataframe(df_movies):
    ''' Fill in the database from csv files

        Args: df_movies Pandas Dataframe containing all movie informations
    '''
    
    connector = mysql.connector.connect(user='root', password='admin', \
                              host = '127.0.0.1', database='movies')
    cursor = connector.cursor(buffered=True)

    tup_dict = fill_in_categorial_tables(df_movies, connector, cursor)
    df_formatted = format_data(df_movies, tup_dict)
    fill_in_movie_table(df_formatted, connector, cursor)

    connector.disconnect()








# -------------------------------- #
#                                  #
#   Functions to fill in MongoDB   #
#                                  #
# -------------------------------- #


def test(df_movies):

    assert True
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Select database "allocine" (or creates if does not exist)
    mydb = client["allocine"]

    # Retrieve the collection "movies" (or creates it if does not exist)
    col_movies = mydb["movies"]
    # col_movies.drop()

    # Insertion of movie plots in MongoDB database
    col_movies.insert_many(df_movies.to_dict(orient='records')) # TO DO ONLY ONCE

    print(f"Insertion of {df_movies.shape[0]} documents in collection 'movies'")
    print("Nb total documents in base:", col_movies.count_documents({}))

    # Store data in csv file
    # lst = list(col_movies.find())
    # df_mongo = pd.DataFrame(lst, columns = ['_id', 'title', 'original_title', 'plot', 'url_thumbnail'])
    # print(df_mongo.shape[0])
    # df_mongo.to_csv('csv/mongoDB_1960_to_2025.csv', sep=',', index = False)