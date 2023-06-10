import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
            
db_host = os.getenv('DB_HOST')
db_database = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

class DataManager():

    def connect(self):
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_database,
                user=db_user,
                password=db_password,
                port=db_port
            )   

            return conn
        except Exception:
            print('Failed to connect to database')
            return None
    
    def get_all_clients(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")

        cur = conn.cursor()

        try:
            select_query = """SELECT c.client_name, c.age, c.weight, c.height, p.personal_name, g.gym_name, c.balance, c.is_flamengo, c.from_souza, c.watch_one_piece
                            FROM clients c
                            LEFT JOIN personals p
                            ON c.personal_id = p.personal_id
                            LEFT JOIN gym g
                            ON c.gym_id = g.gym_id;"""
            
            cur.execute(select_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['name', 'age', 'weight', 'height', 'personal', 'gym', 'balance', 'is_flamengo', 'from_souza', 'watch_one_piece'])
            
            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

    def get_all_personals(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")

        cur = conn.cursor()

        try:
            select_query = """SELECT p.personal_id, p.personal_name, p.price, p.age, p.height, p.weight, g.gym_name, p.from_mari
                              FROM personals p
                              JOIN gym g
                              ON p.gym_id = g.gym_id;"""
            
            cur.execute(select_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari'])
            
            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personal_by_id(self, personal_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_client_query = f"SELECT * FROM personals WHERE personal_id = '{personal_id}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personal_by_name(self, personal_name):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()
        
        try:
            personal_name = personal_name.title()
            select_client_query = f"SELECT * FROM personals WHERE personal_name = '{personal_name}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_client_by_name(self, client_name):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client_name = client_name.title()
            select_client_query = f"SELECT * FROM clients WHERE client_name = '{client_name}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym', 'balance', 'is_flamengo', 'from_souza', 'watch_one_piece'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_client_by_id(self, client_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_client_query = f"SELECT * FROM clients WHERE client_id = '{client_id}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym', 'balance', 'is_flamengo', 'from_souza', 'watch_one_piece'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()