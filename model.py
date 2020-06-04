from tensorflow.keras.models import model_from_json
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
import csv
from datetime import datetime
import flights

def desnormalizarArrDelay(x):
    return ((x * (1171 + 59)) - 59)
  
def desnormalizarDepDelay(x):
    return ((x * (1174 + 35)) - 35)

def make_time_steps(data, h, w, s):
    window_values = range(0, w, 1)
    x_data = np.zeros(shape=(len(data), w, len(data.columns)))
    for i in window_values:
        for j, name in enumerate(data.columns):
            x_data[:, i, j] = data[name].shift(i + 1)
    
    nan_val = np.isnan(x_data).any(axis=(1, 2))
    
    return x_data[~nan_val]
    
  
def get_model():
    json_file = open('archivos/ModeloFinal.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()

    global loaded_model

    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights('archivos/ModeloFinal.h5')
    print('Model loaded!')


#le meto otro parametro con la window(de momento estoy haciendo la window guarra)
def predict(lista_vuelos):
    mms = MinMaxScaler()
    mms.fit(lista_vuelos)
    lista_vuelos = pd.DataFrame(mms.transform(lista_vuelos), index=lista_vuelos.index, columns=lista_vuelos.columns)

    horizon = 1
    window = 64
    step = 1
    
    lista_vuelos = make_time_steps(lista_vuelos, horizon, window, step)
    
    instance_shape = lista_vuelos.shape[1:]

    delaysArr = []
    delaysDep = []
    for y in range(0, len(lista_vuelos - 1)):
        instance_reshaped = lista_vuelos[y].reshape(1, *instance_shape)
        x = loaded_model.predict(instance_reshaped)
        arrDelay = desnormalizarArrDelay(x[0][0][0])
        depDelay = desnormalizarDepDelay(x[1][0][0])
        delaysArr.append(int(round(arrDelay, 0)))
        delaysDep.append(int(round(depDelay, 0)))
        
    return [delaysArr, delaysDep, window]
        

def predict_flights(lista_vuelos):
    lista_vuelos_sin_ID = lista_vuelos.drop(flights.id_column_name, 1)
    predicciones = predict(lista_vuelos_sin_ID)
    return predicciones


def predict_all_flights(all_flights_dict):
    all_flights = None
    for key, vuelosDF in all_flights_dict.items():
        vuelosDF = flights.make_date_index(vuelosDF)
        predictions = predict_flights(vuelosDF)
        window = predictions[2]
        #vuelosDF = vuelosDF[window:]
        
        #anadimos predicciones como columnas al dataframe
        vuelosDF.loc[window:,'PrediccionesLlegada'] = predictions[0]
        vuelosDF.loc[window:,'PrediccionesSalida'] = predictions[1]
        vuelosDF = vuelosDF[window:]

        #all_flights[key] = vuelosDF
        if all_flights is None:
            all_flights = vuelosDF
        else:
            all_flights = pd.concat([all_flights, vuelosDF])
        print("Loaded " + flights.generalCityNameDict[key])
    print("--== All files loaded ==--")

    return all_flights.drop_duplicates(keep='first')
    