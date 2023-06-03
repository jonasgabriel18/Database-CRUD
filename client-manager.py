import psycopg2
import pandas as pd
from dotenv import load_dotenv
from utils import random_workout_generator
import os

from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

load_dotenv()
            
db_host = os.getenv('DB_HOST')
db_database = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

class ClientManager:

    @staticmethod
    def connect():
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
    
    def display_menu(self):
        print()
        print("1: Mostrar clientes")
        print("2: Mostrar um cliente")
        print("3: Registrar novo cliente")
        print("4: Agende um treino")
        print("5: Mostrar agendamentos")
        print("6: Atualizar cliente")
        print("7: Excluir cliente")
        print("8: Mostrar treino do cliente")
        print("9: Mostrar personal trainers")
        print("0: Sair")
        print()
    
    @staticmethod
    @app.route("/clients")
    def show_all_clients():
        conn = ClientManager.connect()
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
            return df.to_html()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    @app.route("/personals")
    def show_all_personals():
        df = ClientManager.get_all_personals()
        return df.to_html()
    
    @staticmethod
    def get_all_personals():
        conn = ClientManager.connect()
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

            df = pd.DataFrame(rows, columns=['id', 'Nome', 'Preço', 'Idade', 'Altura', 'Peso', 'Academia']).set_index('id')
            
            return df
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

    @staticmethod
    @app.route("/client_signin/", methods=["GET", "POST"])
    def show_client():
        if request.method == "POST":
            client_name = request.form.get('client_name')
            return redirect(url_for('show_one_client', client_name=client_name))
        else:
            return render_template('show_one_client.html')
    
    @staticmethod
    def get_client_by_name(client_name):
        conn = ClientManager.connect()
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
    
    @staticmethod
    def get_client_by_id(client_id):
        conn = ClientManager.connect()
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
    
    @staticmethod
    def get_schedule_by_id(schedule_id):
        conn = ClientManager.connect()
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
    
    @staticmethod
    def get_available_schedule(personal_id):
        conn = ClientManager.connect()
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
    
    @staticmethod
    def get_personal_by_id(personal_id):
        conn = ClientManager.connect()
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
            
    @staticmethod
    @app.route("/get-client/<client_name>")
    def show_one_client(client_name):
        client = ClientManager.get_client_by_name(client_name)
        return client.to_html()

    @staticmethod
    @app.route('/register-client', methods=["GET", "POST"])       
    def register_client():
        if request.method == 'GET':
            return render_template('register_client.html')
        elif request.method == 'POST':
            conn = ClientManager.connect()
            if not conn:
                raise Exception("Erro na conexão com o database")
            cur = conn.cursor()

            name = request.form.get('name')
            age = int(request.form.get('age'))
            weight = int(request.form.get('weight'))
            height = int(request.form.get('height'))

            if age < 0:
                raise Exception("Idade não pode ser negativa")

            if weight < 0:
                raise Exception("Peso não pode ser negativo")

            if height < 0:
                raise Exception("Altura não pode ser negativa")

            insert_query = """ INSERT INTO clients(client_name, age, weight, height) VALUES (%s,%s,%s,%s)"""
            inserted_values = (name, age, weight, height)

            try:
                cur.execute(insert_query, inserted_values)
                conn.commit()
                return 'Cliente cadastrado com sucesso!'
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                conn.rollback()
            finally:
                cur.close()
                conn.close()
    
    @staticmethod
    @app.route("/update/<client_name>", methods=["GET", "POST"])
    def update_client(client_name):
        if request.method == "POST":
            updated = {key: value for key, value in request.form.items() if value}

            client = ClientManager.get_client_by_name(client_name)
            client_id = client.iloc[0]['id']

            ClientManager.update(client_id, list(updated.keys()), list(updated.values()))
            client = ClientManager.get_client_by_id(client_id)
            
            return client.to_html()
        else:
            return render_template('update_client.html', client_name=client_name)


    @staticmethod
    def update(client_id, columns_to_update, new_values):
        conn = ClientManager.connect()
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
    

    @staticmethod
    def delete(client_name):
        conn = ClientManager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = ClientManager.get_client_by_name(client_name)
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

    @staticmethod
    @app.route('/delete', methods=["GET", "POST"])
    def delete_client():
        if request.method == "POST":
            client_name = request.form["client_name"]
            ClientManager.delete(client_name)

            return render_template('delete_confirmation.html')
        else:
            return render_template('delete_client.html')
                

    @staticmethod
    @app.route('/make_appointment/<client_name>', methods=["GET", "POST"])
    def appointment(client_name):
        conn = ClientManager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = ClientManager.get_client_by_name(client_name)

            if not client:
                print('Nenhum cliente cadastrado com esse nome foi encontrado')
                return None
            
            client_id = client.iloc[0]['id']
            registered_personal_id = client.iloc[0]['personal_id']

            if not registered_personal_id:
                all_personals = ClientManager.get_all_personals()
                personal_index = int(input('\nDigite o índice do personal trainer de sua escolha: '))

                find_personal_query = f"SELECT * FROM personals WHERE personal_id='{all_personals[personal_index-1][0]}'"
                cur.execute(find_personal_query)
            else:
                find_personal_query = f"SELECT * FROM personals WHERE personal_id='{registered_personal_id}'"
                cur.execute(find_personal_query)

            personal = cur.fetchall()
            
            personal_id = personal[0][0]
            personal_gym = personal[0][6]
            
            get_available_schedule_query = f"SELECT * FROM personals_schedules WHERE personal_id='{personal_id}' AND is_available = true;"
            cur.execute(get_available_schedule_query)
            available_schedule = cur.fetchall()
            
            df_schedule = pd.DataFrame(available_schedule, columns=['id', 'time', 'day', 'availability', 'personal_id'])

            if df_schedule.empty:
                raise Exception("O personal não possui horários livres")
            
            df_schedule.drop(['id', 'availability', 'personal_id'], axis=1, inplace=True)
            print()
            print(df_schedule)
            
            print()
            index = int(input('Selecione o índice do horário que voce deseja marcar: '))
            selected_appointment = available_schedule[index]

            update_personal_query = f"UPDATE personals_schedules SET is_available = false WHERE schedule_id = {selected_appointment[0]}"
            cur.execute(update_personal_query)

            insert_client_appointment = "INSERT INTO clients_appointment (client_id, appointment_time, appointment_day) VALUES(%s, %s, %s)"
            cur.execute(insert_client_appointment, (client_id, selected_appointment[1], selected_appointment[2]))

            update_client_query = "UPDATE clients SET personal_id = %s, gym_id = %s WHERE client_id = %s"
            cur.execute(update_client_query, (personal_id, personal_gym, client_id))

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

            print('Treino marcado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    @app.route('/select-personal/<client_name>', methods=["GET", "POST"])
    def select_personal(client_name):
        if request.method == "POST":
            personal_id = int(request.form["personal_index"])
            return redirect(url_for("select_schedule", client_name=client_name, personal_id=personal_id))
        else:
            client = ClientManager.get_client_by_name(client_name)
            registered_personal_id = client.iloc[0]['personal_id']

            if not registered_personal_id:
                all_personals = ClientManager.get_all_personals()
                return render_template("select_personal.html", client_name=client_name, all_personals=all_personals)
            else:
                return redirect(url_for("select_schedule", client_name=client_name, personal_id=registered_personal_id))

    @staticmethod
    @app.route('/select-schedule/<client_name>/<personal_id>', methods=["GET", "POST"])
    def select_schedule(client_name, personal_id):
        if request.method == "POST":
            schedule_id = int(request.form.get("schedule_index"))
            return redirect(url_for("make_appointment", client_name=client_name, personal_id=personal_id, schedule_id=schedule_id))
        else:
            schedule = ClientManager.get_available_schedule(personal_id)
            print(schedule)
            return render_template("select_schedule.html", client_name=client_name, personal_id=personal_id, schedule=schedule)
    
    @staticmethod
    @app.route('/make_appointment/<client_name>/<personal_id>/<schedule_id>')
    def make_appointment(client_name, personal_id, schedule_id):
        conn = ClientManager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = ClientManager.get_client_by_name(client_name)
            client_id = client.iloc[0]['id'].item()

            selected_appointment = ClientManager.get_schedule_by_id(schedule_id)

            personal = ClientManager.get_personal_by_id(personal_id)

            update_personal_query = f"UPDATE personals_schedules SET is_available = false WHERE schedule_id = {schedule_id}"
            cur.execute(update_personal_query)
            time = selected_appointment.iloc[0]['time']
            day = selected_appointment.iloc[0]['day']

            insert_client_appointment = "INSERT INTO clients_appointment (client_id, appointment_time, appointment_day) VALUES(%s, %s, %s)"
            cur.execute(insert_client_appointment, (client_id, time, day))
            
            update_client_query = "UPDATE clients SET personal_id = %s, gym_id = %s WHERE client_id = %s"
            cur.execute(update_client_query, (int(personal_id), personal.iloc[0]['Academia'].item(), client_id))
            
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

            return "Treino marcado com sucesso!"
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

    def show_appointment(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.show_one_client(False)
            client_id = client[0]

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
            print(df)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()


    def display_workout_options(self):
        print()
        print("1: Mostrar treino A")
        print("2: Mostrar treino B")
        print("3: Mostrar treino C")
        print("4: Mostrar treino de peitoral")
        print("5: Mostrar treino de ombro")
        print("6: Mostrar treino de triceps")
        print("7: Mostrar treino de costas")
        print("8: Mostrar treino de biceps")
        print()

    def show_client_workout(self):
            conn = self.connect()
            if not conn:
                raise Exception("Erro na conexão com o database")
            
            cur = conn.cursor()

            try:
                client = self.show_one_client(False)
                client_id = client[0]
                
                print()
                base_query = f"""SELECT e.exercise_name, e.number_of_sets, e.repetitions, e.weight, e.muscle_group 
                               FROM exercises e
                               JOIN clients c
                               ON e.client_id = c.client_id
                               WHERE c.client_id={client_id}"""
                
                cur.execute(base_query)
                rows = cur.fetchall()

                df = pd.DataFrame(rows, columns=['Exercicio', 'Séries', 'Repetições', 'Peso', 'Músculo'])
                print()
                print(df)

            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                cur.close()
                conn.close()

if __name__ == '__main__':
    app.run(debug=True)