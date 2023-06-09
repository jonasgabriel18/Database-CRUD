import psycopg2
import pandas as pd
from .data_manager import DataManager

class PersonalData(DataManager):

    def get_personals_per_price(self, lower_bound=0, upper_bound=1000):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_personals_query = f"""SELECT * FROM personals p
                                        WHERE p.price BETWEEN {lower_bound} AND {upper_bound}"""
            
            cur.execute(select_personals_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personals_from_mari(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_personals_query = f"""SELECT * FROM personals p
                                        WHERE p.from_mari = true"""
            
            cur.execute(select_personals_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personals_few_availability(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_personals_query = """SELECT p.*, COUNT(ps.is_available)
                                        FROM personals p
                                        JOIN personals_schedules ps ON p.personal_id = ps.personal_id
                                        WHERE ps.is_available = true
                                        GROUP BY p.personal_id
                                        HAVING COUNT(ps.is_available) <= 5;"""
            
            cur.execute(select_personals_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym', 'from_mari', 'qtd_schedules'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personal_statistics(self, personal_id=None, personal_name=None):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_personals_query = f"""SELECT * FROM personal_statistics ps
                                         JOIN personals p
                                         ON p.personal_id = ps.personal_id
                                         WHERE p.personal_id = {personal_id}"""
            
            cur.execute(select_personals_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'personal_id', 'qtd_clients', 'qtd_workouts', 'balance', 'p_id', 'name', 'price', 'age', 'height', 
                                             'weight', 'gym_id', 'from_mari']).set_index('id')
            
            df.drop(['p_id'], axis=1, inplace=True)

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()