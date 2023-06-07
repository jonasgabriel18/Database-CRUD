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

class ClientData:

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
            select_query = """SELECT c.client_name, c.age, c.weight, c.height, p.personal_name, g.gym_name
                            FROM clients c
                            LEFT JOIN personals p
                            ON c.personal_id = p.personal_id
                            LEFT JOIN gym g
                            ON c.gym_id = g.gym_id;"""
            
            cur.execute(select_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['Nome', 'Idade', 'Peso', 'Altura', 'Personal Trainer', 'Academia'])
            
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
            select_query = """SELECT p.personal_id, p.personal_name, p.price, p.age, p.height, p.weight, g.gym_name
                              FROM personals p
                              JOIN gym g
                              ON p.gym_id = g.gym_id;"""
            
            cur.execute(select_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'Nome', 'Preço', 'Idade', 'Altura', 'Peso', 'Academia'])
            
            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_all_appointments(self, client_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            query = f"""SELECT c.client_name, p.personal_name, a.appointment_day, a.appointment_time FROM clients c
                    JOIN personals p
                    ON c.personal_id = p.personal_id
                    JOIN clients_appointment a
                    ON a.client_id = c.client_id
                    WHERE c.client_id = {client_id}
                    ORDER BY a.appointment_day, a.appointment_time ASC;"""
            
            cur.execute(query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['Aluno', 'Personal', 'Dia', 'Hora'])
            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_all_workouts(self, client_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            base_query = f"""SELECT e.exercise_name, e.number_of_sets, e.repetitions, e.weight, e.muscle_group 
                            FROM exercises e
                            JOIN clients c
                            ON e.client_id = c.client_id
                            WHERE c.client_id={client_id}"""
            
            cur.execute(base_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['Exercicio', 'Séries', 'Repetições', 'Peso', 'Músculo'])
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
            select_client_query = f"SELECT * FROM clients WHERE client_name = '{client_name}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym'])

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

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_schedule_by_id(self, schedule_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            select_client_query = f"SELECT * FROM personals_schedules WHERE schedule_id = '{schedule_id}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'time', 'day', 'available', 'personal_id'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def get_available_schedule(self, personal_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            get_available_schedule_query = f"SELECT * FROM personals_schedules WHERE personal_id='{personal_id}' AND is_available = true;"
            cur.execute(get_available_schedule_query)
            available_schedule = cur.fetchall()
            
            df_schedule = pd.DataFrame(available_schedule, columns=['id', 'time', 'day', 'availability', 'personal_id'])

            if df_schedule.empty:
                raise Exception("O personal não possui horários livres")
            
            df_schedule.drop(['availability', 'personal_id'], axis=1, inplace=True)

            return df_schedule
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

            df = pd.DataFrame(rows, columns=['id', 'Nome', 'Preço', 'Idade', 'Altura', 'Peso', 'Academia'])

            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def update(self, client_id, columns_to_update, new_values):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()
        try:
            base_query = "UPDATE clients SET "

            for i, column in enumerate(columns_to_update):
                if new_values[i][0] == '-' and int(new_values[i]) < 0:
                    raise Exception("Valores negativos não são permitidos")
                
                if column == 'name':
                    update_query = f"client_name = '{new_values[i]}'"
                else:
                    update_query = f"{column} = {new_values[i]}"

                if i != len(columns_to_update)-1:
                    update_query += ', '
                
                base_query += update_query
            
            end_query = f" WHERE client_id = {client_id}"
            update_client_query = base_query + end_query
            
            cur.execute(update_client_query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def delete(self, client_name):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.get_client_by_name(client_name)
            if client is None:
                raise Exception("ID do cliente retornou vazio")
            
            client_id = client.iloc[0]['id']

            delete_query = f"DELETE FROM clients WHERE client_id = {client_id}"
            cur.execute(delete_query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
