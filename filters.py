import pandas as pd
from flask import flash

import flights

def error_filter():
    error_message = 'El filtro es incorrecto'
    category = "alert alert-danger alert-dismissible"
    flash(error_message, category)

def get_filter_date(fecha):
    dia_filtro = fecha.day
    mes_filtro = fecha.month
    ano_filtro = fecha.year
    fecha_fitrada = (ano_filtro * 31 * 12 + mes_filtro * 31 + dia_filtro)
    return fecha_fitrada

def filter_flights(all_flights, filtros):
    
    if filtros['ID_filtro'] != None:
        all_flights = all_flights[all_flights['Flight_Number_Reporting_Airline'] == filtros['ID_filtro']]

    #-1 significa que no hay nada 
    if filtros['origen_filtro'] != -2:
        all_flights = all_flights[all_flights['OriginCityName'] == filtros['origen_filtro']]
        
    if filtros['destino_filtro'] != -2:
        all_flights = all_flights[all_flights['DestCityName'] == filtros['destino_filtro']]
        
    #TODO poner bien la fecha de la fecha del filtro dependiendo del resultado del filtro 

    ano = all_flights['Year']
    mes = all_flights['Month']
    dia = all_flights['DayofMonth']

    if filtros['fecha_inicio_filtro'] is not None and filtros['fecha_fin_filtro'] is not None:
        fecha_inicio_fitrada = get_filter_date(filtros['fecha_inicio_filtro'])
        fecha_fin_fitrada = get_filter_date(filtros['fecha_fin_filtro'])      
        despues_inicial_antes_final = (fecha_inicio_fitrada <= (ano * 31 * 12 + mes * 31 + dia)) & ((ano * 31 * 12 + mes * 31 + dia) <= fecha_fin_fitrada)

        all_flights = all_flights[despues_inicial_antes_final]    
        
        if fecha_inicio_fitrada > fecha_fin_fitrada:                
            #si las fechas no cuadran que salte un messsage
            error_message = 'La fecha inicio es más tarde que la de fin'
            category = "alert alert-danger alert-dismissible"
            flash(error_message, category)

    elif filtros['fecha_inicio_filtro'] is not None:
        fecha_inicio_fitrada = get_filter_date(filtros['fecha_inicio_filtro'])    
        despues_fecha_inicio = (ano * 31 * 12 + mes * 31 + dia) >= fecha_inicio_fitrada
        all_flights = all_flights[despues_fecha_inicio]
    
    elif filtros['fecha_fin_filtro'] is not None:
        fecha_fin_fitrada = get_filter_date(filtros['fecha_fin_filtro'])
        antes_fecha_final = (ano * 31 * 12 + mes * 31 + dia) <= fecha_fin_fitrada
        all_flights = all_flights[antes_fecha_final]
    
    max_num_vuelos = 30
    if filtros['max_numero_vuelos'] is not None:
        max_num_vuelos = filtros['max_numero_vuelos']

    vuelos = all_flights.sort_index(axis=0)
    vuelos = vuelos.head(max_num_vuelos)
    

    return vuelos   
    