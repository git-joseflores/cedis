import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from statistics import NormalDist


# @st.cache
def calcular_almancenamiento_picking(datos_sku, datos_embarques):
    """
    docstring
    """
    datos_por_embarque = pd.merge(datos_sku,
                                 datos_embarques,
                                 on='ID del Producto',
                                 how='outer')

    datos_por_embarque['Fecha de Embarque'] = datos_por_embarque['Fecha de Embarque'].dt.strftime('%Y-%m-%d')
    datos_por_embarque.fillna(value=0, inplace=True)

    datos_por_embarque['Cajas Picking'] = datos_por_embarque['Cajas Embarcadas'].mod(datos_por_embarque['Cajas x Tarima'])
    datos_por_embarque['Tarimas Picking'] = datos_por_embarque['Cajas Picking'] / datos_por_embarque['Cajas x Tarima']

    # st.write('Obtuve Cajas Picking y Tarimas Picking')
    # st.write(datos_por_embarque)

    ###########################################
    suma_tarimas_picking = datos_por_embarque.groupby(['ID del Producto'], as_index=False)['Tarimas Picking'].agg({'Suma Tarimas Picking':'sum'})

    
    frequencia_pickeo = datos_por_embarque.groupby(['ID del Producto', 'Fecha de Embarque'])['Cajas Embarcadas'].size()
    frequencia_pickeo = frequencia_pickeo.reset_index()
    frequencia_pickeo = frequencia_pickeo['ID del Producto'].value_counts()
    frequencia_pickeo = frequencia_pickeo.reset_index()
    frequencia_pickeo.columns = ['ID del Producto', 'Frecuencia Pickeo']


    datos_por_sku = pd.merge(suma_tarimas_picking,
                             frequencia_pickeo,
                             on='ID del Producto',
                             how='outer')
    datos_por_sku.fillna(value=0, inplace=True)

    datos_por_sku['Media de Tarimas Picking Diarias'] = datos_por_sku['Suma Tarimas Picking'] / datos_por_sku['Frecuencia Pickeo']

    # st.write('Obtuve Suma de Tarimas Picking, Frecuencia de Pickeo y Media de Tarimas Picking Diarias')
    # st.write(datos_por_sku)

    # ###########################################
    datos_por_embarque = pd.merge(datos_por_embarque,
                                  datos_por_sku[['ID del Producto', 'Media de Tarimas Picking Diarias']],
                                  on='ID del Producto',
                                  how='outer')

    datos_por_embarque['Diferencia Media Cuadrada'] = (datos_por_embarque['Tarimas Picking'] - datos_por_embarque['Media de Tarimas Picking Diarias']) ** 2

    # st.write('Obtuve Diferencia Media Cuadrada')
    # st.write(datos_por_embarque)

    ###########################################
    suma_dif_media_cuadrada = datos_por_embarque.groupby(['ID del Producto'], as_index=False)['Diferencia Media Cuadrada'].agg({'Suma Diferencia Media Cuadrada':'sum'})

    datos_por_sku = pd.merge(datos_por_sku,
                             suma_dif_media_cuadrada,
                             on='ID del Producto',
                             how='outer')

    # st.write('Obtuve Suma Diferencia Media Cuadrada')
    # st.write(datos_por_sku)

    ###########################################
    datos_por_sku['Media de Tarimas Picking Diarias Cuadrada'] = datos_por_sku['Media de Tarimas Picking Diarias'] ** 2
    datos_por_sku['Dias sin Ventas'] = datos_por_embarque['Fecha de Embarque'].nunique() - datos_por_sku['Frecuencia Pickeo']

    datos_por_sku['Media de los Dias sin Ventas'] = datos_por_sku['Dias sin Ventas'] * datos_por_sku['Media de Tarimas Picking Diarias Cuadrada']
    datos_por_sku['Desviacion Estandar de los Dias sin Ventas'] = ((datos_por_sku['Media de los Dias sin Ventas'] + datos_por_sku['Suma Diferencia Media Cuadrada']) / (datos_por_embarque['Fecha de Embarque'].nunique())) ** 0.5

    datos_por_sku['Proteccion 99%'] = datos_por_sku['Media de los Dias sin Ventas'] + (3 * datos_por_sku['Desviacion Estandar de los Dias sin Ventas'])
    datos_por_sku['Rounded Proteccion 99%'] = datos_por_sku['Proteccion 99%'].round()

    # # st.write('Obtuve Media de Tarimas Picking Diarias Cuadrada')
    # st.write(datos_por_embarque)

    # datos_por_sku = datos_por_sku[['ID del Producto', 'Media de los Dias sin Ventas', 'Desviacion Estandar de los Dias sin Ventas', 'Proteccion 99%', 'Rounded Proteccion 99%']]
    # datos_por_sku.columns = ['ID del Producto', 'Picking Diario de Tarimas Promedio', 'Desviacion Estandar', 'Proteccion 99%', 'Proteccion 99% Redondeado']

    datos_por_sku = datos_por_sku[['ID del Producto', 'Media de los Dias sin Ventas']]
    datos_por_sku.columns = ['ID del Producto', 'Picking Diario de Tarimas Promedio']
    # st.write(datos_por_sku)


    # promedio = 220.33
    # desviacion_estandar = 192.13

    promedio = datos_por_sku['Picking Diario de Tarimas Promedio'].mean()
    desviacion_estandar = datos_por_sku['Picking Diario de Tarimas Promedio'].std()
    dict_resumen = {'Promedio de Tarimas por Dia': [promedio],
                    'Desviación Estándar': [desviacion_estandar],
                    'Proteccion 99%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.99)],
                    'Proteccion 95%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.95)],
                    'Proteccion 90%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.90)]}
    tabla_resumen = pd.DataFrame.from_dict(dict_resumen).fillna(0)
    st.table(tabla_resumen.style.format('{:,.1f}'))


    with pd.ExcelWriter("./data/cedis_almacenamiento_picking.xlsx") as writer:
        tabla_resumen.to_excel(writer, sheet_name="Resumen de Tarimas para Picking", index=False)
        datos_por_sku.to_excel(writer, sheet_name="Tarimas para Picking Diario", index=False)




def mostrar_almancenamiento_picking():
    pass