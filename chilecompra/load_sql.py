# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 10:44:44 2021

@author: JavierSchmitt
"""

import pyodbc
import yaml
import os
import pandas as pd


# =============================================================================
#
# # Para probar si está funcionando (Los valores NaN hay que transformarlos
# # siempre a None para que los lea SQL)
#
# import pandas as pd
# import os
#
# path = r'C:\Users\jschmittc\OneDrive - Sociedad Comercializadora Macal\Documentos\comprobacion_botones'
# file = '2021_09_09_comprobacion.xlsx'
# df = pd.read_excel(os.path.join(path,file))
# =============================================================================

df = pd.DataFrame()


#%%


conn_str = (
    r"Driver={SQL Server};"
    r"Server=(local);"
    r"Database=AdventureWorks2019;"
    r"Trusted_Connection=yes;"
    )

conn = pyodbc.connect(conn_str)

cursor = conn.cursor()

for index, row in df.iterrows():
    cursor.execute("""
                   IF (NOT EXISTS (SELECT * 
                                         FROM Gestion11.INFORMATION_SCHEMA.TABLES 
                                         WHERE  TABLE_NAME = 'Check_Descargables'))
                        	BEGIN
                        		CREATE TABLE Gestion11.dbo.Check_Descargables (
                        		IdCheckDesc int IDENTITY(1,1)
                                ,LoteWeb int
                                ,FechaVerificacion date
                                ,Ubicacion varchar(200)
                                ,AntecedentesLegales tinyint
                                ,BasesEspeciales tinyint
                                ,Loteo tinyint
                                ,Procedimiento tinyint
                                ,Bases tinyint
                                ,Planos tinyint
                                ,Brochure tinyint
                                ,Link varchar(50)
                                )
                        	END
                        ELSE
                        	BEGIN
                        		INSERT INTO Gestion11.dbo.Check_Descargables (
                        		LoteWeb
                                ,FechaVerificacion
                                ,Ubicacion
                                ,AntecedentesLegales
                                ,BasesEspeciales
                                ,Loteo
                                ,Procedimiento
                                ,Bases
                                ,Planos
                                ,Brochure
                                ,Link
                        		) values(?,?,?,?,?,?,?,?,?,?,?)
                        	END
                       """,
                       row.LoteWeb,
                       row.FechaVerificacion,
                       row.Ubicacion,
                       row.AntecedentesLegales,
                       row.BasesEspeciales,
                       row.Loteo,
                       row.Procedimiento,
                       row.Bases,
                       row.Planos,
                       row.Brochure,
                       row.Link
                       )


conn.commit()
cursor.close()

print('Trabajo terminado. Todo cargado con éxito.')