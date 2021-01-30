import pandas as pd
import streamlit as st
import plotly.express as px


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

    periodo = tabla_recibos['Fecha Recibo'].max() - tabla_recibos['Fecha Recibo'].min()

    pivot_total = pd.DataFrame(columns=['Mes'])
    for tabla, columna_de_tiempo in zip(tablas, columnas_de_tiempo):
        tabla[columna_de_tiempo] = formatear_tiempo('%m', tabla[columna_de_tiempo], tabla is tabla_inventario)
        pivot_tabla = pd.pivot_table(tabla, index=columna_de_tiempo, aggfunc='sum').sort_index()
        pivot_total = pd.concat([pivot_total, pivot_tabla], axis=1)

    pivot_total['Mes'] = pd.to_datetime(pivot_total.index, format='%m').month_name(locale='es_MX.utf8')
    
    return periodo, pivot_total


def formatear_tiempo(formato, columna, es_inventario=False):
    """
    dosctring
    """
    if es_inventario:
        columna = pd.to_datetime(columna, format=formato)
    return columna.dt.strftime(formato)


def mostrar_estacionalidad(periodo, tabla, cantidad):
    """
    docstring
    """
    tabla_cols = [cantidad + ' Recibidas',
                  cantidad + ' Embarcadas', 
                  cantidad + ' Devueltas',
                  cantidad + ' de Inventario']
    
    titulo = 'Estacionalidad de ' + cantidad
    st.title(titulo)

    st.subheader('Periodo de Análisis:') 
    st.write(f'{periodo.days} días.')

    st.table(tabla.style.format('{:,.0f}', tabla_cols))

    datos_fig = pd.melt(tabla, id_vars='Mes', var_name='Tipo de Cantidad', value_name=cantidad)
    fig = px.bar(datos_fig,
                 x='Mes',
                 y=cantidad,
                 title='AAA',
                 color='Tipo de Cantidad',
                 barmode='group',
                 labels={'Mes': '<b>Mes<b>',
                         cantidad: f'<b>{cantidad}<b>'},
                 hover_data={cantidad: ':,f'})
                 
    fig.update_layout(title_text=f'<b>{titulo}<b>', title_x=0.42, title_y=0.87)
                      
    fig.add_layout_image(dict(source="https://sintec.com/wp-content/uploads/2015/09/sintec-logo.png",
                              xref='paper', yref='paper',
                              x=1.32, y=-0.15,
                              sizex=0.25, sizey=0.25,
                              xanchor='right', yanchor='bottom'))

    fig.add_annotation(text='Absolutely-positioned annotation',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.3,
                       showarrow=False)
                  
    st.plotly_chart(fig)

     