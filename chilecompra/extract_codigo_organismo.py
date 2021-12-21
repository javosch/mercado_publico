# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd


def ObtainCodeOrganization(ticket, organization):

    """
    Parameters
    ----------
    ticket : String
        Ticket para conectarse a la API de Mercado Publico.
    organization : String
        Nombre de organizacion a buscar (Ignora mayusculas y minusculas).

    Returns
    -------
    Tuple
    organization_code : List
        Devuelve los codigos pertenecientes a la palabra clave.
    organization_name : List
        Devuelve los nombres de las instituciones pertenecientes a la palabra clave.

    """

    print('Obteniendo codigo de la organizacion...')
    
    url = 'http://api.mercadopublico.cl/servicios/v1/Publico/Empresas/BuscarComprador?ticket=' \
        + ticket
    data = requests.get(url)
    
    content = json.loads(data.text)
    df = pd.DataFrame(content['listaEmpresas'])
    
    search_organization = df[df.NombreEmpresa.str.contains(organization, case=False)]
    
    organization_code = []
    organization_name = []
    
    if search_organization.CodigoEmpresa.value_counts().sum() == 1:
        organization_code.append(int(search_organization.CodigoEmpresa))
        organization_name.append(search_organization.NombreEmpresa.iat[0])
    elif search_organization.CodigoEmpresa.value_counts().sum() == 0:
        print('No se han encontrado resultados')
    else:
        print('Se ha encontrado más de 1 resultado')
        for i in search_organization.index:
            organization_code.append(int(search_organization.CodigoEmpresa[i]))
            organization_name.append(search_organization.NombreEmpresa[i])

    return organization_code, organization_name
