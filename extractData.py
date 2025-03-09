# -----------------------------------------------------
# 
#           Data Extraction Script 
# 
#   Automatically and periodically launched to:
#   - scrap movies infos
#   - request OMDB API
# 
# -----------------------------------------------------

import os
import re
import json
import requests
import numpy as np
import pandas as pd
from collections import namedtuple
from datetime import datetime
from unidecode import unidecode

# Scrapping
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import numpy as np
import pandas as pd
from collections import namedtuple

from dotenv import load_dotenv

# Environnement variables
load_dotenv()

# API KEY from "https://www.omdbapi.com/"
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

pd.options.mode.copy_on_write = True

# One way to set the driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def _options():
    ''' Set Selenium options '''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu') if os.name == 'nt' else None # Windows workaround
    options.add_argument('--verbose')
    return options

url_site         = 'https://www.allocine.fr/'
url_films        = 'https://www.allocine.fr/films/'
url_new_releases = 'https://www.allocine.fr/film/sorties-semaine/'


# -----------------------------------------
#
#   Object to store all scrapping options
#
# -----------------------------------------

Options_Scrapping = namedtuple('Options', (['use_Selenium', 'driver', 'nb_minimum_critics',\
                                            'nb_consecutives_unpopular_movies_to_break',\
                                            'nb_maximum_movies_per_year']))




month_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
month_EN = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']



# -------------------------------------------
#
#   Web scraping functions
#
# -------------------------------------------



def number_pages_per_year(soup_year):
    ''' Return the number of pages for one year'''
    pagination = soup_year.find('div', class_='pagination-item-holder')
    nb_pages = int(pagination.find_all('span')[-1].text)
    return int(nb_pages)

def delete_thumbnails():
    '''Delete all files in thumbnail directory'''
    assert False
    try:
        folder_name = os.getcwd() + '\\thumbnails\\'
        files = os.listdir(folder_name)
        for file in files:
            file_path = os.path.join(folder_name, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

def scrap_categories():
    ''' scrap all categories from 'Allocine.fr' list
        Return a Pandas series with all categories.
    '''
    r = requests.get(url_films, auth=('user', 'pass'))
    if r.status_code != 200:
        print("url_site error")

    soup = BeautifulSoup(r.content, 'html.parser')

    categories = []
    elt_categories = soup.find('div', class_='filter-entity-section')
    for elt in elt_categories.find_all('li'):
        categories.append(elt.a.text)

    return pd.Series(categories)

def scrap_countries():
    ''' scrap all categories from 'Allocine.fr' list
        Return a Pandas series with all categories.

        Rq: As some countries do not appear in the list but are tagged as "country" for some movies
            we won't use this function, instead we fill in the categories_table from the countries found in each movie.
    '''
    r = requests.get(url_films, auth=('user', 'pass'))
    if r.status_code != 200:
        print("url_site error")

    soup = BeautifulSoup(r.content, 'html.parser')
    elt_categories = soup.find('div', class_='filter-entity-section')
    elt_countries = elt_categories.find_next_sibling().find_next_sibling()
    elts_items = elt_countries.find_all('li', class_ = 'filter-entity-item')

    countries = []
    for elt_item in elts_items:
        countries.append(elt_item.find('span').text.strip())

    # 'Botswana' is not in the country list but there is a movie with nationality 'Botswana', so we manually add it to the list.
    #  https://www.allocine.fr/film/fichefilm_gen_cfilm=2577.html

    if not('Botswana' in countries):
        countries.append('Botswana')
    if not('Namibie' in countries):
        countries.append('Namibie')
    if not('Liechtenstein' in countries):
        countries.append('Liechtenstein')
    if not('Monaco' in countries):
        countries.append('Monaco')

    return pd.Series(countries)

def get_year_links(lst_years_to_scrap):
    ''' Scrap the links of years in the left panel of Allocine.fr '''

    if isinstance(lst_years_to_scrap, list):
        assert all([isinstance(item, int) for item in lst_years_to_scrap])
    else:
        assert isinstance(lst_years_to_scrap, int)
        lst_years_to_scrap = [lst_years_to_scrap]

    lst_decades_to_scrap = list(set([10 * (year // 10) for year in lst_years_to_scrap]))
    lst_years_to_scrap = [str(year) for year in lst_years_to_scrap]
    lst_decades_to_scrap = [str(decade) for decade in lst_decades_to_scrap]

    driver = webdriver.Chrome(options = _options())
    driver.get(url_films)
    elts_decades = driver.find_elements(By.XPATH, '/html/body/div[2]/main/section[4]/div[1]/div/div[3]/div[2]/ul/li')

    dict_year_link = {}
    for elt_decade in tqdm(elts_decades):
        elt_a = elt_decade.find_element(By.TAG_NAME, 'a')
        if not(elt_a.get_attribute('title')[:4] in lst_decades_to_scrap):
            continue

        driver2 = webdriver.Chrome(options = options)
        url_decade = elt_a.get_attribute('href').strip()

        driver2.get(url_decade)
        elts_years = driver2.find_elements(By.XPATH, '/html/body/div[2]/main/section[4]/div[1]/div/div[3]/div[3]/ul/li')

        for elt_year in elts_years:
            year = elt_year.find_element(By.TAG_NAME, 'a').get_attribute('title').strip()
            if year in lst_years_to_scrap:
                link = elt_year.find_element(By.TAG_NAME, 'a').get_attribute('href').strip()
                dict_year_link[year] = link
        driver2.close()

    for year, url_year in dict_year_link.items():
        print("year", year, '  ----  link', url_year)

    driver.close()
    return dict_year_link

#
# list_years_to_scrap = list(range(1960, 2025))
# dict_year_link = get_year_links(list_years_to_scrap)
#

def get_title(soup_movie):
    ''' Return the title of the movie '''

    title = soup_movie.find('div', class_ = "titlebar-title titlebar-title-xl").text
    elts = soup_movie.find_all('div', class_ = 'meta-body-item')
    for elt in elts:
        elts_span = elt.find_all('span')
        for elt_span in elts_span:
            if "Titre original" in elt_span.get_text(strip = True):
                return title, elt_span.find_next_sibling().get_text(strip = True)
    return title, title

def get_date_duration_categories(soup_movie):
    ''' Return date, duration and categories (as string) of the movie '''
    elt = soup_movie.find('div', class_="meta-body-item meta-body-info")
    date, duration, categories = '', '', ''
    
    if False: # Not really accurate
        text = elt.get_text(strip=True)
        # print(text)
        if text.count('|') == 1:
            s1, s2 = text.split('|')
            categories = s2.strip()
        elif text.count('|') == 2:
            s1, s2, s3 = text.split('|')
            date = s1[:-8].strip()
            duration = s2.strip()
            categories = s3.strip()
        return date, duration, categories

    text = elt.get_text(strip = True)
    for elt_span in elt.find_all("span"):
        if 'date' in elt_span.get('class'):
            date = elt_span.get_text(strip = True)
            text = text.replace(date, '')

        elif 'meta-release-type' in elt_span.get('class'):
            text = text.replace(elt_span.get_text(strip = True), '')

        elif 'dark-grey-link' in elt_span.get('class'):
            categories += elt_span.get_text(strip = True) + ','
            for item in elt_span.get_text(strip = True).split():
                text = text.replace(item, '')

    text = text.replace('|', '')
    text = text.replace(',', '')

    if categories[-1] == ',':
        categories = categories[:-1]

    if len(text.strip()):
        duration = text.strip()

    return date, duration, categories

def get_country(soup_movie):
    ''' Return country of the movie '''
    elts_section_title = soup_movie.find_all('div', class_ = 'section-title')
    for elt_section_title in elts_section_title:
        elt_h2 = elt_section_title.find('h2')

        if elt_h2 and 'Infos techniques' in elt_h2.text.strip():
            elt_country = elt_section_title.find_next_sibling()
            assert "Nationalité" in elt_country.find("span", class_ = "what light").text.strip()
            elt_span_that = elt_country.find("span", class_ = "that")
            elts_span_country = elt_span_that.find_all("span")
            lst_countries = []
            for elt_span_country in elts_span_country:
                lst_countries.append(elt_span_country.text.strip())
            return ','.join(lst_countries)
    return ''

def get_directors(soup_casting):
    ''' Return list of directors '''
    elt_director_section = soup_casting.find('section', class_='section casting-director')
    if elt_director_section:
        elt_temp = elt_director_section.find_next()
        elts_directors = elt_temp.find_next_sibling().find_all('div', class_ = 'card person-card person-card-col')
        lst_directors = []
        for elt_director in elts_directors:
            if elt_director.find('a'):
                lst_directors.append(elt_director.text.strip())
        return ','.join(lst_directors)
    return ''

def get_actors(soup_casting):
    ''' Return list of actors (maximum 30) '''
    elt_actor_section = soup_casting.find('section', class_ = 'section casting-actor')
    if elt_actor_section:
        elt_temp = elt_actor_section.find_next()

        # scrap main actors (maximum eight actors in the mosaic, see image above)
        elts_actors = elt_temp.find_next_sibling().find_all('div', class_ = 'card person-card person-card-col')
        lst_actors = []
        for elt_actor in elts_actors:
            elt_figure = elt_actor.find("figure")
            if elt_figure:
                elt_span = elt_figure.find('span')
                if elt_span.get('title') and elt_span.get('title').strip():
                    lst_actors.append(elt_span.get('title').strip())

        # scrap list of actors below the mosaic (we scrap maximum of (8 + 22) 30 actors in total)
        elts_actors = elt_actor_section.find_all('div', class_ = 'md-table-row')
        lst_actors.extend([elt_actor.find('a').text for elt_actor in elts_actors[:22] if elt_actor.find('a')])
        return ','.join(lst_actors)
    return ''

def get_composers(soup_casting):
    ''' Scrap the name(s) of the music composer(s) '''
    elts_sections = soup_casting.find_all("div", class_ = "section casting-list-gql")
    for elt_section in elts_sections:
        elt_title = elt_section.find('div', class_ = 'titlebar section-title').find('h2')
        if 'Soundtrack' in elt_title.text:
            lst_composers = []
            elts_composers = elt_section.find_all('div', class_ = 'md-table-row')
            for elt_composer in elts_composers:
                elts_span = elt_composer.find_all('span')
                if len(elts_span) > 1 and 'Compositeur' in elts_span[1].text.strip():
                    lst_composers.append(elts_span[0].text.strip())
            return ','.join(lst_composers)
    return ''

def get_summary(soup_movie):
    elt_synopsis = soup_movie.find('section', class_ = "section ovw ovw-synopsis")
    if elt_synopsis:
        elt_content = elt_synopsis.find('p', class_ = 'bo-p')
        if elt_content:
            return elt_content.text.strip()
    return 'No content'

def get_thumbnail(soup_movie):
    elt = soup_movie.find('figure', class_ = 'thumbnail')
    return elt.span.img['src']

def get_similar_movies(url_similar_movies):
    ''' return list of similar movies '''

    lst_similar_movies = []
    # print('url_similar_movies:', url_similar_movies)

    # get the 'similar movies page' soup
    r = requests.get(url_similar_movies, auth=('user', 'pass'))
    soup_similar_movie = BeautifulSoup(r.content, 'html.parser')
    if r.status_code != 200:
        return lst_similar_movies
    
    elts_section = soup_similar_movie.find_all('ul', class_ = "section")
    if elts_section:
        elts_similar_movies = elts_section[0].find_all('li', class_ = 'mdl')
        if elts_similar_movies:
            for elt_similar_movie in elts_similar_movies:
                elt_title = elt_similar_movie.find('h2', class_ = 'meta-title')
                lst_similar_movies.append(elt_title.find('a').text.strip())

    return lst_similar_movies

def scrap_movie(elt_movie, options_scrapping):
    ''' scrap all movie informations

        Return: All informations about one movie.
        Args:
         - elt_movie: Full html of the movie page,
         - options_scrapping: scrapping options to keep scrapping a movie / a year or not.
    '''
    
    # get the movie soup
    url_movie = url_site + elt_movie.h2.a.get('href')[1:]
    r = requests.get(url_movie, auth=('user', 'pass'))
    soup_movie = BeautifulSoup(r.content, 'html.parser')
    
    # ------------ #
    #    Title     #
    # ------------ #
    title, original_title = get_title(soup_movie)

    # ------------ #
    #    Ratings   #
    # ------------ #
    star_rating, nb_notes, nb_reviews = get_ratings(soup_movie, options_scrapping)
    nb_reviews = convert_to_integer(nb_reviews)
    if nb_reviews < options_scrapping.nb_minimum_critics:
        print("Not enough reviews, Do not scrape the movie:" , title)
        return 'Reviews', None

    # --------------------------------- #
    #   Date, duration and categories   #
    # --------------------------------- #
    date, duration, categories = get_date_duration_categories(soup_movie)

    # We do not scrape 'Documentaries' or movie with only category : Divers
    if categories.strip() in ['Divers', 'Documentaire']:
        print('We do not scrape those category film:', title)
        return 'Category', None

    print('Title:', title)

    # ---------------- #
    #     Countries    #
    # ---------------- #
    countries = get_country(soup_movie)

    # ---------------------------------- #
    #   Directors / Actors / Composers   #
    # ---------------------------------- #
    directors, actors, composers = '', '', ''
    is_casting_section = False
    elts_end_section = soup_movie.find_all('a', class_ = 'end-section-link')

    if elts_end_section:
        for elt_end_section in elts_end_section:

            if 'Casting' in elt_end_section['title']:
                # If there is a link to the casting section
                is_casting_section = True
                link_casting = elt_end_section['href']
                r = requests.get(url_site + link_casting, auth=('user', 'pass'))
                soup_casting = BeautifulSoup(r.content, 'html.parser')

                # Get directors' list
                directors = get_directors(soup_casting)
                # Get actors' list
                actors = get_actors(soup_casting)
                # Composers' list
                composers = get_composers(soup_casting)
                break 

    if not(is_casting_section):
        # No casting section
        # for example animation movies does not have a casting section
        # some movies neither: https://www.allocine.fr/film/fichefilm_gen_cfilm=27635.html

        # Get directors' list
        elt_director = soup_movie.find('div', class_ = "meta-body-item meta-body-direction")
        if elt_director:
            elts_span = elt_director.find_all('span')
            assert len(elts_span) >= 2
            directors =  elts_span[1].get_text().strip()

        # Get actors' list
        elt_actor = soup_movie.find('div', class_ = "meta-body-item meta-body-actor")
        if elt_actor:
            lst_actors = []
            for elt_a in elt_actor.find_all('a'):
                lst_actors.append(elt_a.text.strip())
            actors = ','.join(lst_actors)

    # ------------ #
    #   Summary    #
    # ------------ #
    summary = get_summary(soup_movie)[:180]

    # ------------ #
    #   Thumbnail  #
    # ------------ #
    url_thumbnail = get_thumbnail(soup_movie)
    # save_thumbnail(title, url_thumbnail)
    # It is not memory efficient to store the images so we just store the url toward the image.

    # ------------------- #
    #     url_reviews     #
    # ------------------- #
    url_reviews = url_movie.replace('_gen_cfilm=', '-')[:-5] + '/critiques/spectateurs/'

    # ------------------- #
    #    Similar Movies   #
    # ------------------- #
    url_similar_movies = url_movie.replace('_gen_cfilm=', '-')[:-5] + '/similaire/'
    # soup_similar_movies
    # lst_similar_movies = get_similar_movies(url_similar_movies)
    # print(lst_similar_movies)

    return 'OK', (title, original_title, date, duration, categories, countries, star_rating, \
                  nb_notes, nb_reviews, directors, actors, composers,\
                  summary, url_thumbnail, url_reviews, url_similar_movies)


def get_ratings(soup_movie, options_scrapping):
    ''' Scrap the ratings of the movie.

        Return:
         - stareval:   star rating (0.5 to 5),
         - nb_notes:   number of votes,
         - nb_reviews: number of reviews (written reviews),

        Args:
         - soup_movie:   object BeautifulSoup of the movie,
         - options_scrapping: Scrapping options for example:
                              options_scrapping.useSelenium: boolean to choose if we use Selenium or not
                                        True:  Selenium's method,      (SLOWER)
                                        False: Beautifulsoup's method. (FASTER)
        '''

    star_rating, nb_notes, nb_reviews = '0', '0', '0'

    if options_scrapping.use_Selenium:
        elts_ratings = options_scrapping.driver.find_elements(By.CLASS_NAME, 'rating-item')
        
        for elt_rating in elts_ratings:
            elt = None
            try:
                elt = elt_rating.find_element(By.TAG_NAME, 'a')
                if 'Spectateurs' in elt.text.strip():
                    elt_stareval_note = elt_rating.find_element(By.CLASS_NAME, 'stareval-note')
                    star_rating = elt_stareval_note.text.strip()
                    elt_stareval_review = elt_rating.find_element(By.CLASS_NAME, 'stareval-review')
                    stareval_review = elt_stareval_review.text.strip()
                    if stareval_review.count(',') == 1:
                        nb_notes, nb_reviews = stareval_review.split(',')
                        nb_notes = nb_notes.split()[0]
                        nb_reviews = nb_reviews.split()[0]
                    elif 'note' in stareval_review:
                        nb_notes = stareval_review.split()[0].strip()
                    elif 'critique' in stareval_review:
                        nb_reviews = stareval_review.split()[0].strip()
                    else:
                        assert False

            except:
                print('no tag "a" in elt_rating')

    else: # use beautiful soup
        elts_ratings = soup_movie.find_all('div', class_ = 'rating-item-content')
        
        for elt_rating in elts_ratings:
            if 'Spectateurs' in elt_rating.find("span").text.strip():
                elt_stareval_note = elt_rating.find("span", class_ = "stareval-note")
                star_rating = elt_stareval_note.text.strip()
                elt_stareval_review = elt_rating.find("span", class_ = "stareval-review")
                stareval_review = elt_stareval_review.text.strip()
                if stareval_review.count(',') == 1:
                    nb_notes, nb_reviews = stareval_review.split(',')
                    nb_notes = nb_notes.split()[0]
                    nb_reviews = nb_reviews.split()[0]
                elif 'note' in stareval_review:
                    nb_notes = stareval_review.split()[0].strip()
                elif 'critique' in stareval_review:
                    nb_reviews = stareval_review.split()[0].strip()
                else:
                    assert False

    return star_rating, nb_notes, nb_reviews

def convert_to_integer(st):
    ''' Convert the string str_nb_reviews into integer '''
    if not(st):
        return 0
    test = re.search('\\d+', st)
    return int(test.string)

def extract_digits(st):
    if not(st):
        return '0'
    test = re.search('\\d+', st)
    return test.string

def scrap_years(dict_year_link, options_scrapping):
    ''' Scrap the movies of the years listed in the provided dictionary

        Return: Pandas Dataframe with all informations about scrapped movies.

        Args:
         - dict_year_link: dictionary with list of years to scrap,
         - Options_Scrapping: options to stop scraping a year or to scrap or not a movie.
    '''

    if options_scrapping.use_Selenium:
        options_scrapping.driver = webdriver.Chrome(options = _options())

    counter_movies                          = 0
    counter_scraped_movies                  = 0
    counter_not_scraped_not_enough_reviews  = 0
    counter_not_scraped_categories          = 0
    movies = []

    for year, url_year in dict_year_link.items():
        
        r = requests.get(url_year, auth=('user', 'pass'))
        if r.status_code != 200:
            print("url_site error")

        soup_year = BeautifulSoup(r.content, 'html.parser')
        nb_pages = number_pages_per_year(soup_year)
        consecutive_number_of_unpopular_movies  = 0
        counter_movies_per_year                 = 0

        for i in range(nb_pages):
            url_year_page = url_year + f'?page={i+1}'
            r = requests.get(url_year_page, auth=('user', 'pass'))
            if r.status_code != 200:
                print("url_site error")

            print(f"***  Year {year}  ---  Page {i+1}  ***")
            soup_movies = BeautifulSoup(r.content, 'html.parser')
            elt_movies = soup_movies.find_all('li', class_='mdl')

            for elt_movie in elt_movies:
                # print('---------------------------------------------------------------- ')
                status, movie = scrap_movie(elt_movie, options_scrapping)
                counter_movies += 1
                
                if status == 'Reviews':
                    counter_not_scraped_not_enough_reviews += 1
                    consecutive_number_of_unpopular_movies += 1
                    if consecutive_number_of_unpopular_movies == options_scrapping.nb_consecutives_unpopular_movies_to_break:
                        # Reached the number of consecutives "unpopular" movies so we stop scrapping this year.
                        print(f"Reached {options_scrapping.nb_consecutives_unpopular_movies_to_break} consecutives 'unpopular' movies: BREAK")
                        break

                else:
                    consecutive_number_of_unpopular_movies = 0 # Reset the number of unpopular movies

                    if status == 'OK':
                        movies.append(movie)
                        counter_scraped_movies  += 1
                        counter_movies_per_year += 1
                        if counter_movies_per_year == options_scrapping.nb_maximum_movies_per_year:
                            # Reached the maximum number to scrap per year
                            break
                    else:
                        assert status == 'Category'
                        counter_not_scraped_categories += 1
            
            if counter_movies_per_year == options_scrapping.nb_maximum_movies_per_year or \
               consecutive_number_of_unpopular_movies == options_scrapping.nb_consecutives_unpopular_movies_to_break:
                print('Stop scrapping for this year')
                break

    # Display some infos
    print("***** Scrapping summary *****")
    print("* Nb movies scanned: ", counter_movies)
    print("* Nb movies scrapped:", counter_scraped_movies)
    print("*****************************")
    
    if counter_not_scraped_not_enough_reviews:
        print("Not scrapped Reviews: ", counter_not_scraped_not_enough_reviews)
    if counter_not_scraped_categories:
        print("Not scrapped Category:  ", counter_not_scraped_categories)

    df_movies = pd.DataFrame(movies, columns = ['title', 'original_title', 'date', 'duration', 'categories', \
                                                'countries', 'star_rating', 'notes', 'reviews', \
                                                'directors', 'actors', 'composers', 'summary', \
                                                'url_thumbnail', 'url_reviews', 'url_similar_movies'])
    return df_movies

# -------------------------------------------
#
#   Scrap movies released the current week
#
#   From: https://www.allocine.fr/film/sorties-semaine/
#
# -------------------------------------------

def scrap_new_release(options_scrapping, url = ''):
    ''' Scrap new movies released in url
        url is either the current week: https://www.allocine.fr/film/sorties-semaine/
               either a specific week:  https://www.allocine.fr/film/agenda/sem-2025-01-22/
        
        Return: Pandas dataframe with all movies' informations
        
        Args:
         - options_scrapping: options to stop scraping a year or to scrap or not a movie,
         - url (string, optional): specify the url of the week.
    '''
    url_new_release = url if url != '' else 'https://www.allocine.fr/film/sorties-semaine/'

    r = requests.get(url_new_release, auth=('user', 'pass'))
    if r.status_code != 200:
        print("url_site error")

    print(f"Scrapping movies on {url_new_release}\n")
    soup_new_releases = BeautifulSoup(r.content, 'html.parser')
    elts_movies = soup_new_releases.find_all('li', class_='mdl')
    counter_scraped_movies = 0
    counter_movies = 0

    movies = []
    for elt_movie in elts_movies[:10]:
        status, movie = scrap_movie(elt_movie, options_scrapping)
        counter_movies += 1
        if status == 'OK':
            movies.append(movie)
            counter_scraped_movies += 1

    # Display some infos
    print("\n*** Scrapping summary ***")
    print("Nb movies scanned: ", counter_movies)
    print("Nb movies scrapped:", counter_scraped_movies, '\n')

    df_movies = pd.DataFrame(movies, columns = ['title', 'original_title', 'date', 'duration', 'categories', \
                                                'countries', 'star_rating', 'notes', 'reviews', \
                                                'directors', 'actors', 'composers', 'summary', \
                                                'url_thumbnail', 'url_reviews', 'url_similar_movies'])
    return df_movies

# Used to scrap movies released from 1st january to 5th february 2025
lst_urls = [
            'https://www.allocine.fr/film/agenda/sem-2025-01-01/',
            'https://www.allocine.fr/film/agenda/sem-2025-01-08/',
            'https://www.allocine.fr/film/agenda/sem-2025-01-15/',
            'https://www.allocine.fr/film/agenda/sem-2025-01-22/',
            'https://www.allocine.fr/film/agenda/sem-2025-02-05/'
            ]

def scrap_new_releases_from_urls(lst_urls, options_scrapping):
    ''' Scrap new movies released in a list of urls
        Used to scrap new movies from 1st january 2025
    '''
    df_movies = pd.DataFrame()
    for url in lst_urls:
        df_movies = pd.concat([df_movies, scrap_new_release(options_scrapping, url=url)])
    return df_movies




# -------------------------------------------
#
#   OMDB request functions
#
# -------------------------------------------


def format_string(st):
    ''' format string 
        from "title of the movie" 
        to title+of+the+movie

        Arg: st string to be converted.
    '''
    res = ''
    for c in st:
        if c.isdigit() or c.isalpha() or c.isspace():
            res += unidecode(c)
        else:
            res += ' '
    return '+'.join([word for word in res.split() if len(word) > 1])

def request_omdb_from_title(title):
    ''' Request the omdb API
    
        return a json dictionary with the information about the movie.

        Arg:
         - title: string with title of the movie we want the infos about.
    '''
    url = f"https://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={format_string(title)}"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"ERROR {title}, Response Code: {r.status_code}")
        print("Request:", url)
        return {'Response': 'False'}
    return json.loads(r.text)

def get_plot_and_thumbail_from_omdb(title):
    ''' return movie plot and thumbail through an API request.

        return: 
          - plot:      string containing the plot of the movie,
          - thumbnail: string containing the url of the thumbnail.

        Arg: title: string with the title of the movie.
    '''
    plot, thumbnail = '', ''
    res_dict = request_omdb_from_title(title)
    lst_keys = res_dict.keys()
    assert 'Response' in res_dict
    if res_dict['Response'] == 'True':
        assert 'Plot' in lst_keys and 'Poster' in lst_keys
        if res_dict['Plot'] != 'N/A':
            plot = res_dict['Plot']
        if res_dict['Poster'] != '' and res_dict['Poster'] != 'N/A':
            thumbnail = res_dict['Poster']
    print("plot:", plot)
    print("thumbnail:", thumbnail)
    return plot + "AND" + thumbnail


def request_to_OMDB(df_movies):
    ''' request OMDB API and add informations into 'df_movies'

        Return: dataframe with new informations (plot and thumbnail_url)

        Arg: df_movies Pandas Dataframe containing movie informations.
    '''
    if df_movies.empty:
        print('Dataframe is empty, nothing to request to OMDB')
        return None

    assert all(column in df_movies.columns for column in ['title', 'original_title', 'summary', 'url_thumbnail'])
    
    df_movies['temp']          = df_movies['original_title'].apply(get_plot_and_thumbail_from_omdb)
    df_movies['summary']       = df_movies['temp'].apply(lambda x : x.split('AND')[0].strip())
    df_movies['url_thumbnail'] = df_movies['temp'].apply(lambda x : x.split('AND')[1].strip())

    print(f"OMDB requestd for {df_movies.shape[0]} movies")
    return df_movies[['title', 'original_title', 'summary', 'url_thumbnail']]






if __name__ == '__main__':

    print("***********************************************************")

    now = datetime.now()
    day, month, year, hour, min, sec = now.strftime("%d-%m-%Y-%H-%M-%S").split('-')
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

    print("--------------- scrapping new release ---------------")
    # -------------- #
    #   Scrapping    #
    # -------------- #
    df_movies = scrap_new_release(options_scrapping, url = 'https://www.allocine.fr/film/agenda/sem-2025-02-26/')
    
    print("--------------- Requesting OMDB ---------------")
    #   Request API OMDB   #
    # -------------------- #
    df_temp = df_movies.copy()
    df_movies_wiht_plot_and_thumbnail = request_to_OMDB(df_temp[['title', 'original_title', 'summary', 'url_thumbnail']])

    # ------------------------------ #
    #   Save the data in csv files   #
    # ------------------------------ #
    df_movies.to_csv(f'csv/movies_week_{year}_{month}_{day}.csv', sep=',', index = False)
    df_movies_wiht_plot_and_thumbnail.to_csv(f'csv/mongoDB_week_{year}_{month}_{day}.csv', sep=',', index = False)

    now = datetime.now()
    print(f"\nFinished Scrapping and Requesting OMDB at: {now.strftime("%H:%M:%S")}")
