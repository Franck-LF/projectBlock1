# -----------------------------------------------------
# 
#           Main Script 
# 
#   Automatically and periodically launched to:
#   - scrap
#   - request OMDB API
#   - Insert All Data in data bases (MySQL and MongoDb)
# 
# -----------------------------------------------------



from datetime import datetime

# Import scrapping functions
from scrapping import scrap_new_release, Options_Scrapping

# Import request API functions
from requestOMDB import request_to_OMDB

# Import databases functions
from database import fill_in_mysql_db_from_dataframe
from database import fill_in_mongo_db_from_dataframe





if __name__ == '__main__':

    print("--------------- Start scrapping new release ---------------")

    now = datetime.now()
    year, month, day, hour, min, sec = now.strftime("%d-%m-%Y-%H-%M-%S").split('-')
    print(f"Date: {year}/{month}/{day}")
    print(f"Start at: {hour}:{min}:{sec}\n")

    use_Selenium = False
    driver = None
    nb_minimum_critics = 0
    nb_consecutives_unpopular_movies_to_break = 20
    nb_maximum_movies_per_year = 250
    options_scrapping = Options_Scrapping(
                                    use_Selenium, driver, nb_minimum_critics,
                                    nb_consecutives_unpopular_movies_to_break,
                                    nb_maximum_movies_per_year)

    # -------------- #
    #   Scrapping    #
    # -------------- #    
    df_movies = scrap_new_release(options_scrapping, url = 'https://www.allocine.fr/film/agenda/sem-2025-02-12/')
    
    # -------------------- #
    #   Request API OMDB   #
    # -------------------- #
    df_movies_wiht_plot_and_thumbnail = request_to_OMDB(df_movies[['title', 'original_title', 'summary', 'url_thumbnail']])

    # ----------------------------------- #
    #   Save the dataframe in csv file    #
    # ----------------------------------- #
    # df_movies.to_csv(f'csv/movies_mysql_{year}_{month}_{day}.csv', sep=',', index = False)
    # df_movies_wiht_plot_and_thumbnail.to_csv(f'csv/movies_mongo_{year}_{month}_{day}.csv', sep=',', index = False)

    # -------------------------------------- #
    #   Insert movies infos into Databases   #
    # -------------------------------------- #
    # MySQL
    fill_in_mysql_db_from_dataframe(df_movies)
    # MongoDB
    fill_in_mongo_db_from_dataframe(df_movies_wiht_plot_and_thumbnail)

    now = datetime.now()
    print(f"\nFinished at: {now.strftime("%H:%M:%S")}")
    print("-------------------- End --------------------")