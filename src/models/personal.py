import psycopg2
import pandas as pd
from .data_manager import DataManager

class PersonalData(DataManager):

    def register(self, name, price, age, height, weight, gym_id, from_mari):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            register_query = """INSERT INTO personals(personal_name, price, age, height, weight, gym_id, from_mari)
                                VALUES (%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(register_query, (name, price, age, height, weight, gym_id, from_mari))
            conn.commit()

            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def update(self, personal_id, columns_to_update, new_values):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()
        try:
            base_query = "UPDATE personals SET "

            for i, column in enumerate(columns_to_update):
                if type(new_values[i]) != bool and new_values[i][0] == '-' and int(new_values[i]) < 0:
                    raise Exception("Valores negativos não são permitidos")
                
                if column == 'name':
                    update_query = f"personal_name = '{new_values[i]}'"
                else:
                    update_query = f"{column} = {new_values[i]}"

                if i != len(columns_to_update)-1:
                    update_query += ', '
                
                base_query += update_query
            
            end_query = f" WHERE personal_id = {personal_id}"
            update_personal_query = base_query + end_query
            
            cur.execute(update_personal_query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def delete(self, personal_name):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            personal = self.get_personal_by_name(personal_name)
            if personal.empty:
                return Exception("ID do personal retornou vazio")
            personal_id = personal.iloc[0]['id']

            delete_query = f"DELETE FROM personals WHERE personal_id = {personal_id}"
            cur.execute(delete_query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

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
        if not personal_id:
            personal = self.get_personal_by_name(personal_name)
            personal_id = personal.iloc[0]['id']

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
    
    def get_personal_schedules(self, personal_name):
        personal = self.get_personal_by_name(personal_name)
        personal_id = personal.iloc[0]['id']

        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            get_available_schedule_query = f"SELECT * FROM personals_schedules WHERE personal_id={personal_id};"
            cur.execute(get_available_schedule_query)
            available_schedule = cur.fetchall()
            
            df_schedule = pd.DataFrame(available_schedule, columns=['id', 'time', 'day', 'availability', 'personal_id']).set_index('id')

            if df_schedule.empty:
                raise Exception("O personal não possui horários livres")

            return df_schedule
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personal_appointments(self, personal_name):
        personal = self.get_personal_by_name(personal_name)
        personal_id = personal.iloc[0]['id']

        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            get_appointments_query = f"""SELECT p.personal_name, c.client_name, ca.appointment_day, ca.appointment_time
                                        FROM personals p
                                        LEFT JOIN clients c ON c.personal_id = p.personal_id
                                        LEFT JOIN clients_appointment ca ON ca.client_id = c.client_id
                                        WHERE p.personal_id = {personal_id};"""
            
            cur.execute(get_appointments_query)
            available_schedule = cur.fetchall()
            
            df_schedule = pd.DataFrame(available_schedule, columns=['name', 'client', 'day', 'time'])

            if df_schedule.empty:
                raise Exception("O personal não possui treinos marcados")

            return df_schedule
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_personal_stats(self, personal_name):
        personal = self.get_personal_by_name(personal_name)
        personal_id = personal.iloc[0]['id']

        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            get_stats_query = f"""SELECT p.personal_name, s.*
                                FROM personals p
                                LEFT JOIN personal_statistics s ON p.personal_id = s.personal_id
                                WHERE p.personal_id = {personal_id};"""
            
            cur.execute(get_stats_query)
            stats = cur.fetchall()
            
            df_stats = pd.DataFrame(stats, columns=['name', 's_id', 'p_id', 'qtd_clients', 'qtd_workouts', 'balance'])
            df_stats.drop(['s_id', 'p_id'], axis=1, inplace=True)

            if df_stats.empty:
                raise Exception("O personal não possui treinos marcados")

            return df_stats
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()