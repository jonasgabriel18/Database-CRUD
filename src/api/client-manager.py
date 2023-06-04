import psycopg2
import pandas as pd
import os
import sys

directory = os.path.dirname(os.path.abspath("__file__"))
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.models.utils import random_workout_generator
from src.models.client import ClientData

from flask import Flask, request, render_template, redirect, url_for, flash, render_template_string

template_dir = os.path.abspath('../templates')
app = Flask(__name__, template_folder=template_dir)
cli_manager = ClientData()
    
@app.route('/')
def menu():
    return render_template('menu.html')
    
@app.route("/clients")
def show_all_clients():
    conn = cli_manager.connect()
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
        html_df = df.to_html()
            
        html_table_button = f"""
                            {html_df}
                                <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                            """
            
        return render_template_string(html_table_button)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        cur.close()
        conn.close()
    
@app.route("/personals")
def show_all_personals():
    df = cli_manager.get_all_personals()
    html_df = df.to_html()
    html_table_button = f"""
                                        {html_df}
                                        <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                                        """
        
    return render_template_string(html_table_button)

        
@app.route("/get-client/", methods=["GET", "POST"])
def show_one_client():
    if request.method == "POST":
        client_name = request.form.get('client_name')
        client = cli_manager.get_client_by_name(client_name)
        html_df = client.to_html()
        html_table_button = f"""
                                        {html_df}
                                        <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                                        """
        
        return render_template_string(html_table_button)
    else:
        return render_template('get_client_name.html')

@app.route('/register-client', methods=["GET", "POST"])       
def register_client():
    if request.method == 'GET':
        return render_template('register_client.html')
    elif request.method == 'POST':
        conn = cli_manager.connect()
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

@app.route("/update/", methods=["GET", "POST"])
def update_client():
    if request.method == "POST":
        updated = {key: value for key, value in request.form.items() if value}
        client_name = request.form.get("client_name")
        client = cli_manager.get_client_by_name(client_name)
        client_id = client.iloc[0]['id']

        cli_manager.update(client_id, list(updated.keys()), list(updated.values()))
        client = cli_manager.get_client_by_id(client_id)
        
        html_df = client.to_html()
        html_table_button = f"""
                                {html_df}
                                <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                                """
        
        return render_template_string(html_table_button)
    else:
        return render_template('update_client.html')

@app.route('/delete', methods=["GET", "POST"])
def delete_client():
    if request.method == "POST":
        client_name = request.form["client_name"]
        cli_manager.delete(client_name)

        return "Client deletado com sucesso!"
    else:
        return render_template('get_client_name.html')
            
@app.route('/select-personal/<client_name>', methods=["GET", "POST"])
def select_personal(client_name):
    if request.method == "POST":
        personal_id = int(request.form.get('personal_id'))
        return redirect(url_for("select_schedule", client_name=client_name, personal_id=personal_id))
    else:
        all_personals = cli_manager.get_all_personals()
        return render_template("select_personal.html", client_name=client_name, all_personals=all_personals)

@app.route('/select-schedule/<client_name>/<personal_id>', methods=["GET", "POST"])
def select_schedule(client_name, personal_id):
    if request.method == "POST":
        schedule_id = int(request.form.get("schedule_index"))
        conn = cli_manager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client = cli_manager.get_client_by_name(client_name)
            client_id = client.iloc[0]['id'].item()

            selected_appointment = cli_manager.get_schedule_by_id(schedule_id)

            personal = cli_manager.get_personal_by_id(personal_id)

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
    else:
        schedule = cli_manager.get_available_schedule(personal_id)
        return render_template("select_schedule.html", client_name=client_name, personal_id=personal_id, schedule=schedule)

@app.route('/make-appointment', methods=["GET", "POST"])
def make_appointment():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        client = cli_manager.get_client_by_name(client_name)
        registered_personal_id = client.iloc[0]['personal_id']

        if not registered_personal_id:
            return redirect(url_for("select_personal", client_name=client_name))
        else:
            return redirect(url_for("select_schedule", client_name=client_name, personal_id=registered_personal_id))
    else:
        return render_template("get_client_name.html")
    
@app.route('/appointments/', methods=["GET", "POST"])
def show_appointment():
    if request.method == "POST":
        conn = cli_manager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client_name = request.form.get('client_name')
            client = cli_manager.get_client_by_name(client_name)
            client_id = client.iloc[0]['id']

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
            if df.empty:
                flash('Aluno não possui treinos marcados!')
            html_df = df.to_html()
            html_table_button = f"""
                                        {html_df}
                                        <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                                        """
        
            return render_template_string(html_table_button)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    else:
        return render_template('get_client_name.html')

@app.route("/workouts", methods=["GET", "POST"])
def show_client_workout():
    
    if request.method == "POST":
        conn = cli_manager.connect()
        if not conn:
            raise Exception("Erro na conexão com o database")
        
        cur = conn.cursor()

        try:
            client_name = request.form.get("client_name")
            client = cli_manager.get_client_by_name(client_name)
            client_id = client.iloc[0]['id']
            
            base_query = f"""SELECT e.exercise_name, e.number_of_sets, e.repetitions, e.weight, e.muscle_group 
                            FROM exercises e
                            JOIN clients c
                            ON e.client_id = c.client_id
                            WHERE c.client_id={client_id}"""
            
            cur.execute(base_query)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['Exercicio', 'Séries', 'Repetições', 'Peso', 'Músculo'])
            html_df = df.to_html()
            html_table_button = f"""
                                        {html_df}
                                        <a href="{ url_for('menu') }">Voltar ao Menu Principal</a>
                                        """
        
            return render_template_string(html_table_button)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            cur.close()
            conn.close()
    else:
        return render_template('get_client_name.html')

if __name__ == '__main__':
    app.run(debug=True)