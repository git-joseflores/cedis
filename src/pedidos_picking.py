import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from statistics import NormalDist

# @st.cache
def calcular_pedidos_picking(datos_sku, datos_embarques):
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
    datos_por_embarque['Tarimas Pedido'] = datos_por_embarque['Cajas Embarcadas'] / datos_por_embarque['Cajas x Tarima']    
    # st.write(datos_por_embarque)

    datos_picking = datos_por_embarque.groupby(['Pedido', 'Fecha de Embarque']).agg('sum')[['Tarimas Picking', 'Tarimas Pedido']]
    datos_picking = datos_picking.reset_index()
    # st.write(datos_picking)
    
    tarimas_por_dia = datos_picking.groupby(['Fecha de Embarque']).agg('sum')[['Tarimas Pedido']]
    tarimas_por_dia = tarimas_por_dia.reset_index()
    tarimas_por_dia.columns = ['Fecha de Embarque', 'Tarimas Totales por Dia']
    # st.write(tarimas_por_dia)

    
    datos_picking = pd.merge(datos_picking,
                             tarimas_por_dia,
                             on='Fecha de Embarque',
                             how='outer')
    datos_picking.fillna(value=0, inplace=True)

    # st.write(datos_picking)

    promedio = datos_picking['Tarimas Totales por Dia'].mean()
    desviacion_estandar = datos_picking['Tarimas Totales por Dia'].std()
    dict_resumen = {'Promedio de Tarimas por Dia': [promedio],
                    'Desviación Estándar': [desviacion_estandar],
                    'Proteccion 99%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.99)],
                    'Proteccion 95%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.95)],
                    'Proteccion 90%': [NormalDist(mu=promedio, sigma=desviacion_estandar).inv_cdf(0.90)]}
    tabla_resumen = pd.DataFrame.from_dict(dict_resumen).fillna(0)
    st.table(tabla_resumen.style.format('{:,.1f}'))


    with pd.ExcelWriter("./data/cedis_pedidos_picking.xlsx") as writer:
        tabla_resumen.to_excel(writer, sheet_name="Resumen de Pedidos para Picking", index=False)
        datos_picking.to_excel(writer, sheet_name="Pedidos para Picking Diario", index=False)




def mostrar_pedidos_picking():
    pass