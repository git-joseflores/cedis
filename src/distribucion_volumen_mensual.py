import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


@st.cache
def calcular_distribucion_volumen(datos_sku, datos_embarques, cortes):
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
    
    datos_distribucion['Volumen Promedio Mensual'] = datos_distribucion.mean(axis=1)
    datos_distribucion['Volumen Promedio Mensual'].fillna(0, inplace=True)
    datos_distribucion.reset_index(inplace=True)
    datos_distribucion = datos_distribucion[['ID del Producto', 'Volumen Promedio Mensual']]

    etiquetas = [f'({cortes[i]}, {cortes[i + 1]}]' for i in range(len(cortes) - 1)]
    etiquetas[0] = etiquetas[0].replace("(", "[")

    datos_distribucion['Sección de Volumen Promedio Mensual'] = pd.cut(datos_distribucion['Volumen Promedio Mensual'],
                                                                        cortes,
                                                                        labels=etiquetas,
                                                                        include_lowest=True)
    
    advertencia = (not datos_distribucion[datos_distribucion.isnull().any(axis=1)].empty)

    datos_grafico = datos_distribucion.groupby('Sección de Volumen Promedio Mensual', as_index=False)['Volumen Promedio Mensual'].agg({'Volumen Acumulado':'sum'})
    datos_grafico['Volumen Porcentaje'] = datos_grafico['Volumen Acumulado'] / datos_grafico['Volumen Acumulado'].sum()

    del datos_grafico['Volumen Acumulado']

    return datos_distribucion, datos_grafico, advertencia


def mostrar_distribucion_volumen(datos_distribucion, datos_grafico, advertencia, rango_fechas):
    """
    docstring
    """
    fig = px.bar(datos_grafico,
                 x='Sección de Volumen Promedio Mensual',
                 y="Volumen Porcentaje")

    fig.update_layout(title_text='<b>Distribución del Volumen Mensual Embarcado</b>',
                        title_x=0.5,
                        title_y=0.97,
                        width=950,
                        height=600,
                        margin=dict(l=50,
                                    r=50,
                                    b=150,
                                    t=50,
                                    pad=5),
                        xaxis = dict(title='<b>Metros Cúbicos Mensuales</b>'),
                        yaxis = dict(title=f'<b>% de Productos por Rango</b>'))

    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(hovertemplate='Metros Cúbicos Mensuales: %{x} <br>% de Productos por Rango: %{y:.0%}')

    meses = {1: 'Enero',
                2: 'Febrero',
                3: 'Marzo',
                4: 'Abril',
                5: 'Mayo',
                6: 'Junio',
                7: 'Julio',
                8: 'Agosto',
                9: 'Septiembre',
                10: 'Octubre',
                11: 'Noviembre',
                12: 'Diciembre'} 

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU y Embarques<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year} al ' +
                            f'{rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                    xref='paper', yref='paper',
                    x=0.5, y=-0.27,
                    showarrow=False,
                    font={'size': 11})

    st.plotly_chart(fig)


@st.cache
def descargar_distribucion_volumen(datos_distribucion):
    """
    docstring
    """
    with pd.ExcelWriter(".\data\cedis_distribucion_volumen.xlsx") as writer:
        datos_distribucion.to_excel(writer, sheet_name="Distribución Volumen Mensual", index=False)