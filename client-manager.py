import psycopg2
import pandas as pd
import json
from utils import correlate_day

class ClientManager:

    def connect(self):
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='crud',
                user='postgres',
                password='220918',
                port='5432'
            )   

            return conn
        except Exception:
            print('Failed to connect to database')
            return None
    
    def display_menu(self):
        print("1: Show clients")
        print("2: Register new client")
        print("3: Update client")
        print("4: Delete client")
        print("5: Show client workout")
        print("6: Show available personal trainers")
        print("7: Show gyms")
    
    def show_all(self, table):
        conn = self.connect()
        if not conn:
            return None

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        
        if table == 'clients':
            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'appointment']).set_index('id')
            print(df)
        elif table == 'gym':
            df = pd.DataFrame(rows, columns=['id', 'name', 'address', 'opening_time', 'closing_time', 'fee']).set_index('id')
            print(df)
        elif table == 'personals':
            df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'linked_gym', 'client_id', 'schedule', 'age', 'height', 'weight']).set_index('id')
            print(df)
        
        cur.close()
        conn.close()
    
    def register_client(self):
        conn = self.connect()
        if not conn:
            return None

        cur = conn.cursor()

        name = input('Insira seu nome: ')
        age = int(input('Insira sua idade: '))
        weight = int(input('Insira seu peso (em kg): '))
        height = int(input('Insira sua altura (em cm): '))

        insert_query = """ INSERT INTO clients(client_name, age, weight, height) VALUES (%s,%s,%s,%s)"""
        inserted_values = (name, age, weight, height)

        try:
            cur.execute(insert_query, inserted_values)
            conn.commit()
            print('Cliente registrado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

    def make_appointment(self):
        conn = self.connect()
        if not conn:
            return None
        
        cur = conn.cursor()
        client_name = input('Insira seu nome: ')

        try:
            find_client_query = f"SELECT * FROM clients WHERE client_name='{client_name}'"
            cur.execute(find_client_query)
            client = cur.fetchall()

            if not client:
                print('Não foi encontrado nenhum cliente registrado com esse nome.')
                return None
            elif len(client) > 1:
                print('Foi encontrado mais de um cliente com esse nome')
                return None
            client_id = client[0][0]
            self.show_all('personals')
            personal_name = input('Digite o nome do personal trainer de sua escolha: ')
            find_personal_query = f"SELECT * FROM personals WHERE personal_name='{personal_name}'"
            cur.execute(find_personal_query)
            personal = cur.fetchall()

            if not personal:
                print('Não foi encontrado nenhum personal trainer registrado com esse nome.')
                return None
            elif len(personal) > 1:
                print('Foi encontrado mais de um personal trainer com esse nome!')
                return None
            
            personal_id = personal[0][0]
            personal_schedule = personal[0][5]
            available_schedule = dict.fromkeys(personal_schedule.keys())
            for key in personal_schedule:
                for _, availability in personal_schedule[key].items():
                    if availability:
                        available_schedule[key] = personal_schedule[key]
            
            print("\nEscolha um dia da semana\n:")
            print('''
            1: Segunda-feira
            2: Terça-feira
            3: Quarta-feira
            4: Quinta-feira
            5: Sexta-feira
            6: Sábado
            ''')

            day = int(input())
            day = correlate_day(day)

            print("\nEscolha um horario livre: ")
            print(available_schedule[day])
            free_time = list(available_schedule[day].keys())
            for i in range(len(free_time)):
                print(f"{i}: {free_time[i]}")
            
            time = int(input())
            time = free_time[time]
            personal_schedule[day][time] = False
            personal_schedule = json.dumps(personal_schedule)

            update_personal_query = "UPDATE personals SET schedule = %s, client_id = %s WHERE personal_id = %s"
            cur.execute(update_personal_query, (personal_schedule, client_id, personal_id))

            time_string = f"{time[:2]}:00:00"
            update_client_query = "UPDATE clients SET personal_id = %s, appointment = %s WHERE client_id = %s"
            cur.execute(update_client_query, (personal_id, time_string, client_id))

            conn.commit()

            print('Treino marcado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

manager = ClientManager()
#manager.show_all('gym')
#manager.register_client()
manager.make_appointment()