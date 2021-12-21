
from extract_ordenes_compra import ObtainOC
import argparse
import pandas as pd
from datetime import timedelta
import time
from requests.exceptions import ConnectionError
import logging


def main():

    parser = argparse.ArgumentParser(description='Ingresar los datos para la busqueda de información')
    parser.add_argument('--t', metavar='Ticket', type=str, required=True, help='Se debe ingresar el ticket que entrega mercado publico')
    parser.add_argument('--o', metavar='Organization', type=str, required=True, help='Ingresar nombre de organización a buscar.')
    parser.add_argument('--sdt', metavar='Start Date', type=str, required=True, help='Fecha de inicio en formato YYYY-MM-DD')
    parser.add_argument('--edt', metavar='End Date', type=str, required=True, help='Fecha de termino en formato YYYY-MM-DD')

    args = parser.parse_args()

    dates_list = pd.date_range(args.sdt, args.edt, freq='m')

    data = pd.DataFrame()
    list_data = pd.DataFrame()

    # Como hay meses que la extraccion es erronea mejor procesar el pedido de informacion de manera mensual
    if len(pd.DatetimeIndex(dates_list)) == 0:
        try:
            print('Buscando datos...')
            data, list_data = ObtainOC(args.t, args.o, args.sdt, args.edt)
        except ConnectionError:
            print('Error de conexión, intentando de nuevo en 10 segundos')
            for i in range(10, 0, -1):
                time.sleep(1)
                print(i)
            data, list_data = ObtainOC(args.t, args.o, args.sdt, args.edt)
    elif len(pd.DatetimeIndex(dates_list)) == 1:
        try:
            print('Buscando datos...')
            data, list_data = ObtainOC(args.t, args.o, args.sdt, args.edt)
        except ConnectionError:
            print('Error de conexión, intentando de nuevo en 10 segundos')
            for i in range(10, 0, -1):
                time.sleep(1)
                print(i)
            data, list_data = ObtainOC(args.t, args.o, args.sdt, args.edt)
    else:
        for i in range(len(pd.DatetimeIndex(dates_list))):
            print('Entrando en la tabla temporal {}'.format(i + 1))
            if i == 0:
                sdate = args.sdt
                edate = dates_list[i]
            elif i + 1 >= len(pd.DatetimeIndex(dates_list)):
                sdate = dates_list[i - 1] + timedelta(days=1)
                edate = args.edt
            else:
                sdate = dates_list[i - 1] + timedelta(days=1)
                edate = dates_list[i]

            print(i, ' - ', sdate, ' - ', edate)
            try:
                data_temp, list_data_temp = ObtainOC(args.t, args.o, args.sdt, args.edt)
            except ConnectionError:
                print('Error de conexión, intentando de nuevo en 10 segundos')
                for i in range(10, 0, -1):
                    time.sleep(1)
                    print(i)
                data_temp, list_data_temp = ObtainOC(args.t, args.o, args.sdt, args.edt)
            except KeyError:
                logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.DEBUG)
                logging.error('KeyError occurred with start date: {} and end date: {}'.format(sdate, edate))
            print('Guardando en la tabla temporal {}'.format(i + 1))
            data = data.append(data_temp, ignore_index=True)
            list_data = list_data.append(list_data_temp, ignore_index=True)

    data.to_csv('oc_data_year.csv', sep='|', index=False)
    list_data.to_csv('oc_list_items_year.csv', sep='|', index=False)


if __name__=='__main__':
    main()