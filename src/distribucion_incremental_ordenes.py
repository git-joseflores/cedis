import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache
def calcular_distribucion_ordenes(datos_sku, datos_embarques):
    """
    docstring
    """
    datos_ordenes = pd.merge(datos_sku,
                             datos_embarques,
                             on='ID del Producto',
                             how='inner')

    datos_ordenes['Tarimas al 100%'] = datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes['Completitud en Tarimas Incompletas'] = datos_ordenes['Cajas Embarcadas'] / datos_ordenes['Cajas x Tarima'] - datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes.loc[datos_ordenes['Completitud en Tarimas Incompletas'] == 0, 'Completitud en Tarimas Incompletas'] = 1
    
    datos_ordenes['Secciones'] = pd.cut(datos_ordenes['Completitud en Tarimas Incompletas'],
                                       [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1],
                                       labels=['0-5%', '5-10%', '10-15%', '15-20%', '20-25%', '25-30%', '30-35%', '35-40%', '40-45%', '45-50%',
                                               '50-55%', '55-60%', '60-65%', '65-70%', '70-75%', '75-80%', '80-85%', '85-90%', '90-95%', '95-100%'],
                                       include_lowest=True)

    datos_ordenes = datos_ordenes.groupby('Secciones', as_index=False)['Completitud en Tarimas Incompletas'].agg({'Conteo':'count'})

    datos_ordenes['% de Conteo'] = datos_ordenes['Conteo'] / datos_ordenes['Conteo'].sum()

    return datos_ordenes


def mostrar_distribucion_ordenes(datos, rango_fechas):
    """
    docstring
    """
    fig = px.bar(datos,
                 x='Secciones',
                 y="Conteo")

    fig.update_layout(title_text='<b>Distribución Incremental de Órdenes</b>',
                        title_x=0.5,
                        title_y=0.97,
                        width=950,
                        height=600,
                        margin=dict(l=50,
                                    r=50,
                                    b=150,
                                    t=50,
                                    pad=5),
                        xaxis = dict(title='<b>% de Completitud</b>'),
                        yaxis = dict(title=f'<b>Tarimas</b>'))

    fig.update_yaxes(tickformat=",.0f")
    fig.update_xaxes(tickangle=45,
                     tick0=0.0,
                     dtick=0.05)
    fig.update_traces(hovertemplate='% de Completitud: %{x}<br>Tarimas: %{y:,.0f}')

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                         xref='paper', yref='paper',
    #                         x=1, y=-0.25,
    #                         sizex=0.17, sizey=0.17,
    #                         xanchor='right', yanchor='bottom'))

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
                    x=0.5, y=-0.35,
                    showarrow=False,
                    font={'size': 11})


    st.plotly_chart(fig)



    fig = px.bar(datos,
                 x='Secciones',
                 y='% de Conteo')

    fig.update_layout(title_text='<b>Distribución Incremental de Órdenes</b>',
                        title_x=0.5,
                        title_y=0.97,
                        width=950,
                        height=600,
                        margin=dict(l=50,
                                    r=50,
                                    b=150,
                                    t=50,
                                    pad=5),
                        xaxis = dict(title='<b>% de Completitud</b>'),
                        yaxis = dict(title=f'<b>% de Tarimas</b>'))

    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(tickangle=45,
                     tick0=0.0,
                     dtick=0.05)
    fig.update_traces(hovertemplate='% de Completitud: %{x}<br>% de Tarimas: %{y:.0%}')


    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                         xref='paper', yref='paper',
    #                         x=1, y=-0.25,
    #                         sizex=0.17, sizey=0.17,
    #                         xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU y Embarques<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year} al ' +
                            f'{rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                    xref='paper', yref='paper',
                    x=0.5, y=-0.35,
                    showarrow=False,
                    font={'size': 11})

    st.plotly_chart(fig)