import psycopg2
import pandas as pd
from .utils import random_workout_generator
from .data_manager import DataManager

class ClientData(DataManager):
    
    def get_all_appointments(self, client_id):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            query = f"""SELECT c.client_name, p.personal_name, a.appointment_day, a.appointment_time, a.payment_form, a.value_payed FROM clients c
                    JOIN personals p
                    ON c.personal_id = p.personal_id
                    JOIN clients_appointment a
                    ON a.client_id = c.client_id
                    WHERE c.client_id = {client_id}
                    ORDER BY a.appointment_day, a.appointment_time ASC;"""
            
            cur.execute(query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['client', 'personal', 'day', 'time', 'payment_form', 'value'])
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

            df = pd.DataFrame(rows, columns=['exercise', 'sets', 'repetitions', 'weight', 'muscle'])
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
    
    def register(self, name, age, weight, height, balance, is_flamengo, from_souza, watch_one_piece):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            register_query = """ INSERT INTO clients(client_name, age, weight, height, balance, is_flamengo, from_souza, watch_one_piece) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(register_query, (name, age, weight, height, balance, is_flamengo, from_souza, watch_one_piece))
            conn.commit()

            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return False
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
                if type(new_values[i]) != bool and new_values[i][0] == '-' and int(new_values[i]) < 0:
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

    def make_appointment(self, client_name, personal_id, schedule_id, cost_per_appointment, payment_form):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.get_client_by_name(client_name)
            client_id = client.iloc[0]['id'].item()

            selected_appointment = self.get_schedule_by_id(schedule_id)

            personal = self.get_personal_by_id(personal_id)

            update_personal_query = f"UPDATE personals_schedules SET is_available = false WHERE schedule_id = {schedule_id}"
            cur.execute(update_personal_query)
            time = selected_appointment.iloc[0]['time']
            day = selected_appointment.iloc[0]['day']

            insert_client_appointment = """INSERT INTO clients_appointment (client_id, appointment_time, appointment_day, value_payed, payment_form) 
                                        VALUES(%s, %s, %s, %s, %s)"""
            cur.execute(insert_client_appointment, (client_id, time, day, cost_per_appointment, payment_form))
            
            update_client_query = "UPDATE clients SET personal_id = %s, gym_id = %s WHERE client_id = %s"
            cur.execute(update_client_query, (int(personal_id), personal.iloc[0]['gym'].item(), client_id))
            
            search_exercises_query = f"SELECT * FROM clients c JOIN exercises e ON c.client_id = e.client_id WHERE c.client_id={client_id};"
            cur.execute(search_exercises_query)
            rows = cur.fetchall()
            
            if not rows:
                exercises = random_workout_generator()
                for exercise in exercises:
                    exercise_query = f"""INSERT INTO exercises(client_id, exercise_name, number_of_sets, repetitions, weight, muscle_group)
                                        VALUES ({client_id}, %s, %s, %s, %s, %s);"""
                    cur.execute(exercise_query, exercise)
            
            conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
    
    def insert_appointments(self, client_name, personal_id, schedule_indexes, payment_method):
        conn = self.connect()
        if not conn:
            return None
        cur = conn.cursor()

        try:
            client = self.get_client_by_name(client_name)
            personal = self.get_personal_by_id(personal_id)
            client_id = client.iloc[0]['id']

            balance = client.iloc[0]['balance']
            price = personal.iloc[0]['price']

            total_cost = len(schedule_indexes) * price

            if client.iloc[0]['is_flamengo']:
                total_cost *= 0.95
            
            if client.iloc[0]['from_souza']:
                total_cost *= 0.95
            
            if client.iloc[0]['watch_one_piece']:
                total_cost *= 0.95

            if total_cost > balance:
                return False
            
            new_balance = balance - total_cost
            cost_per_appointment = total_cost//len(schedule_indexes)
            update_balance_query = f"UPDATE clients SET balance = {new_balance} WHERE client_id={client_id};"
            cur.execute(update_balance_query)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

        op_result = True
        for schedule_id in schedule_indexes:
            op = self.make_appointment(client_name, personal_id, schedule_id, cost_per_appointment, payment_method)
            op_result = op_result == op
        
        return op_result
    
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