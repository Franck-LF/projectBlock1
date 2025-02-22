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



# import numpy as np
# import pandas as pd
from datetime import datetime
from collections import namedtuple

# Import scrapping functions
from scrapping import scrap_new_release, Options_Scrapping

# Import request API functions
from requestOMDB import request_plot_and_thumbnail



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

    # Scrap new releases of the week
    options_scrapping = Options_Scrapping(
                                    use_Selenium, driver, nb_minimum_critics,
                                    nb_consecutives_unpopular_movies_to_break,
                                    nb_maximum_movies_per_year)
    
    df_movies = scrap_new_release(options_scrapping)
    assert all(column in df_movies.columns for column in ['title', 'original_title', 'url_thumbnail'])

    # Save the dataframe in csv file
    df_movies.to_csv(f'csv/movies_{year}_{month}_{day}.csv', sep=',', index = False)

    # Request API to get more informations
    df_movies_wiht_plot_and_thumbnail = request_plot_and_thumbnail(df_movies[['title', 'original_title', 'url_thumbnail']])

    # Insert scrapped informations into MySQL Database

    # Insert Requested infos from OMDB into MongoDB Database

    now = datetime.now()
    print(f"Finished at: {now.strftime("%H:%M:%S")}")
    print("-------------------- End --------------------")