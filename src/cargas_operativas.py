import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache
def calcular_cargas(tabla_recibos, tabla_embarques, tabla_devoluciones, cantidad, periodo, rango_fechas, cortes=[]):
    """
    docstring
    """
    tablas = [tabla_recibos,
              tabla_embarques,
              tabla_devoluciones]

    columnas_de_cantidades = [cantidad + ' Recibidas',
                            cantidad + ' Embarcadas',
                            cantidad + ' Devueltas']

    if periodo == 'Horario':
        tabla_recibos['Horario de Recibo'] = tabla_recibos['Horario de Recibo'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                           .str.split(':', 1).str[0].str.strip().astype('int32')

        tabla_embarques['Horario de Embarque'] = tabla_embarques['Horario de Embarque'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                                   .str.split(':', 1).str[0].str.strip().astype('int32')

        tabla_devoluciones['Horario de Devolución'] = tabla_devoluciones['Horario de Devolución'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                                             .str.split(':', 1).str[0].str.strip().astype('int32')

    tabla_recibos.rename(columns={periodo + ' de Recibo': periodo}, inplace = True) 
    tabla_embarques.rename(columns={periodo + ' de Embarque': periodo}, inplace = True) 
    tabla_devoluciones.rename(columns={periodo + ' de Devolución': periodo}, inplace = True) 

    total_dias = (rango_fechas[1] - rango_fechas[0]).days

    pivot_total = pd.DataFrame(columns=[periodo])
    pivot_total.set_index([periodo], inplace=True)

    for tabla, cantidades in zip(tablas, columnas_de_cantidades):      
        pivot_tabla = tabla.groupby(periodo)[cantidades].agg('sum') / (total_dias + 1)
        pivot_total = pd.merge(pivot_total, pivot_tabla, how='outer', left_index=True, right_index=True)

    pivot_total.fillna(0, inplace=True)
    pivot_total.reset_index(inplace=True)

    advertencia = False
    if periodo == 'Horario':
        etiquetas = [f'({cortes[i]}, {cortes[i + 1]}]' for i in range(len(cortes) - 1)]
        etiquetas[0] = etiquetas[0].replace("(", "[")

        pivot_total['Sección de Horario'] = pd.cut(pivot_total[periodo],
                                                   cortes,
                                                   labels=etiquetas,
                                                   include_lowest=True)

        if not pivot_total[pivot_total.isnull().any(axis=1)].empty:
            advertencia = True
        
        pivot_total = pivot_total.groupby('Sección de Horario')[columnas_de_cantidades].agg('sum')
        pivot_total.reset_index(inplace=True)

    return pivot_total, advertencia


def mostrar_cargas(datos, advertencia, cantidad, periodo, rango_fechas):
    """
    docstring
    """
    titulo = 'Cargas Operativas de ' + cantidad + ' por ' + periodo
    st.title(titulo)

    if advertencia:
        st.warning('Advertencia: Existen datos en horarios no seleccionados.')
        
    st.subheader('Periodo de Análisis:')
    total_dias = (rango_fechas[1] - rango_fechas[0]).days + 1
    st.write(f"{total_dias} día{'s' if total_dias != 1 else ''}.")

    datos_cols = [cantidad + ' Recibidas',
                  cantidad + ' Embarcadas', 
                  cantidad + ' Devueltas']

    st.table(datos.astype('object').style.format('{:,.1f}', datos_cols))


    if periodo == 'Horario':
        periodo = 'Sección de Horario'

    datos_fig = pd.melt(datos, id_vars=periodo, var_name='Tipo de ' + cantidad, value_name=cantidad)
    fig = px.bar(datos_fig,
                 x=periodo,
                 y=cantidad,
                 color='Tipo de ' + cantidad,
                 barmode='group',
                 labels={periodo: f'<b>{periodo}</b>',
                         cantidad: f'<b>{cantidad}</b>'})
                     
    fig.update_traces(hovertemplate='' + periodo + ': %{x} <br>'+ cantidad +': %{y:,.1f}')    
    fig.update_layout(title_text=f'<b>{titulo}</b>', 
                      title_x=0.5,
                      xaxis={'type': 'category'},
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

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

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Recibos, Embarques y Devoluciones<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year}' +
                            f' al {rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.22,
                       showarrow=False,
                       font={'size': 11})
    
    st.plotly_chart(fig)
