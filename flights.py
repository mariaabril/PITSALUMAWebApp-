#aqui haremos todo lo de los vuelos

import csv
import pandas as pd
import os

import model
import filters


id_column_name = 'Flight_Number_Reporting_Airline'
all_flights = None


def make_date_index(data, dt='Date'):
    data[dt]= pd.to_datetime(data[dt])
    data.set_index(dt, inplace=True)
    data.index = data.index.round(freq='T')  
    return data

def flights_to_html(csv_vuelos):
    primera_fila = []
    primera_fila.append({
        'ID': 'ID',
        'Fecha': 'Fecha',
        'HoraS': 'Hora de s. local',
        'HoraL': 'Hora de l. local',
        'Origen': 'Origen',  
        'Destino': 'Destino',
        'RetrasoS': 'Retraso Salida',
        'RetrasoL': 'Retraso Llegada'
        })

    vuelos = []     
    contador = 0
       
    for index, vuelo in csv_vuelos.iterrows():            
        vuelos.append({
        'ID': int(vuelo['Flight_Number_Reporting_Airline']),
        'Fecha': f"{int(vuelo['DayofMonth'])}/{int(vuelo['Month'])}/{int(vuelo['Year'])}",
        'HoraS': get_format_time(vuelo['CRSDepTime']),
        'HoraL':  get_format_time(vuelo['CRSArrTime']),
        'Origen': generalCityNameDict[vuelo['OriginCityName']],  
        'Destino': generalCityNameDict[vuelo['DestCityName']],
        'RetrasoS': int(vuelo['PrediccionesSalida']),
        'RetrasoL': int(vuelo['PrediccionesLlegada'])
        })
        contador += 1
        
    return [primera_fila, vuelos]   
  
    
def get_csv_dict(archivo):
    aeropuertos = csv.reader(open(archivo))
    dictionary = {}

    for aeropuerto in aeropuertos:
        key = int(aeropuerto[0])
        if key in dictionary:
            pass
        dictionary[key] = aeropuerto[1]
        
    return dictionary

def get_cities(diccionario):
    cities = []
    for i in range(0,len(diccionario)):
        cities.append(diccionario.get(i))
    
    return cities

def get_id_from_name(dictionary, search_name):
    #get id from name in dictionary
    for id, name in dictionary.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if name == search_name:
            return id
    return -1

def get_format_time(hora):
    hora = int(hora)
    return '{:02d}:{:02d}'.format(hora // 100, hora % 100)

#leemos todos los archivos importantes de cada ciudad
def read_all_flights():
    with open('archivos/directorio.txt') as f:
        directorio = f.read().splitlines()

    global generalCityNameDict, listCities
    generalCityNameDict = get_csv_dict("archivos/citynamedict.csv")
    listCities = get_cities(generalCityNameDict)

    all_flights_dict = {}
    for city_file in directorio:
        filenameVuelosCSV = "archivos/aeropuertos_ciudades/" + city_file + "_reduced.csv"
        vuelosDF = pd.read_csv(filenameVuelosCSV)

        #queremos que la clave de all_flights_dict sea la clave del diccionario general
        cityId = get_id_from_name(generalCityNameDict, city_file)
        
        if cityId != -1:
            all_flights_dict[cityId] = vuelosDF
        else:
            print(city_file + ' no esta en el diccionario')
            
            
    #print("Chequeo completo")
    return all_flights_dict


def init_all_flights_data():
    all_flights_dict = read_all_flights()

    #leemos modelo 
    model.get_model() 
    
    global all_flights 
    all_flights = model.predict_all_flights(all_flights_dict)
