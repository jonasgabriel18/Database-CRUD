import psycopg2
import pandas as pd
import os
import sys
import ast

directory = os.path.dirname(os.path.abspath("__file__"))
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.models.utils import random_workout_generator, df_html
from src.models.client import ClientData

from flask import Flask, request, render_template, redirect, url_for, flash, render_template_string, Blueprint

template_dir = os.path.abspath('../templates')
#app = Flask(__name__, template_folder=template_dir)
client_routes = Blueprint('client_routes', __name__)
cli_manager = ClientData()
    
@client_routes.route('/menu-clients')
def menu():
    return render_template('menu.html')
    
@client_routes.route("/clients")
def show_all_clients():
    df = cli_manager.get_all_clients()
    html_table_button = df_html(df)
    return render_template_string(html_table_button)
    
#@client_routes.route("/personals")
#def show_all_personals():
    #df = cli_manager.get_all_personals()
    #html_table_button = df_html(df)
    #return render_template_string(html_table_button)

@client_routes.route("/get-client/", methods=["GET", "POST"])
def show_one_client():
    if request.method == "POST":
        client_name = request.form.get('client_name')
        client = cli_manager.get_client_by_name(client_name)
        html_table_button = df_html(client)
        
        return render_template_string(html_table_button)
    else:
        return render_template('get_client_name.html')

@client_routes.route('/register-client', methods=["GET", "POST"])       
def register_client():
    if request.method == 'GET':
        return render_template('register_client.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        age = int(request.form.get('age'))
        weight = int(request.form.get('weight'))
        height = int(request.form.get('height'))
        balance = int(request.form.get('balance'))
        is_flamengo = request.form.get('is_flamengo') == 'on'
        from_souza = request.form.get('from_souza') == 'on'
        watch_one_piece = request.form.get('watch_one_piece') == 'on'

        if age < 0:
            raise Exception("Idade não pode ser negativa")

        if weight < 0:
            raise Exception("Peso não pode ser negativo")

        if height < 0:
            raise Exception("Altura não pode ser negativa")
        
        register_op = cli_manager.register(name, age, weight, height, balance, is_flamengo, from_souza, watch_one_piece)

        if register_op:
            return f"""Cliente cadastrado com sucesso!
                    <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""
        else:
            return f"""Erro na operação!
                    <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""

@client_routes.route("/update_info/<client_name>", methods=["GET", "POST"])
def update_info(client_name):
    if request.method == "POST":
        updated = {key: value for key, value in request.form.items() if value}
        return redirect(url_for("api.client_routes.update", client_name=client_name, info=updated))
    else:
        return render_template('update_client.html')

@client_routes.route("/update-client/", methods=["GET", "POST"])
def update_client():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        return redirect(url_for("api.client_routes.update_info", client_name=client_name))
    else:
        return render_template('get_client_name.html')

@client_routes.route("/update/<client_name>/<info>")
def update(client_name, info):
    client = cli_manager.get_client_by_name(client_name)
    info = ast.literal_eval(info)

    booleans_info = {
        'is_flamengo': info.get('is_flamengo', 'off') == 'on',
        'from_souza': info.get('from_souza', 'off') == 'on',
        'watch_one_piece': info.get('watch_one_piece', 'off') == 'on',
    }

    info.update(booleans_info)
    
    client_id = client.iloc[0]['id']

    cli_manager.update(client_id, list(info.keys()), list(info.values()))
    client = cli_manager.get_client_by_id(client_id)
        
    html_table_button = df_html(client)
    return render_template_string(html_table_button)

@client_routes.route('/delete-client', methods=["GET", "POST"])
def delete_client():
    if request.method == "POST":
        client_name = request.form["client_name"]
        cli_manager.delete(client_name)

        return f"""Cliente deletado com sucesso!
                    <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""
    else:
        return render_template('get_client_name.html')
            
@client_routes.route('/select-personal/<client_name>', methods=["GET", "POST"])
def select_personal(client_name):
    if request.method == "POST":
        personal_id = int(request.form.get('personal_id'))
        return redirect(url_for("api.client_routes.select_schedule", client_name=client_name, personal_id=personal_id))
    else:
        all_personals = cli_manager.get_all_personals()
        return render_template("select_personal.html", client_name=client_name, all_personals=all_personals)

@client_routes.route('/select-schedule/<client_name>/<personal_id>', methods=["GET", "POST"])
def select_schedule(client_name, personal_id):
    if request.method == "POST":
        schedule_id = request.form.getlist("schedule_index")
        schedule_indexes = list(map(int, schedule_id))
        payment_form = request.form.get("payment_method")
        appointment_op = cli_manager.insert_appointments(client_name, personal_id, schedule_indexes, payment_form)

        if appointment_op:
            return f"""Treino marcado com sucesso!
                        <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""
        else:
            return f"""Saldo insuficiente!!!
                        <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""
    else:
        schedule = cli_manager.get_available_schedule(personal_id)
        if type(schedule) == None:
            return f"""Erro!!!
                        <a href="{ url_for('api.client_routes.menu') }">Voltar ao Menu Principal</a>"""
        return render_template("select_schedule.html", client_name=client_name, personal_id=personal_id, schedule=schedule)

@client_routes.route('/make-appointment', methods=["GET", "POST"])
def make_appointment():
    if request.method == "POST":
        client_name = request.form.get("client_name")
        client = cli_manager.get_client_by_name(client_name)
        registered_personal_id = client.iloc[0]['personal_id']

        if not registered_personal_id:
            return redirect(url_for("api.client_routes.select_personal", client_name=client_name))
        else:
            return redirect(url_for("api.client_routes.select_schedule", client_name=client_name, personal_id=registered_personal_id))
    else:
        return render_template("get_client_name.html")
    
@client_routes.route('/appointments-clients/', methods=["GET", "POST"])
def show_appointment():
    if request.method == "POST":
        client_name = request.form.get('client_name')
        client = cli_manager.get_client_by_name(client_name)
        client_id = client.iloc[0]['id']

        df = cli_manager.get_all_appointments(client_id)

        if df.empty:
            flash('Aluno não possui treinos marcados!')

        html_table_button = df_html(df)
        
        return render_template_string(html_table_button)
    else:
        return render_template('get_client_name.html')

@client_routes.route("/workouts", methods=["GET", "POST"])
def show_client_workout():
    
    if request.method == "POST":
        client_name = request.form.get("client_name")
        client = cli_manager.get_client_by_name(client_name)
        client_id = client.iloc[0]['id']

        df = cli_manager.get_all_workouts(client_id)
        if df.empty:
            flash('Aluno não possui treinos marcados!')

        html_table_button = df_html(df)
        
        return render_template_string(html_table_button)
    else:
        return render_template('get_client_name.html')

#if __name__ == '__main__':
    #app.run(debug=True)