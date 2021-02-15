import pandas as pd
import streamlit as st
import plotly.express as px


@st.cache
def calcular_distribucion_comparacion(datos_embarques, datos_sku):
    """
    docstring
    """
    datos_ordenes = pd.merge(datos_embarques,
                             datos_sku,
                             on='ID Producto',
                             how='inner')

    datos_ordenes['Tarimas al 100%'] = datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']
    datos_ordenes['Completitud en Tarimas Incompletas'] = datos_ordenes['Cajas Embarcadas'] / datos_ordenes['Cajas x Tarima'] - datos_ordenes['Cajas Embarcadas'] // datos_ordenes['Cajas x Tarima']

    datos_ordenes['Tarimas Completas'] = (datos_ordenes['Tarimas al 100%'] != 0) & (datos_ordenes['Completitud en Tarimas Incompletas'] == 0)
    datos_ordenes['Tarimas Incompletas'] = (datos_ordenes['Tarimas al 100%'] == 0) & (datos_ordenes['Completitud en Tarimas Incompletas'] != 0)
    datos_ordenes['Tarimas Mixtas'] = (datos_ordenes['Tarimas Completas'] == 0) & (datos_ordenes['Tarimas Incompletas'] == 0)

    datos_pedidos = datos_ordenes.groupby('Pedido', as_index=False)['Pedido', 'Tarimas Completas', 'Tarimas Incompletas', 'Tarimas Mixtas'].agg(sum)
    datos_pedidos['Pedidos Completos'] = (datos_pedidos['Tarimas Completas'] != 0) & (datos_pedidos['Tarimas Incompletas'] == 0) & (datos_pedidos['Tarimas Mixtas'] == 0)
    datos_pedidos['Pedidos Incompletos'] = (datos_pedidos['Tarimas Completas'] == 0) & (datos_pedidos['Tarimas Incompletas'] != 0) & (datos_pedidos['Tarimas Mixtas'] == 0)
    datos_pedidos['Pedidos Mixtos'] = (datos_pedidos['Pedidos Completos'] == 0) & (datos_pedidos['Pedidos Incompletos'] == 0) 

    datos_dict = {'Tipo': ['Completos', 'Incompletos', 'Mixtos'],
                  'Tarimas': [datos_ordenes['Tarimas Completas'].sum(), datos_ordenes['Tarimas Incompletas'].sum(), datos_ordenes['Tarimas Mixtas'].sum()],
                  'Pedidos': [datos_pedidos['Pedidos Completos'].sum(), datos_pedidos['Pedidos Incompletos'].sum(), datos_pedidos['Pedidos Mixtos'].sum()]}

    datos = pd.DataFrame(datos_dict)

    datos['Tarimas'] = datos['Tarimas'] / datos['Tarimas'].sum()
    datos['Pedidos'] = datos['Pedidos'] / datos['Pedidos'].sum()

    return datos



def mostrar_distribucion_comparacion(datos, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()
    
    fig = px.bar(datos,
                 x='Tipo',
                 y=['Tarimas', 'Pedidos'],
                 barmode='group',
                 labels={'Tipo': '<b>Tipo de Embarque<b>',
                         'value': f'<b>% de Conteo<b>'})
    
    
    fig.update_layout(title_text=f'<b>Comparación de Embarques Completos/Incompletos/Mixtos<b>',
                      title_x=0.5,
                      width=850,
                      height=600,
                      margin=dict(
                          l=50,
                          r=50,
                          b=150,
                          t=35,
                          pad=5))
    fig.update_yaxes(tickformat=".0%")
    
    fig.update_traces(hovertemplate='Tipo de Embarque: %{x} <br>% de Conteo: %{y:.0%}')

    fig.update_layout(legend_title_text='Tipo de Embarque')

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