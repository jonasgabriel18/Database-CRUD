import psycopg2
import pandas as pd
import json
from utils import correlate_day, cls

class ClientManager:

    def connect(self):
        try:
            conn = psycopg2.connect(
                host='localhost',
                database='personals-db',
                user='postgres',
                password='220918',
                port='5432'
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
        print("5: Atualizar cliente")
        print("6: Excluir cliente")
        print("7: Mostrar treino do cliente")
        print("8: Mostrar personal trainers disponíveis")
        print("9: Mostrar academias")
        print("0: Sair")
        print()
    
    def show_all(self, table):
        conn = self.connect()
        if not conn:
            return None

        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            
            if table == 'clients':
                df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym']).set_index('id')
                print(df)
            elif table == 'gym':
                df = pd.DataFrame(rows, columns=['id', 'name', 'address', 'opening_time', 'closing_time', 'fee']).set_index('id')
                print(df)
            elif table == 'personals':
                df = pd.DataFrame(rows, columns=['id', 'name', 'price', 'age', 'height', 'weight', 'gym_id']).set_index('id')
                print(df)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def show_one_client(self):
        conn = self.connect()
        if not conn:
            return None
        
        cur = conn.cursor()
        client_name = input("Digite seu nome: ")
        print()

        try:
            select_client_query = f"SELECT * FROM clients WHERE client_name = '{client_name}'"
            cur.execute(select_client_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['id', 'name', 'age', 'weight', 'height', 'personal_id', 'gym']).set_index('id')
            print(df)

            cur.close()
            conn.close()

            return rows[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            cur.close()
            conn.close()
            
    def register_client(self):
        conn = self.connect()
        if not conn:
            return None

        cur = conn.cursor()

        name = input('Digite seu nome: ')
        age = int(input('Digite sua idade: '))
        weight = int(input('Digite seu peso (em kg): '))
        height = int(input('Digite sua altura (em cm): '))
        print()

        insert_query = """ INSERT INTO clients(client_name, age, weight, height) VALUES (%s,%s,%s,%s)"""
        inserted_values = (name, age, weight, height)

        try:
            cur.execute(insert_query, inserted_values)
            conn.commit()
            print('Cliente cadastrado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def update_client_register(self):
        conn = self.connect()
        if not conn:
            return None
        
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
            
            update_client_query = f"UPDATE clients SET {column_to_update} = {new_value} WHERE client_id = {client_id}"
            cur.execute(update_client_query)
            conn.commit()
            print()
            print('Informações cadastrais atualizadas com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    
    def delete_client(self):
        conn = self.connect()
        if not conn:
            return None
        
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
        finally:
            cur.close()
            conn.close()

    def make_appointment(self):
        conn = self.connect()
        if not conn:
            return None
        
        cur = conn.cursor()

        try:
            client = self.show_one_client()

            if not client:
                print('Nenhum cliente cadastrado com esse nome foi encontrado')
                return None
            
            client_id = client[0]
            registered_personal_id = client[5]

            print()
            if not registered_personal_id:
                self.show_all('personals')

                personal_name = input('\nDigite o nome do personal trainer de sua escolha: ')
                find_personal_query = f"SELECT * FROM personals WHERE personal_name='{personal_name}'"
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
            df_schedule.drop(['id', 'availability', 'personal_id'], axis=1, inplace=True)
            print()
            print(df_schedule)
            
            print()
            index = int(input('Selecione o índice do horário que voce deseja marcar: '))
            selected_appointment = available_schedule[index]
            #appointment_id = selected_appointment[3]

            update_personal_query = f"UPDATE personals_schedules SET is_available = false WHERE schedule_id = {selected_appointment[0]}"
            cur.execute(update_personal_query)

            insert_client_appointment = "INSERT INTO clients_appointment (client_id, appointment_time, appointment_day) VALUES(%s, %s, %s)"
            cur.execute(insert_client_appointment, (client_id, selected_appointment[1], selected_appointment[2]))
            
            ###FALTA DAR INSERT NA TABELA DE RELACIONAMENTO WORKOUT

            update_client_query = "UPDATE clients SET personal_id = %s, gym_id = %s WHERE client_id = %s"
            cur.execute(update_client_query, (personal_id, personal_gym, client_id))

            conn.commit()

            print('Treino marcado com sucesso!')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()

if __name__ == '__main__':
    manager = ClientManager()

    while True:
        manager.display_menu()
        choice = int(input("Escolha uma opção: "))
        print()
        if choice == 1:
            manager.show_all('clients')
        elif choice == 2:
            manager.show_one_client()
        elif choice == 3:
            manager.register_client()
        elif choice == 4:
            manager.make_appointment()
        elif choice == 5:
            manager.update_client_register()
        elif choice == 6:
            manager.delete_client()
        elif choice == 7:
            print('ops')
            #manager.show_client_workout()
        elif choice == 8:
            manager.show_all('personals')
        elif choice == 9:
            manager.show_all('gym')
        elif choice == 0:
            break
        else:
            print('Opção inválida')