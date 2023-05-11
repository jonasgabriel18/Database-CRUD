import psycopg2

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
        for row in rows:
            print(row)
        
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
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            print('Cliente registrado com sucesso!')
            cur.close()
            conn.close()


manager = ClientManager()
manager.show_all('clients')
#manager.register_client()