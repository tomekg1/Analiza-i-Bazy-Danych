import numpy as np
import pickle

import psycopg2 as pg
import pandas.io.sql as psql
import pandas as pd

from typing import Union, List, Tuple

connection = pg.connect(host='pgsql-196447.vipserv.org', port=5432, dbname='wbauer_adb', user='wbauer_adb', password='adb2020');

def film_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o tytuł filmu, język, oraz kategorię dla zadanego id kategorii.
    Przykład wynikowej tabeli:
    |   |title          |languge    |category|
    |0	|Amadeus Holy	|English	|Action|
    
    Tabela wynikowa ma być posortowana po tylule filmu i języku.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
    
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category_id, int):
        s = '''SELECT f.title, l.name, c.name FROM language l
        INNER JOIN film f ON l.language_id = f.language_id
        INNER JOIN film_category fc ON f.film_id = fc.film_id
        INNER JOIN category c ON fc.category_id = c.category_id
        WHERE c.category_id = %(category_id)s
        ORDER BY f.title
        '''
        df = pd.read_sql(s, con=connection, params={'category_id': category_id})
        df.columns = ['title', 'languge', 'category']
        return df

    return None

    
def number_films_in_category(category_id:int)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów w zadanej kategori przez id kategorii.
    Przykład wynikowej tabeli:
    |   |category   |count|
    |0	|Action 	|64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    category_id (int): wartość id kategorii dla którego wykonujemy zapytanie
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(category_id, int):

        s = '''
        SELECT c.name, COUNT(f.title) FROM category c
        INNER JOIN film_category fc ON c.category_id = fc.category_id
        INNER JOIN film f ON fc.film_id = f.film_id
        WHERE c.category_id = %(category_id)s
        GROUP BY c.name
        
        '''
        df = pd.read_sql(s, con=connection, params={'category_id': category_id})
        df.columns = ['category', 'count']
        return df
    return None

def number_film_by_length(min_length: Union[int,float] = 0, max_length: Union[int,float] = 1e6 ) :
    ''' Funkcja zwracająca wynik zapytania do bazy o ilość filmów o dla poszczegulnych długości pomiędzy wartościami min_length a max_length.
    Przykład wynikowej tabeli:
    |   |length     |count|
    |0	|46 	    |64	  | 
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    min_length (int,float): wartość minimalnej długości filmu
    max_length (int,float): wartość maksymalnej długości filmu
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(min_length, (int, float)) and isinstance(max_length, (int, float)):

        s = '''
        SELECT length, COUNT(length)
        FROM film
        WHERE length >= %(min_l)s AND length <= %(max_l)s
        GROUP BY length
        '''
        df = pd.read_sql(s, con=connection, params={'min_l': min_length, 'max_l': max_length})
        df.columns = ['length', 'count']
        if df.empty:
            return None
        return df

    return None

def client_from_city(city:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o listę klientów z zadanego miasta przez wartość city.
    Przykład wynikowej tabeli:
    |   |city	    |first_name	|last_name
    |0	|Athenai	|Linda	    |Williams
    
    Tabela wynikowa ma być posortowana po nazwisku i imieniu klienta.
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    city (str): nazwa miaste dla którego mamy sporządzić listę klientów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(city, str):
        s = '''
        SELECT ci.city, cu.first_name, cu.last_name FROM customer cu
        INNER JOIN address ad ON cu.address_id = ad.address_id
        INNER JOIN city ci ON ad.city_id = ci.city_id
        WHERE ci.city = %(city)s
        '''
        df = pd.read_sql(s, con=connection, params={'city': city})

        return df
    return None

def avg_amount_by_length(length:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o średnią wartość wypożyczenia filmów dla zadanej długości length.
    Przykład wynikowej tabeli:
    |   |length |avg
    |0	|48	    |4.295389
    
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    length (int,float): długość filmu dla którego mamy pożyczyć średnią wartość wypożyczonych filmów
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(length, (int, float)):
        s = '''
        SELECT f.length, AVG(p.amount) FROM film f
        INNER JOIN inventory inv ON f.film_id = inv.film_id
        INNER JOIN rental r ON inv.inventory_id = r.inventory_id
        INNER JOIN payment p ON r.rental_id = p.rental_id
        WHERE f.length = %(length)s
        GROUP BY f.length
        '''
        df = pd.read_sql(s, con=connection, params={'length': length})

        return df
    return None

def client_by_sum_length(sum_min:Union[int,float])->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o sumaryczny czas wypożyczonych filmów przez klientów powyżej zadanej wartości .
    Przykład wynikowej tabeli:
    |   |first_name |last_name  |sum
    |0  |Brian	    |Wyman  	|1265
    
    Tabela wynikowa powinna być posortowane według sumy, imienia i nazwiska klienta.
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    sum_min (int,float): minimalna wartość sumy długości wypożyczonych filmów którą musi spełniać klient
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(sum_min, (int, float)):
        s = '''
        SELECT cu.first_name, cu.last_name, SUM(f.length) FROM customer cu
        INNER JOIN rental r ON cu.customer_id = r.customer_id
        INNER JOIN inventory inv ON r.inventory_id = inv.inventory_id
        INNER JOIN film f ON inv.film_id = f.film_id
        GROUP BY cu.last_name, cu.first_name
        HAVING SUM(f.length) >= %(sum_min)s
        ORDER BY SUM(f.length), cu.last_name, cu.first_name ASC
        '''
        df = pd.read_sql(s, con=connection, params={'sum_min': sum_min})

        return df
    return None   

def category_statistic_length(name:str)->pd.DataFrame:
    ''' Funkcja zwracająca wynik zapytania do bazy o statystykę długości filmów w kategorii o zadanej nazwie.
    Przykład wynikowej tabeli:
    |   |category   |avg    |sum    |min    |max
    |0	|Action 	|111.60 |7143   |47 	|185
    
    Jeżeli warunki wejściowe nie są spełnione to funkcja powinna zwracać wartość None.
        
    Parameters:
    name (str): Nazwa kategorii dla której ma zostać wypisana statystyka
    
    Returns:
    pd.DataFrame: DataFrame zawierający wyniki zapytania
    '''
    if isinstance(name, str):
        s = '''
        SELECT c.name, AVG(f.length), SUM(f.length), MIN(f.length), MAX(f.length) FROM category c
        INNER JOIN film_category fc ON c.category_id = fc.category_id
        INNER JOIN film f ON fc.film_id = f.film_id
        WHERE c.name = %(name)s
        GROUP BY c.name
        '''
        df = pd.read_sql(s, con=connection, params={'name': name})
        df.rename(columns={'name': 'category'}, inplace=True)
        return df

    return None