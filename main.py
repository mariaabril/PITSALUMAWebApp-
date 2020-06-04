from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import jsonify
from flask import session
from flask_wtf import CsrfProtect
from flask import flash
from flask import redirect, url_for
from flask_mail import Mail
from flask_mail import Message

import pandas as pd

import csv

import keras
from keras.models import load_model

from flask import Response
import json
import threading
import time
import re 

import forms
import flights
import model
import database
import config
import filters


import os

app = Flask(__name__)
#from application.plotlydash.dashboar    d import create_dashboard
#app = create_dashboard(app)

app.config.from_object(config.DevelopmentConfig)
#app.config.from_object(config.Config)
app.static_folder = 'static'

use_multithreading = app.config['MULTITHREADING']
print("use_multithreading=" + str(use_multithreading))
loading_thread = None
if use_multithreading:
    loading_thread = threading.Thread(target=flights.init_all_flights_data)
    loading_thread.start()
else:
    flights.init_all_flights_data()

mail = Mail()
database.db.init_app(app)
#-------------------------------------------------------------------------------------------


#conseguimos los diccionarios de los aeropuertos
#flights.get_airport_dicts()
database.CreateDatabase()


@app.route('/')
def start():
    if 'email' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))

@app.route('/vuelos', methods = ['GET', 'POST'])
def index():
    if 'email' not in session:
        return redirect(url_for('login'))

    if use_multithreading:
        while loading_thread.is_alive():
            print("Threading still alive")
            time.sleep(1)

    title = 'APP web PITSALUMA'

    #miramos si el usuario esta en la sesion
    if 'email' in session:
        email = session['email']
        print(email)

    #recopilamos filtros 
    filtros_app = forms.FiltroForm(request.form)
    #convertimos los filtros de origen y destino a numeros para que se puedan comparar con el dataset
    origen_airport = -2
    if filtros_app.origen.data != '':
        origen_airport = flights.get_id_from_name(flights.generalCityNameDict, filtros_app.origen.data.strip())
    dest_airport = -2
    if filtros_app.destino.data != '':
        dest_airport = flights.get_id_from_name(flights.generalCityNameDict, filtros_app.destino.data)
    
    filtros = {
        'fecha_inicio_filtro': filtros_app.fecha_inicio.data,
        'fecha_fin_filtro': filtros_app.fecha_fin.data,
        'ID_filtro': filtros_app.identificador_vuelo.data,
        'origen_filtro': origen_airport,
        'destino_filtro': dest_airport,
        'max_numero_vuelos': filtros_app.num_vuelos.data
    }
    print(filtros)
    
    global vuelos_filtrados, vuelos
    if origen_airport != -1 and dest_airport != -1:
        #conseguimos los vuelos filtrados 
        vuelos_filtrados = filters.filter_flights(flights.all_flights, filtros)
    else:
        vuelos_filtrados = pd.DataFrame()
        filters.error_filter()

    tabla_html = flights.flights_to_html(vuelos_filtrados)

    primera_fila = tabla_html[0]
    vuelos = tabla_html[1]

    fichero = pd.DataFrame(vuelos)
    print(fichero)
    
    fichero.to_csv('templates/graficos/tabla.csv')
    fichero_graficos = fichero

    if fichero_graficos.empty:
        fichero.to_csv('templates/graficos/fichero_graficos.csv')
    else:
        fichero_ciudad_retrasos = fichero.drop(['ID', 'HoraS', 'HoraL', 'Destino', 'Fecha'], axis=1)
        fichero_ciudad_retrasos.to_csv('templates/graficos/fichero_ciudad_retrasos.csv')
        fichero_graficos = fichero.drop(['ID','HoraS','HoraL','Origen','Destino'], axis=1)
        fichero_graficos['Fecha'] = pd.to_datetime(pd.Series(fichero_graficos['Fecha']), format="%d/%m/%Y")
        fichero_graficos = fichero_graficos.groupby('Fecha').max()
        fichero_graficos.to_csv('templates/graficos/fichero_graficos.csv')
       
   
    
    print(fichero)
    return render_template('index.html', title=title, form=filtros_app, primera_fila=primera_fila, vuelos=vuelos, filtros=filtros)

@app.route('/loading')
def loading():
    title = 'CARGANDO'
    if 'email' not in session:
        return redirect(url_for('login'))
    if not use_multithreading:
        return redirect(url_for('index'))
    return render_template('loading.html', title=title)


@app.route('/hasfinishedloading')
def hasfinishedloading():
    if use_multithreading:
        while loading_thread.is_alive():
            print("Threading still alive")
            return jsonify(result=False)
    return jsonify(result=True)

#esta funcion servira unicamente para poder obtener las fotos de la carpeta principal
@app.route('/img/<path:filename>')
def send_file(filename):
    return send_from_directory(os.path.join(app.root_path, 'img'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, app.static_folder), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#esta funcion servira unicamente para poder obtener los html de los graficos en la carpeta principal
@app.route('/templates/graficos/<path:filename>')
def send_file_csv(filename):
    return send_from_directory('templates/graficos', filename)

#estas dos funciones autocompletaran el filtro de las ciudades de destino y origen
@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('q')
    regularexpresion = re.compile(search, re.I)
    lista = [city for city in flights.listCities if regularexpresion.match(city)]
    return jsonify(matching_results=lista)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = forms.LoginForm(request.form)
    title = 'LOG-IN'
    if request.method == 'POST' and login_form.validate():
        email = login_form.email.data
        passw = login_form.password.data
        #si existe va a devolver el usuario y si no devuelve None
        user = database.User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(passw):
            success_message = 'Bienvenido {}'.format(email)
            category = "alert alert-success alert-dismissible"
            flash(success_message, category)
            session['email'] = email
            return redirect( url_for('loading') )
        else:
            user = None
            error_message = 'Usuario o contraseña incorrectos'
            category = "alert alert-danger alert-dismissible"
            flash(error_message, category)
        #validamos que la contraseña sea la misma 
        
    return render_template('login.html', title=title, form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = forms.RegisterForm(request.form)
    title = 'REGISTER'
    if request.method == 'POST' and register_form.validate():
        email = register_form.email.data
        passw = register_form.password.data
        #comprobar que no este en la base de datos
        user = database.User.query.filter_by(email=email).first()
        if user is None:
            user = database.User(email = email, password = passw)
            database.db.session.add(user)
            database.db.session.commit()
        
            msg = Message('Gracias por tu registro!', sender = app.config['MAIL_USERNAME'], recipients=[user.email])
            
            msg.html = render_template('email.html')
            #mail.send(msg)
                        

            success_message = 'Usuario registrado'
            category = "alert alert-success alert-dismissible"
            flash(success_message, category)
            return redirect( url_for('index') )
        
        else:
            error_message = 'Ya existe este usuario'
            category = "alert alert-danger alert-dismissible"
            flash(error_message, category)
        
    return render_template('register.html', title=title, form=register_form)

@app.route('/reset', methods = ['GET', 'POST'])
def reset():
    reset_form = forms.ResetForm(request.form)
    title = 'RESET'
    #if request.method == 'POST' and login_form.validate():
        #cada vez que el usuario inicie sesion, se va a crear una variable de sesion
        #session['username'] = reset_form.username.data
        
    return render_template('reset.html', title=title, form=reset_form)

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email')
    return redirect(url_for('login'))


@app.route('/delete')
def delete():
    if 'email' in session:
        user = database.User.query.filter_by(email=session.get('email')).first()
        database.db.session.delete(user)
        database.db.session.commit()
        session.pop('email')

    success_message = 'Usuario eliminado correctamente'
    category = "alert alert-success alert-dismissible"
    flash(success_message, category)

    return redirect(url_for('login'))

#le metemos el numero correspondiente de error
@app.errorhandler(404)
def page_not_found(e):
    return(render_template('404.html'), 404)

if __name__ == '__main__':
    mail.init_app(app)
    #app.run(port=8001)#, threaded=False)#, use_reloader=False) #hay que quitar el reloader?
    app.run(host='0.0.0.0', port=8003)
