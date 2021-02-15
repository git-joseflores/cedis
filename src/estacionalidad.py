import pandas as pd
import streamlit as st
import plotly.express as px


def formatear_tiempo(formato, columna, es_inventario=False):
    """
    dosctring
    """
    if es_inventario:
        columna = pd.to_datetime(columna, format=formato)
    return columna.dt.strftime(formato)


@st.cache
def calcular_estacionalidad(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones):
    """
    docstring
    """
    tablas = [tabla_recibos,
              tabla_embarques,
              tabla_devoluciones,
              tabla_inventario]
    
    columnas_de_tiempo = ['Fecha Recibo',
                          'Fecha Embarque',
                          'Fecha Devolución',
                          'Mes']

    pivot_total = pd.DataFrame(columns=['Mes'])
    for tabla, columna_de_tiempo in zip(tablas, columnas_de_tiempo):
        tabla[columna_de_tiempo] = formatear_tiempo('%m', tabla[columna_de_tiempo], tabla is tabla_inventario)
        pivot_tabla = pd.pivot_table(tabla, index=columna_de_tiempo, aggfunc='sum').sort_index()
        pivot_total = pd.concat([pivot_total, pivot_tabla], axis=1)

    pivot_total['Mes'] = pd.to_datetime(pivot_total.index, format='%m').month_name(locale='es_MX.utf8')
    
    return pivot_total


def mostrar_estacionalidad(datos, cantidad, columna_tiempo):
    """
    docstring
    """
    datos_cols = [cantidad + ' Recibidas',
                  cantidad + ' Embarcadas', 
                  cantidad + ' Devueltas',
                  cantidad + ' de Inventario']
    
    titulo = 'Estacionalidad de ' + cantidad
    st.title(titulo)

    st.subheader('Periodo de Análisis:') 
    periodo_min = columna_tiempo.min()
    periodo_max = columna_tiempo.max()
    st.write(f'{(periodo_max - periodo_min).days} días.')

    st.table(datos.style.format('{:,.0f}', datos_cols))

    datos_fig = pd.melt(datos, id_vars='Mes', var_name='Tipo de Cantidad', value_name=cantidad)
    fig = px.bar(datos_fig,
                 x='Mes',
                 y=cantidad,
                 color='Tipo de Cantidad',
                 barmode='group',
                 labels={'Mes': '<b>Mes<b>',
                         cantidad: f'<b>{cantidad}<b>'},
                 hover_data={cantidad: ':,f'})
                 
    fig.update_layout(title_text=f'<b>{titulo}<b>', title_x=0.5)
                      
    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.38, y=0.3,
                              sizex=0.28, sizey=0.28,
                              xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Inventarios, Recibos, Embarques <br>' +
                            f'y Devoluciones del periodo {periodo_min.day}-{periodo_min.month}-{periodo_min.year} al ' +
                            f'{periodo_max.day}-{periodo_max.month}-{periodo_max.year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.25,
                       showarrow=False,
                       font={'size': 11})
                  
    st.plotly_chart(fig)

    st.subheader('Rotación de Inventario:')
    rot = datos[datos_cols[1]].sum() / datos[datos_cols[3]].sum()
    st.write(f'{rot:.3f}')
    
    st.subheader('DDI Promedio:')
    ddi = rot * 31
    st.write(f'{ddi:.3f}')
    
    st.subheader('% de Devoluciones:')
    dev_emb = datos[datos_cols[2]].sum() / datos[datos_cols[1]].sum() * 100
    st.write(f'{dev_emb:.3f}%')
    