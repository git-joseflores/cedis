import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


# @st.cache
def calcular_densidad_pickeo(datos_sku, datos_embarques):
    """
    docstring
    """
    datos_embarques['Mes'] = datos_embarques['Fecha de Embarque'].dt.month

    datos_distribucion = datos_embarques.groupby(['ID del Producto', 'Mes'], as_index=False)['Unidades Embarcadas'].agg({'Embarque Total':'sum'})
    
    datos_distribucion = pd.merge(datos_sku,
                                  datos_distribucion,
                                  on='ID del Producto',
                                  how='outer')

    datos_distribucion['Volumen x Mes'] = datos_distribucion['Embarque Total'] * datos_distribucion['Volumen x Unidad']
    del datos_distribucion['Embarque Total']
    del datos_distribucion['Volumen x Unidad']
    
    datos_distribucion = pd.pivot(datos_distribucion, index='ID del Producto', columns='Mes')['Volumen x Mes']
    datos_distribucion.columns.name = None

    datos_distribucion['Volumen de Venta'] = datos_distribucion.mean(axis=1)
    datos_distribucion['Volumen de Venta'].fillna(0, inplace=True)
    datos_distribucion.reset_index(inplace=True)
    datos_distribucion = datos_distribucion[['ID del Producto', 'Volumen de Venta']]

    datos_distribucion = pd.merge(datos_sku,
                                  datos_distribucion,
                                  on='ID del Producto',
                                  how='outer')

    del datos_distribucion['Volumen x Unidad']


    datos_popularidad = datos_embarques['ID del Producto'].value_counts().reset_index()
    datos_popularidad.columns = ['ID del Producto', 'Popularidad']

    datos_completos = pd.merge(datos_distribucion,
                                datos_popularidad,
                                on='ID del Producto',
                                how='outer')
    datos_completos['Popularidad'].fillna(value=0, inplace=True)
    
    datos_completos['Densidad de Pickeo'] = datos_completos['Popularidad'] / datos_completos['Volumen de Venta']
    datos_completos['Densidad de Pickeo'].fillna(value=0, inplace=True)
    
    datos_completos['Rank'] = datos_completos.groupby('Zona de Completitud')['Densidad de Pickeo'].rank("dense", ascending=False)
    datos_completos.sort_values(by=['Zona de Completitud', 'Rank'], inplace=True)

    st.write(datos_completos)

    with pd.ExcelWriter("./data/cedis_densidad_de_pickeo.xlsx") as writer:
        datos_completos.to_excel(writer, sheet_name="Densidad de Pickeo", index=False)



def mostrar_densidad_pickeo():
    pass