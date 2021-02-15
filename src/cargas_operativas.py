import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache
def calcular_cargas(tabla_recibos, tabla_embarques, tabla_devoluciones, periodo):
    """
    docstring
    """
    tablas = [tabla_recibos,
              tabla_embarques,
              tabla_devoluciones]

    columnas_de_tiempo = [periodo + ' Recibo',
                          periodo + ' Embarque',
                          periodo + ' Devolución']

    pivot_total = pd.DataFrame()
    for tabla, columna_de_tiempo in zip(tablas, columnas_de_tiempo):
        pivot_tabla = pd.pivot_table(tabla, index=columna_de_tiempo, aggfunc='sum').sort_index()
        pivot_total = pd.concat([pivot_total, pivot_tabla], axis=1)
        
    
    return pivot_total


def mostrar_cargas(datos, cantidad, periodo, columna_tiempo):
    """
    docstring
    """
    titulo = 'Cargas Operativas de ' + cantidad + ' por ' + periodo
    st.title(titulo)

    st.subheader('Periodo de Análisis:') 
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()
    tiempo_dias = (tiempo_max - tiempo_min).days
    st.write(f'{tiempo_dias} días.')

    datos_cols = [cantidad + ' Recibidas',
                  cantidad + ' Embarcadas', 
                  cantidad + ' Devueltas']
    datos.index.name = periodo
    datos = (datos / tiempo_dias).sort_index().reset_index()
    st.table(datos.style.format('{:,.0f}', datos_cols))

    datos_fig = pd.melt(datos, id_vars=periodo, var_name='Tipo de Cantidad', value_name=cantidad)
    fig = px.bar(datos_fig,
                 x=periodo,
                 y=cantidad,
                 color='Tipo de Cantidad',
                 barmode='group',
                 labels={periodo: f'<b>{periodo}<b>',
                         cantidad: f'<b>{cantidad}<b>'},
                 hover_data={cantidad: ':,.0f'})

    fig.update_layout(xaxis={'type': 'category'})
    fig.update_layout(title_text=f'<b>{titulo}<b>', title_x=0.5)
    
    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.38, y=0.3,
                              sizex=0.28, sizey=0.28,
                              xanchor='right', yanchor='bottom'))
    
    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Recibos, Embarques y Devoluciones <br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.25,
                       showarrow=False,
                       font={'size': 11})
                  
    st.plotly_chart(fig)
