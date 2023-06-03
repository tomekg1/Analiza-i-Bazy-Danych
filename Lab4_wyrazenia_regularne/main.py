import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

from typing import Union, List, Tuple

connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

def film_in_category(category:Union[int,str])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego:
        - id: jeżeli categry jest int
        - name: jeżeli category jest str, dokładnie taki jak podana wartość
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category (int,str): wartość kategorii po id (jeżeli typ int) lub nazwie (jeżeli typ str)  dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category, int):
        s = '''SELECT f.title, l.name, c.name FROM language l
        INNER JOIN film f ON l.language_id = f.language_id
        INNER JOIN film_category fc ON f.film_id = fc.film_id
        INNER JOIN category c ON fc.category_id = c.category_id
        WHERE c.category_id = %(category_id)s
        ORDER BY f.title
        '''
        df = pd.read_sql(s, con=connection, params={'category_id': category})
        df.columns = ['title', 'languge', 'category']
        return df

    if isinstance(category, str):
        s = '''SELECT f.title, l.name, c.name FROM language l
        INNER JOIN film f ON l.language_id = f.language_id
        INNER JOIN film_category fc ON f.film_id = fc.film_id
        INNER JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %(category_id)s
        ORDER BY f.title
        '''
        df = pd.read_sql(s, con=connection, params={'category_id': category})
        df.columns = ['title', 'languge', 'category']
        return df

    return None
    
def film_in_category_case_insensitive(category:Union[int,str])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego:
        - id: jeżeli categry jest int
        - name: jeżeli category jest str
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category (int,str): wartość kategorii po id (jeżeli typ int) lub nazwie (jeżeli typ str)  dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category, int):
        df = pd.read_sql(f"""
            select film.title, language.name as languge, category.name as category from film 
            inner join language on language.language_id = film.language_id
            inner join film_category on film_category.film_id = film.film_id
            inner join category on category.category_id = film_category.category_id
            where category.category_id = {category}
            order by film.title, languge
        """, con=connection)
        return df
    elif isinstance(category, str):
        df = pd.read_sql(f"""
            select film.title, language.name as languge, category.name as category from film 
            inner join language on language.language_id = film.language_id
            inner join film_category on film_category.film_id = film.film_id
            inner join category on category.category_id = film_category.category_id
            where category.name ilike '{category}'
            order by film.title, languge
        """, con=connection)
        return df
    else:
        return None
    
def film_cast(title:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o obsadę filmu o dokładnie zadanym tytule.
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |
    |0	|Greg       |Chaplin    | 
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    title (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if type(title) == str:
        df = pd.read_sql("SELECT actor.first_name, actor.last_name FROM film " +
                         "INNER JOIN film_actor ON film.film_id = film_actor.film_id " +
                         "INNER JOIN actor ON film_actor.actor_id = actor.actor_id " +
                         f"WHERE film.title ~ '^{title}$' " +
                         "ORDER BY actor.last_name, actor.first_name", con=connection)
        return df

    else:
        return None
    

def film_title_case_insensitive(words:list) :
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuły filmów zawierających conajmniej jedno z podanych słów z listy words.
    Przykład wynikowej tabeli:
    |   |title              |
    |0	|Crystal Breaking 	| 
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.

    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    words(list): wartość minimalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(words, list):
        reg_ex = ''
        for word in words:
            reg_ex = reg_ex + word + '|'

        reg_ex = reg_ex[:-1]
        reg_ex = '( |^)(' + reg_ex + ')( |$)'

        df = pd.read_sql("SELECT title FROM film " +
                         f"WHERE title ~* '{reg_ex}' " +
                         "ORDER BY title", con=connection)
        return df

    else:
        return None