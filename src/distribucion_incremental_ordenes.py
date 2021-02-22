import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache
def calcular_distribucion_ordenes(datos_embarques, datos_sku):
    """
    docstring
    """
    datos_ordenes = pd.merge(datos_embarques,
                             datos_sku,
                             on='ID del Producto',
                             how='inner')

    datos_ordenes['Tarimas al 100%'] = datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes['Completitud en Tarimas Incompletas'] = datos_ordenes['Cajas Embarcadas'] / datos_ordenes['Cajas x Tarima'] - datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes.loc[datos_ordenes['Completitud en Tarimas Incompletas'] == 0, 'Completitud en Tarimas Incompletas'] = 1
    
    datos_ordenes['Secciones'] = pd.cut(datos_ordenes['Completitud en Tarimas Incompletas'],
                                       [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1],
                                       include_lowest=True)

    datos_ordenes = datos_ordenes.groupby('Secciones', as_index=False)['Completitud en Tarimas Incompletas'].agg({'Conteo':'count'})

    datos_ordenes['Secciones'] = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1]
    datos_ordenes['% de Conteo'] = datos_ordenes['Conteo'] / datos_ordenes['Conteo'].sum()

    return datos_ordenes


def mostrar_distribucion_ordenes(datos, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    fig = px.bar(datos,
                 x='Secciones',
                 y="Conteo",
                 labels={'Secciones': f'<b>Secciones</b>',
                          'Conteo': f'<b>Conteo</b>'})


    fig.update_layout(title_text=f'<b>Distribución Incremental de Órdenes<b>',
                      title_x=0.5,
                      width=850,
                      height=600,
                      margin=dict(
                          l=50,
                          r=50,
                          b=150,
                          t=35,
                          pad=5))
    fig.update_yaxes(tickformat=",.0f")
    fig.update_xaxes(tickformat=".0%",
                     tickangle=45,
                     tick0=0.0,
                     dtick=0.05)
    
    fig.update_traces(hovertemplate='Sección: %{x:.0%}<br>Conteo: %{y:,.0f}')

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

    fig = px.bar(datos,
                 x='Secciones',
                 y='% de Conteo',
                 labels={'Secciones': f'<b>Secciones</b>',
                         '% de Conteo': f'<b>% de Conteo</b>'})


    fig.update_layout(title_text=f'<b>Distribución Incremental de Órdenes<b>',
                      title_x=0.5,
                      width=850,
                      height=600,
                      
                      margin=dict(
                          l=50,
                          r=50,
                          b=150,
                          t=35  ,
                          pad=5
                        ))
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(tickformat=".0%",
                     tickangle=45,
                     tick0=0.0,
                     dtick=0.05)
    
    fig.update_traces(hovertemplate='Sección: %{x:.0%}<br>Porcentaje de Conteo: %{y:.0%}')

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