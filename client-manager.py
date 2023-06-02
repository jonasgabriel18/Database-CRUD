import psycopg2
import pandas as pd
from dotenv import load_dotenv
from utils import random_workout_generator
import os

from flask import Flask, request, render_template

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
            #print(df)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    @app.route("/personals")
    def show_all_personals():
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
            #print(df)
            return df.to_html()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    @app.route("/clients/<client_name>")
    def show_one_client(client_name, show=True):
        conn = ClientManager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()
        client_name = str(client_name)
        #print()

        try:
            select_client_query = f"SELECT * FROM clients WHERE client_name = '{client_name}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym']).set_index('id')
            #print(df)

            return df.to_html()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

    @staticmethod
    @app.route('/register-client', methods=["GET", "POST"])       
    def register_client():
        conn = ClientManager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")

        if request.method == 'GET':
            return render_template('register_client.html')
        elif request.method == 'POST':
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
    
    def update_client_register(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.show_one_client()
            if client is None:
                raise Exception("ID do cliente retornou vazio")
            client_id = client[0]
            
            print()
            column_to_update = input("Digite a coluna que deseja alterar: ")
            new_value = input("Digite seu novo valor: ")

            if column_to_update in ["age", "weight", "height"]:
                new_value = int(new_value)
                if new_value < 0:
                    raise Exception("Valor não pode ser negativo")
            
            update_client_query = f"UPDATE clients SET {column_to_update} = {new_value} WHERE client_id = {client_id}"
            cur.execute(update_client_query)
            conn.commit()
            print()
            print('Informações cadastrais atualizadas com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    def delete_client(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.show_one_client()
            if client is None:
                raise Exception("ID do cliente retornou vazio")
            client_id = client[0]

            delete_query = f"DELETE FROM clients WHERE client_id = {client_id}"
            cur.execute(delete_query)
            conn.commit()

            print()
            print('Cadastro de cliente deletado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def make_appointment(self):
        conn = self.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = self.show_one_client(False)

            if not client:
                print('Nenhum cliente cadastrado com esse nome foi encontrado')
                return None
            
            client_id = client[0]
            registered_personal_id = client[5]

            print()
            if not registered_personal_id:
                all_personals = self.show_all_personals()
                personal_index = int(input('\nDigite o índice do personal trainer de sua escolha: '))

                find_personal_query = f"SELECT * FROM personals WHERE personal_id='{all_personals[personal_index-1][0]}'"
                cur.execute(find_personal_query)
            else:
                find_personal_query = f"SELECT * FROM personals WHERE personal_id='{registered_personal_id}'"
                cur.execute(find_personal_query)

            personal = cur.fetchall()

            #if not personal:
                #print('Nenhum personal trainer registrado com esse nome foi encontrado')
                #return None
            
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
                #self.display_workout_options()
                #choice = int(input("Selecione uma opção: "))
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
    #manager = ClientManager()
"""
    while True:
        manager.display_menu()
        
        choice = int(input("Escolha uma opção: "))
        print()
        if choice == 1:
            manager.show_all_clients()
        elif choice == 2:
            manager.show_one_client()
        elif choice == 3:
            manager.register_client()
        elif choice == 4:
            manager.make_appointment()
        elif choice == 5:
            manager.show_appointment()
        elif choice == 6:
            manager.update_client_register()
        elif choice == 7:
            manager.delete_client()
        elif choice == 8:
             manager.show_client_workout()
        elif choice == 9:
            manager.show_all_personals()
        elif choice == 0:
            break
        else:
            print('Opção inválida')
"""