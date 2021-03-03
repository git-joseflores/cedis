import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache
def calcular_distribucion_comparacion(datos_sku, datos_embarques):
    """
    docstring
    """
    datos_ordenes = pd.merge(datos_sku,
                             datos_embarques,
                             on='ID del Producto',
                             how='inner')

    datos_ordenes['Tarimas al 100%'] = datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes['Completitud en Tarimas Incompletas'] = datos_ordenes['Cajas Embarcadas'] / datos_ordenes['Cajas x Tarima'] - datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']

    datos_ordenes['Tarimas Completas'] = (datos_ordenes['Tarimas al 100%'] != 0) & (datos_ordenes['Completitud en Tarimas Incompletas'] == 0)
    datos_ordenes['Tarimas Incompletas'] = (datos_ordenes['Tarimas al 100%'] == 0) & (datos_ordenes['Completitud en Tarimas Incompletas'] != 0)
    datos_ordenes['Tarimas Mixtas'] = (datos_ordenes['Tarimas Completas'] == 0) & (datos_ordenes['Tarimas Incompletas'] == 0)

    datos_pedidos = datos_ordenes.groupby('Pedido', as_index=False)[['Pedido', 'Tarimas Completas', 'Tarimas Incompletas', 'Tarimas Mixtas']].agg(sum)
    datos_pedidos['Pedidos Completos'] = (datos_pedidos['Tarimas Completas'] != 0) & (datos_pedidos['Tarimas Incompletas'] == 0) & (datos_pedidos['Tarimas Mixtas'] == 0)
    datos_pedidos['Pedidos Incompletos'] = (datos_pedidos['Tarimas Completas'] == 0) & (datos_pedidos['Tarimas Incompletas'] != 0) & (datos_pedidos['Tarimas Mixtas'] == 0)
    datos_pedidos['Pedidos Mixtos'] = (datos_pedidos['Pedidos Completos'] == 0) & (datos_pedidos['Pedidos Incompletos'] == 0) 

    datos_dict = {'Tipo': ['Completos', 'Incompletos', 'Mixtos'],
                  'Tarimas': [datos_ordenes['Tarimas Completas'].sum(), datos_ordenes['Tarimas Incompletas'].sum(), datos_ordenes['Tarimas Mixtas'].sum()],
                  'Pedidos': [datos_pedidos['Pedidos Completos'].sum(), datos_pedidos['Pedidos Incompletos'].sum(), datos_pedidos['Pedidos Mixtos'].sum()]}

    datos = pd.DataFrame(datos_dict)

    datos['Líneas'] = datos['Tarimas'] / datos['Tarimas'].sum()
    datos['Pedidos'] = datos['Pedidos'] / datos['Pedidos'].sum()

    return datos



def mostrar_distribucion_comparacion(datos, rango_fechas):
    """
    docstring
    """
    fig = px.bar(datos,
                 x='Tipo',
                 y=['Líneas', 'Pedidos'],
                 barmode='group')
    

    fig.update_layout(title_text='<b>Comparación de Embarques Completos, Incompletos y Mixtos</b>',
                        title_x=0.5,
                        title_y=0.97,
                        width=950,
                        height=600,
                        margin=dict(l=50,
                                    r=50,
                                    b=150,
                                    t=50,
                                    pad=5),
                        xaxis = dict(title='<b>Tipo de Embarque</b>'),
                        yaxis = dict(title=f'<b>% de Distribución</b>'))

    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(hovertemplate='Tipo de Embarque: %{x} <br>% de Distribución: %{y:.0%}')
    fig.update_layout(legend_title_text='Tipo de Embarque')

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

    st.balloons()