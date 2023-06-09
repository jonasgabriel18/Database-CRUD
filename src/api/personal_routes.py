import psycopg2
import pandas as pd
import os
import sys
import ast

directory = os.path.dirname(os.path.abspath("__file__"))
sys.path.append(os.path.dirname(os.path.dirname(directory)))

from src.models.utils import random_workout_generator, df_html
from src.models.client import ClientData
from src.models.personal import PersonalData

from flask import Flask, request, render_template, redirect, url_for, flash, render_template_string

template_dir = os.path.abspath('../templates')
app = Flask(__name__, template_folder=template_dir)
cli_manager = ClientData()
per_manager = PersonalData()

#@app.route('/')
#def menu():
    #return render_template('menu.html')

@app.route('/register-personal', methods=["GET", "POST"])       
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

        if age < 0:
            raise Exception("Idade não pode ser negativa")

        if weight < 0:
            raise Exception("Peso não pode ser negativo")

        if height < 0:
            raise Exception("Altura não pode ser negativa")
        
        register_op = per_manager.register(name, price, age, height, weight, gym_id, from_mari)

        if register_op:
            return f"""Personal cadastrado com sucesso!"""
            #return f"""Personal cadastrado com sucesso!
                    #<a href="{ url_for('menu') }">Voltar ao Menu Principal</a>"""
        else:
            return f"""Erro na operação!"""
            #return f"""Erro na operação!
                    #<a href="{ url_for('menu') }">Voltar ao Menu Principal</a>"""

@app.route("/update_info/<personal_name>", methods=["GET", "POST"])
def update_info(personal_name):
    if request.method == "POST":
        updated = {key: value for key, value in request.form.items() if value}
        return redirect(url_for("update", personal_name=personal_name, info=updated))
    else:
        return render_template('update_personal.html')

@app.route("/update-personal/", methods=["GET", "POST"])
def update_personal():
    if request.method == "POST":
        personal_name = request.form.get("personal_name")
        return redirect(url_for("update_info", personal_name=personal_name))
    else:
        return render_template('get_personal_name.html')

@app.route("/update/<personal_name>/<info>")
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
        
    html_table_button = df_html(personal)
    #return render_template_string(html_table_button)
    return personal.to_html()

@app.route('/delete-personal', methods=["GET", "POST"])
def delete_personal():
    if request.method == "POST":
        personal_name = request.form["personal_name"]
        per_manager.delete(personal_name)

        return f"""Personal deletado com sucesso!"""
        #return f"""Personal deletado com sucesso!
                    #<a href="{ url_for('menu') }">Voltar ao Menu Principal</a>"""
    else:
        return render_template('get_personal_name.html')

if __name__ == '__main__':
    app.run(debug=True)