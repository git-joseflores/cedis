import pandas as pd
import plotly.express as px
import streamlit as st


# @st.cache
def preparar_cargas(tabla_recibos, tabla_embarques, tabla_devoluciones, cantidad, fechas, periodo):
    """
    Se acotan las tablas de recibos, embarques y devoluciones de acuerdo a las cantidades y rango de fechas seleccionados.




            Parámetros:
                    tabla_recibos (Pandas DataFrame): Tabla correspondiente a la Base de Recibo.
                    tabla_embarques (Pandas DataFrame): Tabla correspondiente a la Base de Embarque.
                    tabla_devoluciones (Pandas DataFrame): Tabla correspondiente a la Base de Devoluciones.
                    cantidad (string): Texto que indica que cantidad se ha seleccionado, ya sea Unidades, Cajas o Tarimas. 
                    fechas (tuple): Tupla de fechas que indican el rango seleccionado.

            Valor de Retorno:
                    tablas_acotadas (list of Pandas DataFrames): Lista de tablas acotadas.
                    columnas_de_tiempo (list of strings): Lista del nombre de las fechas en cada tabla.
                    columnas_de_cantidad (list of strings): Lista del nombre de las cantidades seleccionada en cada tabla.
                    cantidad (string): Texto que indica que cantidad se ha seleccionado, ya sea Unidades, Cajas o Tarimas.
    """
    tablas = [tabla_recibos,
              tabla_embarques,
              tabla_devoluciones]
    
    columnas_de_cantidad = [cantidad + ' Recibidas',
                            cantidad + ' Embarcadas',
                            cantidad + ' Devueltas']

    columnas_de_fechas = ['Fecha de Recibo',
                          'Fecha de Embarque',
                          'Fecha de Devolución']
    if periodo == 'Horario':
        columnas_de_periodo = ['Horario de Recibo',
                               'Horario de Embarque',
                               'Horario de Devolución']
    else:
        columnas_de_periodo = ['Turno de Recibo',
                               'Turno de Embarque',
                               'Turno de Devolución']
        

    # Lista de tablas acotadas, creada vacia.
    tablas_acotadas = []
    
    # Ciclar por las tablas, sus fechas y las cantidades seleccionadas.
    for tabla, columna_de_cantidad, columna_de_fecha, columna_de_periodo in zip(tablas, columnas_de_cantidad, columnas_de_fechas, columnas_de_periodo):
        
        # Crear una nueva tabla alternativa que no incluye valores basura en la columna de cantidad y sus fechas.
        tabla_alternativa = tabla[(pd.to_numeric(tabla[columna_de_cantidad], errors='coerce').notna()) &
                                  (pd.to_datetime(tabla[columna_de_fecha], errors='coerce').notna())]

        # Transformar los datos de fechas en su tipo correspondiente.
        tabla_alternativa[columna_de_fecha] = pd.to_datetime(tabla_alternativa[columna_de_fecha])

        # Acotar la tabla alternativa al rango de fechas obtenido.
        tabla_alternativa = tabla_alternativa.loc[(tabla_alternativa[columna_de_fecha].dt.date >= fechas[0]) &
                                                  (tabla_alternativa[columna_de_fecha].dt.date <= fechas[1]),
                                                 [columna_de_cantidad, columna_de_periodo]]

        # Agregar la tabla alternatica a la lista de tablas acotadas.
        tablas_acotadas.append(tabla_alternativa)

    return tablas_acotadas, columnas_de_cantidad, cantidad, fechas, periodo


def calcular_cargas(tablas, columnas_de_cantidad, cantidad, fechas, periodo, cortes=[]):
    """
    docstring
    """
    if periodo == 'Horario':
        tablas[0]['Horario de Recibo'] = tablas[0]['Horario de Recibo'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                           .str.split(':', 1).str[0].str.strip().astype('int32')

        tablas[1]['Horario de Embarque'] = tablas[1]['Horario de Embarque'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                                   .str.split(':', 1).str[0].str.strip().astype('int32')

        tablas[2]['Horario de Devolución'] = tablas[2]['Horario de Devolución'].astype(str).str.split(' ').str[-1].str.strip() \
                                                                                                             .str.split(':', 1).str[0].str.strip().astype('int32')

    tablas[0].rename(columns={periodo + ' de Recibo': periodo}, inplace = True) 
    tablas[1].rename(columns={periodo + ' de Embarque': periodo}, inplace = True) 
    tablas[2].rename(columns={periodo + ' de Devolución': periodo}, inplace = True) 

    total_dias = (fechas[1] - fechas[0]).days

    pivot_total = pd.DataFrame(columns=[periodo])
    pivot_total.set_index([periodo], inplace=True)

    for tabla, cantidades in zip(tablas, columnas_de_cantidad):      
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
        
        pivot_total = pivot_total.groupby('Sección de Horario')[columnas_de_cantidad].agg('sum')
        pivot_total.reset_index(inplace=True)

    return pivot_total, advertencia, cantidad, fechas, periodo


def mostrar_cargas(datos, advertencia, cantidad, fechas, periodo):
    """
    docstring
    """
    if advertencia:
        st.warning('Advertencia: Existen datos en horarios no seleccionados.')
        
    st.subheader('Período de Análisis:')
    total_dias = (fechas[1] - fechas[0]).days + 1
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
    fig.update_layout(title_text=f'<b>Cargas Operativas de {cantidad}</b>', 
                      title_x=0.5,
                      xaxis={'type': 'category'},
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))
    
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
                            f'del periodo que comprende del {fechas[0].day} de {meses[fechas[0].month]} de {fechas[0].year}' +
                            f' al {fechas[1].day} de {meses[fechas[1].month]} de {fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.22,
                       showarrow=False,
                       font={'size': 11})
    
    st.plotly_chart(fig)





# fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
#                         xref='paper', yref='paper',
#                         x=1, y=-0.25,
#                         sizex=0.17, sizey=0.17,
#                         xanchor='right', yanchor='bottom'))