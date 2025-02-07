# -----------------------------------------------------
#
# 
#
# -----------------------------------------------------




import os
import re
import io
import math
import copy
import json
import requests
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from IPython.display import display
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# One way to set the driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def _options():
    ''' Another way to set the options '''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--test-type')
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--disable-gpu') if os.name == 'nt' else None # Windows workaround
    options.add_argument('--verbose')
    return options

url_site  = 'https://www.allocine.fr/'
url_films = 'https://www.allocine.fr/films/'



