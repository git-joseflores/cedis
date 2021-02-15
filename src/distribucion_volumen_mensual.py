import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


# @st.cache
def calcular_distribucion_volumen(datos_embarques, datos_sku):
    """
    docstring
    """
    datos_embarques['Mes'] = datos_embarques['Fecha Embarque'].dt.month
    
    datos_distribucion = datos_embarques.groupby(['ID Producto', 'Mes'], as_index=False)['Unidades Embarcadas'].agg({'Embarque Total':'sum'})
    
    datos_distribucion = pd.merge(datos_distribucion,
                                  datos_sku,
                                  on='ID Producto',
                                  how='outer')

    datos_distribucion['Volumen x Mes'] = datos_distribucion['Embarque Total'] * datos_distribucion['Volumen x Unidad']
    del datos_distribucion['Embarque Total']
    del datos_distribucion['Volumen x Unidad']

    datos_distribucion = datos_distribucion.pivot(index='ID Producto', columns='Mes')['Volumen x Mes']
    datos_distribucion.columns.name = None
    
    datos_distribucion['Volumen Promedio'] = datos_distribucion.mean(axis=1)
    datos_distribucion.reset_index(inplace=True)
    
    return datos_distribucion[['ID Producto', 'Volumen Promedio']]


def mostrar_distribucion_volumen(datos, numero_de_secciones, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    secciones = np.linspace(datos['Volumen Promedio'].min(), datos['Volumen Promedio'].max(), numero_de_secciones + 1)
    
    datos['Secciones'] = pd.cut(datos['Volumen Promedio'], secciones, include_lowest=True)
    
    datos_distribucion = datos.groupby('Secciones', as_index=False)['Volumen Promedio'].agg({'Volumen Acumulado':'sum'})
    
    datos_distribucion['Volumen Porcentaje'] = datos_distribucion['Volumen Acumulado'] / datos_distribucion['Volumen Acumulado'].sum()
    
    datos_distribucion['Secciones']= datos_distribucion['Secciones'].astype(str)
    
    fig = px.bar(datos_distribucion,
                 x='Secciones',
                 y="Volumen Porcentaje",
                 labels={'Secciones': f'<b>Metros Cúbicos Mensuales</b>',
                          'Volumen Porcentaje': f'<b>% de Productos</b>'})

    fig.update_layout(title_text=f'<b>Distribución de Volumen Embarcado por Mes<b>',
                      title_x=0.5,
                      width=850,
                      height=700,
                      margin=dict(
                          l=50,
                          r=50,
                          b=150,
                          t=35,
                          pad=5),
                      xaxis={'tickfont': {'size': 10}})
    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(hovertemplate='Metros Cúbicos Mensuales: %{x} <br>% de Productos: %{y:.0%}')

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                            xref='paper', yref='paper',
                            x=1, y=-0.25,
                            sizex=0.17, sizey=0.17,
                            xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU y Embarques<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                    xref='paper', yref='paper',
                    x=0.5, y=-0.27,
                    showarrow=False,
                    font={'size': 11})

    st.plotly_chart(fig)
