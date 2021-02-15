import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# @st.cache
def calcular_resumenes(datos, columna_de_tiempo, fechas):
    """
    docstring
    """
    index = pd.date_range(fechas.min(), fechas.max())    
    pivot_datos = pd.pivot_table(datos, index=columna_de_tiempo, aggfunc='sum').sort_index()
    pivot_datos.index = pd.DatetimeIndex(pivot_datos.index)
    pivot_datos = pivot_datos.reindex(index, fill_value=0)
    
    dict_resumen = {'Máximo': pivot_datos.max(),
                    'Mínimo': pivot_datos.min(),
                    'Promedio': pivot_datos.mean(),
                    'Desviación Estándar': pivot_datos.std()}

    tabla_resumen = pd.DataFrame.from_dict(dict_resumen)

    return pivot_datos, tabla_resumen

# def mostrar_resumenes(datos, cantidad, fecha, datos_completos, num_secciones):
def mostrar_resumenes(datos, resumen, cantidad, columna_tiempo, tipo, numero_de_secciones):
    """
    docstring
    """
    titulo = 'Resumen de ' + cantidad
    st.title(titulo)
    
    st.subheader('Periodo de Análisis:') 
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()
    tiempo_dias = (tiempo_max - tiempo_min).days
    st.write(f'{tiempo_dias} días.')

    st.table(resumen.style.format('{:,.0f}'))

    datos = datos.reset_index()

    fig = px.box(datos,
                 y=cantidad,
                 points="all",
                 labels={cantidad: f'<b>{cantidad}<b>'},
                 hover_data={cantidad: ':,.0f'})
                 
    fig.update_layout(title_text=f'<b>Box & Whisker de {cantidad}<b>', title_x=0.5)

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.14, y=-0.15,
                              sizex=0.2, sizey=0.2,
                              xanchor='right', yanchor='bottom'))
    
    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.15,
                       showarrow=False,
                       font={'size': 11})

    st.plotly_chart(fig)
    
    fig = px.line(datos,
                  x='index',
                  y=cantidad,
                  labels={'index': f'<b>{columna_tiempo.name}<b>',
                          cantidad: f'<b>{cantidad}<b>'},
                 hover_data={cantidad: ':,.0f'})
  
    fig.update_xaxes(tickformat="%d-%m-%Y")

    fig.update_layout(title_text=f'<b>Serie de Tiempo de {cantidad}<b>', title_x=0.5)

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.14, y=-0.15,
                              sizex=0.2, sizey=0.2,
                              xanchor='right', yanchor='bottom'))
        
    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.26,
                       showarrow=False,
                       font={'size': 11})

    st.plotly_chart(fig)


    secciones = np.linspace(datos[cantidad].min(), datos[cantidad].max(), numero_de_secciones + 1)
    datos['Secciones'] = pd.cut(datos[cantidad], secciones, include_lowest=True)
    acumulado = datos['Secciones'].value_counts()
    acumulado = acumulado.sort_index().to_frame().reset_index()
    acumulado.rename(columns={'index': 'Secciones', 'Secciones': 'Conteo'}, inplace=True)
    acumulado["Secciones"] = acumulado["Secciones"].astype("str")
    fig = px.bar(acumulado,
                 x='Secciones',
                 y="Conteo",
                 labels={'Secciones': '',
                          'Conteo': f'<b>Conteo<b>'},
                 hover_data={'Conteo': ':,.0f'})

    fig.update_layout(title_text=f'<b>Histograma de {cantidad}<b>', title_x=0.5, xaxis={'tickfont': {'size': 8}})

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.14, y=0.5,
                              sizex=0.13, sizey=0.13,
                              xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.3,
                       showarrow=False,
                       font={'size': 11})

    st.plotly_chart(fig)
