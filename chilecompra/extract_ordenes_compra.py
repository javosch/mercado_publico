# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
import time
from datetime import date
from extract_codigo_organismo import ObtainCodeOrganization


def ObtainOrdenCompraCodigo(ticket, organization_code, start_date, end_date):

    """
    Parameters
    ----------
    ticket : String
        Ticket para conectarse a la API de Mercado Publico.
    organization_code : Integrer
        Codigo de la organizacion a buscar
    start_date : String
        Fecha inicio en formato YYYY-MM-DD.
    end_date : String
        Fecha final en formato YYYY-MM-DD.

    Returns
    -------
    codes_oc : List
        Regresa una lista con los codigos correspondientes a las fechas ingresadas.

    """

    print('Obteniendo ordenes de compras para la/s fecha/s requeridas...')
    
    sdate = date.fromisoformat(start_date)
    edate = date.fromisoformat(end_date)
    dates_list = pd.date_range(sdate,
                               edate,#-timedelta(days=1),
                               freq='d'
                               ).strftime('%d%m%Y')
    
    urls_code = []
    codes_oc_json = []
    codes_oc = pd.DataFrame()

    print('\n', '-------')
    for i in range(len(dates_list)):
        print('\r', 'Obteniendo fechas: {}/{}'.format(len(dates_list), i+1), end='')
        url_code = 'http://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=' \
             + dates_list[i] + '&CodigoOrganismo=' + str(organization_code) +'&ticket=' + ticket
        urls_code.append(url_code)

    print('\n', '-------')
    for i in range(len(urls_code)):
        print('\r', 'Obteniendo urls de codigos: {}/{}'.format(len(urls_code), i+1),  end='')
        response_code_oc = requests.get(urls_code[i])
        data_json = json.loads(response_code_oc.text)
        try:
            codes_oc_json.append(data_json['Listado'])
        except KeyError:
            print(data_json)
    
#    if sdate != edate:
    print('\n', '-------')
    for i in range(len(codes_oc_json)):
        print('\r', 'Obteniendo codigos de orden de compra: {}/{}'.format(len(codes_oc_json), i+1), end='')
        codes_oc_temp = pd.json_normalize(codes_oc_json[i])
        codes_oc = codes_oc.append(codes_oc_temp)
    #codes_oc = pd.json_normalize(codes_oc_json[0])

    # Pasar a una lista las ordenes de compras
    try:
        codes_oc = codes_oc.Codigo.to_list()
    except:
        pass
    
    return codes_oc


def ObtainOrdenCompraDetails(ticket, codes_oc):

    """
    Parameters
    ----------
    codes_oc : List
        Lista con los codigos a buscar para extraer la informacion.

    ticket : String
        Ticket para conectarse a la API de Mercado Publico.

    Returns
    -------
    data : DataFrame
        Regresa un DataFrame con toda la informacion de las OC.
    
    listado_data : DataFrame
        Regresa un DataFrame con toda la informacion del listado de items por OC.

    """

    print('\n', 'Obteniendo detalle de las ordenes de compra...')
    
    urls_oc = []
    data_oc = []
    listado_data = []

    print('\n', '-------')
    for i in range(len(codes_oc)):
        print('\r', 'Obteniendo url de orden de compra: {}/{}'.format(len(codes_oc), i+1), end='')
        url = 'http://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?' \
              + 'codigo=' + str(codes_oc[i]) +'&ticket=' + ticket
        urls_oc.append(url)

    print('\n', '-------')
    for i in range(len(urls_oc)):
        print('\r', 'Obteniendo orden de compra: {}/{}'.format(len(urls_oc), i+1), end='')
        response_oc = requests.get(urls_oc[i])
        data_oc_json = json.loads(response_oc.text)
        try:
            data_oc.append(data_oc_json['Listado'][0])
        except KeyError:
            pass
    
        # El tiempo minimo para que no de un error de excesos de llamados es de 2 segundos
        time.sleep(2)
    
    data = pd.json_normalize(data_oc)
    
    # Extraer la informacion de los productos por cada OC
    print('\n', 'Obteniendo informacion de los productos de las ordenes de compra...')

    try:
        print('\n', '-------')
        for i in range(len(data['Items.Listado'])):
            print('\r', 'Obteniendo productos de orden de compra: {}/{}'.format(len(data['Items.Listado']), i+1), end='')
            listado_data.append(data['Items.Listado'][i][0])
    
        listado_data = pd.json_normalize(listado_data)
        listado_data['Codigo'] = data.Codigo
    except:
        pass

    return data, listado_data


def ObtainOC(ticket, organization, start_date, end_date):

    """
    Parameters
    ----------
    ticket : String
        Ticket para conectarse a la API de Mercado Publico.
    start_date : String
        Fecha inicio en formato YYYY-MM-DD.
    end_date : String
        Fecha final en formato YYYY-MM-DD.

    Returns
    -------
    data : DataFrame
        Regresa un DataFrame con toda la informacion de las OC.
    
    listado_data : DataFrame
        Regresa un DataFrame con toda la informacion del listado de items
        por OC.

    """

    s_time = time.time()
    
    organization_code, organization_name = ObtainCodeOrganization(ticket, organization)
    i = 0
    if len(organization_code) != 1:
        print(dict(zip(organization_code, organization_name)))
        i = int(input('Seleccione cual desea ver...'))
    
    codes_oc = ObtainOrdenCompraCodigo(ticket,
                                       organization_code[i],
                                       start_date,
                                       end_date)
    
    data, listado_data = ObtainOrdenCompraDetails(ticket, codes_oc)
    
    elapsed_time = time.time() - s_time
    
    m, s = divmod(elapsed_time, 60)
    h, m = divmod(m, 60)
    
    print('Trabajo terminado en {:02d}:{:02d}:{:02d}'.format(int(h), int(m), int(s)))
    
    return data, listado_data
