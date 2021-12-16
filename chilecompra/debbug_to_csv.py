from extract_ordenes_compra import ObtainOC
import argparse
import pandas as pd
from datetime import timedelta
import time
from requests.exceptions import ConnectionError
import logging

t = '961C67F0-9FC9-4B63-97EC-69AC6BF0F6F8'
o = 'Armada'
sdt = '2021-01-01'
edt = '2021-12-12'

dates_list = pd.date_range(sdt, edt, freq='m')

data = pd.DataFrame()
list_data = pd.DataFrame()

# Como hay meses que la extraccion es erronea mejor procesar el pedido de informacion de manera mensual
if len(pd.DatetimeIndex(dates_list)) == 1:
    try:
        data, list_data = ObtainOC(t, o, sdt, edt)
    except ConnectionError:
        print('Error de conexión, intentando de nuevo en 10 segundos')
        for i in range(10, 0, -1):
            time.sleep(1)
            print(i)
        data, list_data = ObtainOC(t, o, sdt, edt)

else:
    for i in range(len(pd.DatetimeIndex(dates_list))):
        print('Entrando en la tabla temporal {}'.format(i+1))
        if i == 0:
            sdate = sdt
            edate = dates_list[i]
        elif i+1 >= len(pd.DatetimeIndex(dates_list)):
            sdate = dates_list[i-1] + timedelta(days=1)
            edate = edt
        else:
            sdate = dates_list[i-1] + timedelta(days=1)
            edate = dates_list[i]

        print(i, ' - ', sdate, ' - ', edate)
        try:
            data_temp, list_data_temp = ObtainOC(t, o, sdt, edt)
        except ConnectionError:
            print('Error de conexión, intentando de nuevo en 10 segundos')
            for i in range(10, 0, -1):
                time.sleep(1)
                print(i)
            data_temp, list_data_temp = ObtainOC(t, o, sdt, edt)
        except KeyError:
            logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.DEBUG)
            logging.error('KeyError occurred with start date: {} and end date: {}'.format(sdate,edate))
        print('Guardando en la tabla temporal {}'.format(i+1))
        data = data.append(data_temp, ignore_index=True)
        list_data = list_data.append(list_data_temp, ignore_index=True)

data.to_csv('oc_data.csv', sep='|', index=False)
list_data.to_csv('oc_list_items.csv', sep='|', index=False)
