import psycopg2
import pandas as pd
import os
import sys
import ast

directory = os.path.dirname(os.path.abspath("__file__"))
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.models.utils import random_workout_generator, df_html_personal
from src.models.client import ClientData
from src.models.personal import PersonalData

from flask import Flask, request, render_template, redirect, url_for, flash, render_template_string, Blueprint

template_dir = os.path.abspath('../templates')
#app = Flask(__name__, template_folder=template_dir)
personal_routes = Blueprint('personal_routes', __name__)
cli_manager = ClientData()
per_manager = PersonalData()

@personal_routes.route('/menu-personal')
def menu():
    return render_template('menu_personals.html')

@personal_routes.route("/personals")
def show_all_personals():
    df = cli_manager.get_all_personals()
    html_table_button = df_html_personal(df)
    return render_template_string(html_table_button)

@personal_routes.route("/gyms")
def show_all_gyms():
    df = cli_manager.get_all_gyms()
    html_table_button = df_html_personal(df)
    return render_template_string(html_table_button)

@personal_routes.route("/get-personal/", methods=["GET", "POST"])
def show_one_personal():
    if request.method == "POST":
        personal_name = request.form.get('personal_name')
        personal = per_manager.get_personal_by_name(personal_name)
        html_table_button = df_html_personal(personal)
        
        return render_template_string(html_table_button)
    else:
        return render_template('get_personal_name.html')

@personal_routes.route('/register-personal', methods=["GET", "POST"])       
def register_personal():
    if request.method == 'GET':
        return render_template('register_personal.html')
    elif request.method == 'POST':

        name = request.form.get('name')
        age = int(request.form.get('age'))
        weight = int(request.form.get('weight'))
        height = int(request.form.get('height'))
        price = int(request.form.get('price'))
        gym_id = int(request.form.get('gym_id'))
        from_mari = request.form.get('from_mari') == 'on'

        if age < 0 or weight <= 0 or weight <= 0:
            return f"""Valores negativos não são permitidos!
                    #<a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""
        
        register_op = per_manager.register(name, price, age, height, weight, gym_id, from_mari)

        if register_op:
            return f"""Personal cadastrado com sucesso!
                    #<a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""
        else:
            return f"""Erro na operação!
                    #<a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""

@personal_routes.route("/update_info/<personal_name>", methods=["GET", "POST"])
def update_info(personal_name):
    if request.method == "POST":
        updated = {key: value for key, value in request.form.items() if value}
        return redirect(url_for("api.personal_routes.update", personal_name=personal_name, info=updated))
    else:
        return render_template('update_personal.html')

@personal_routes.route("/update-personal/", methods=["GET", "POST"])
def update_personal():
    if request.method == "POST":
        personal_name = request.form.get("personal_name")
        return redirect(url_for("api.personal_routes.update_info", personal_name=personal_name))
    else:
        return render_template('get_personal_name.html')

@personal_routes.route("/update/<personal_name>/<info>")
def update(personal_name, info):
    personal = per_manager.get_personal_by_name(personal_name)
    info = ast.literal_eval(info)

    booleans_info = {
        'from_mari': info.get('from_mari', 'off') == 'on',
    }

    info.update(booleans_info)
    
    personal_id = personal.iloc[0]['id']

    per_manager.update(personal_id, list(info.keys()), list(info.values()))
    personal = per_manager.get_personal_by_id(personal_id)
        
    html_table_button = df_html_personal(personal)
    return render_template_string(html_table_button)

@personal_routes.route('/delete-personal', methods=["GET", "POST"])
def delete_personal():
    if request.method == "POST":
        personal_name = request.form["personal_name"]
        per_manager.delete(personal_name)

        return f"""Personal deletado com sucesso!
                    #<a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""
    else:
        return render_template('get_personal_name.html')

@personal_routes.route('/schedule-personal', methods=["GET", "POST"])#todos os horários
def schedule_personal():
    if request.method == "POST":
        personal_name = request.form["personal_name"]
        schedule = per_manager.get_personal_schedules(personal_name)

        if schedule.empty:
            return f"""Personal ainda não definiu seus horários!
                    <a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""

        df_sched = df_html_personal(schedule)
        return render_template_string(df_sched)
    else:
        return render_template('get_personal_name.html')

@personal_routes.route('/appointments-personal', methods=["GET", "POST"])#treinos ja marcados
def appointments_personal():
    if request.method == "POST":
        personal_name = request.form["personal_name"]
        schedule = per_manager.get_personal_appointments(personal_name)

        if schedule.empty:
            return f"""Personal não possui agendamentos!
                    <a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""
        
        df_sched = df_html_personal(schedule)
        return render_template_string(df_sched)
    else:
        return render_template('get_personal_name.html')

@personal_routes.route('/personal-statistics', methods=["GET", "POST"])
def personal_statistics():
    if request.method == "POST":
        personal_name = request.form.get("personal_name")
        stats = per_manager.get_personal_stats(personal_name)
        df_stats = df_html_personal(stats)
        return render_template_string(df_stats)
    else:
        return render_template('get_personal_name.html')

@personal_routes.route('/add-schedule', methods=["GET", "POST"])
def insert_schedule():
    if request.method == "POST":
        personal_name = request.form.get("personal_name")
        return redirect(url_for('api.personal_routes.select_day', personal_name=personal_name))
    else:
        return render_template('get_personal_name.html')

@personal_routes.route("/select-day/<personal_name>", methods=["GET", "POST"])
def select_day(personal_name):
    if request.method == "POST":
        day = request.form.get("day")
        return redirect(url_for('api.personal_routes.select_time', personal_name=personal_name, day=day))
    else:
        return render_template('get_day.html')

@personal_routes.route("/select-time/<personal_name>/<day>", methods=["GET", "POST"])
def select_time(personal_name, day):
    if request.method == "POST":
        time = request.form.get('time')
        per_manager.add_schedule_time(personal_name, day, time)

        return f"""Horário marcado com sucesso!
                    <a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""
    else:
        return render_template('get_time.html')

@personal_routes.route("/personals-few-schedules")
def get_personals_few_schedules():
    df = per_manager.get_personals_few_availability()

    if df.empty:
        return f"""Não há personais com menos de 5 agendamentos!
                <a href="{ url_for('api.personal_routes.menu') }">Voltar ao Menu Principal</a>"""

    html_table_button = df_html_personal(df)
    return render_template_string(html_table_button)