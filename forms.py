from wtforms import Form
from wtforms import  StringField, TextField, IntegerField, FieldList, SelectField
from wtforms.fields.html5 import EmailField
from wtforms import PasswordField, BooleanField, SubmitField
from datetime import datetime
from wtforms import validators
from wtforms.fields.html5 import DateField


class  FiltroForm(Form):
    fecha_inicio = DateField('Fecha inicio', format='%Y-%m-%d')
    fecha_fin = DateField('Fecha fin', format='%Y-%m-%d')
    identificador_vuelo = IntegerField('Identificador')
    #hora_salida = TimeField('Hora de salida')
    origen = StringField('Origen', id='origin_autocomplete')
    destino = StringField('Destino', id='dest_autocomplete')
    num_vuelos = IntegerField('Max nº de vuelos a mostrar')


class LoginForm(Form):
    email = EmailField('Email', [
        validators.Email(message="Por favor, introduce un email valido "),
        validators.Required(message="El email es obligatorio"),
        ])
    
    password = PasswordField('Contaseña', [
        validators.Required(message="La contraseña es obligatoria"),
    ])

class RegisterForm(Form):
    email = EmailField('Email', [
        validators.Email(message="Por favor, introduce un email valido "),
        validators.Required(message="El email es obligatorio"),
        ])
    
    password = PasswordField('Contaseña', [
        validators.Required(message="La contraseña es obligatoria"),
    ])

class ResetForm(Form):
    email = EmailField('Email', [
        validators.Email(message="Por favor, introduce un email valido "),
        validators.Required(message="El email es obligatorio"),
        ])
    