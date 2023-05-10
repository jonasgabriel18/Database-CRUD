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
    
    def show_all_gyms(self):
        conn = self.connect()
        if not conn:
            return None

        cur = conn.cursor()
        cur.execute("SELECT * FROM gym")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        
        cur.close()
        conn.close()

manager = ClientManager()
manager.show_all_gyms()