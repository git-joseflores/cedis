import pandas as pd
import plotly.express as px
import streamlit as st


# @st.cache
def preparar_estacionalidad(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones, cantidad, fechas):
    """
    Se acotan las tablas de inventario, recibos, embarques y devoluciones de acuerdo a las cantidades y rango de fechas seleccionados.

            Parámetros:
                    tabla_inventario (Pandas DataFrame): Tabla correspondiente a la Foto de Inventarios.
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
              tabla_devoluciones,
              tabla_inventario]
    
    columnas_de_tiempo = ['Fecha de Recibo',
                          'Fecha de Embarque',
                          'Fecha de Devolución',
                          'Fecha de Inventario']

    columnas_de_cantidad = [cantidad + ' Recibidas',
                            cantidad + ' Embarcadas',
                            cantidad + ' Devueltas',
                            cantidad + ' de Inventario']

    # Lista de tablas acotadas, creada vacia.
    tablas_acotadas = []
    
    # Ciclar por las tablas, sus fechas y las cantidades seleccionadas.
    for tabla, columna_de_tiempo, columna_de_cantidad in zip(tablas, columnas_de_tiempo, columnas_de_cantidad):
        
        # Crear una nueva tabla alternativa que no incluye valores basura en la columna de cantidad y sus fechas.
        tabla_alternativa = tabla[(pd.to_numeric(tabla[columna_de_cantidad], errors='coerce').notna()) &
                                  (pd.to_datetime(tabla[columna_de_tiempo], errors='coerce').notna())]

        # Transformar los datos de fechas en su tipo correspondiente.
        tabla_alternativa[columna_de_tiempo] = pd.to_datetime(tabla_alternativa[columna_de_tiempo])

        # Acotar la tabla alternativa al rango de fechas obtenido.
        tabla_alternativa = tabla_alternativa.loc[(tabla_alternativa[columna_de_tiempo].dt.date >= fechas[0]) &
                                                  (tabla_alternativa[columna_de_tiempo].dt.date <= fechas[1]),
                                                 [columna_de_cantidad, columna_de_tiempo]]

        # Agregar la tabla alternatica a la lista de tablas acotadas.
        tablas_acotadas.append(tabla_alternativa)

    return tablas_acotadas, columnas_de_tiempo, columnas_de_cantidad, cantidad, fechas


def calcular_estacionalidad(tablas, columnas_de_tiempo, columnas_de_cantidad, cantidad, fechas, tipo):
    """
    Se calculan los datos agregados de cada una de las tablas segun su tipo de analisis de estacionalidad.

            Parámetros:
                    tablas (list of Pandas DataFrames): Lista de tablas acotadas.
                    columnas_de_tiempo (list of strings): Lista del nombre de las fechas en cada tabla.
                    columnas_de_cantidad (list of strings): Lista del nombre de las cantidades seleccionada en cada tabla.
                    cantidad (string): Texto que indica que cantidad se ha seleccionado, ya sea Unidades, Cajas o Tarimas.
                    fechas (tuple): Tupla de fechas que indican el rango seleccionado.
                    tipo (string): Texto que indica el tipo de analisis a efecturar, ya sea por Mes-Año o Semana-Año.

            Valor de Retorno:
                    pivot_total (Pandas DataFrame): Tabla con los datos agregados segun el tipo de analisis realizado.
                    cantidad (string): Texto que indica que cantidad se ha seleccionado, ya sea Unidades, Cajas o Tarimas.
                    tipo (string): Texto que indica el tipo de analisis a efecturar, ya sea por Mes-Año o Semana-Año.
    """
    if tipo == 'Por Mes':
        resumen = ['Mes', 'Año']
    else:
        resumen = ['Semana', 'Año']

    # Crear una tabla con columnas segun el tipo de analisis, ponerlas como index.
    pivot_total = pd.DataFrame(columns=resumen)
    pivot_total.set_index(resumen, inplace=True)

    # Ciclar por las tablas, sus fechas y las cantidades seleccionadas.
    for tabla, columna_de_tiempo, columna_de_cantidad in zip(tablas, columnas_de_tiempo, columnas_de_cantidad):
        # Segun el tipo de analisis, se obtiene el mes o la semana del año.
        if tipo == 'Por Mes':
            tabla['Mes'] = tabla[columna_de_tiempo].dt.month
        else:
            tabla['Semana'] = tabla[columna_de_tiempo].dt.isocalendar().week

        # Se obtiene tambien el año.
        tabla['Año'] = tabla[columna_de_tiempo].dt.year
        
        # Se agrupa la tabla segun su mes-año o semana-año, realiazndo una suma de las cantidades seleccionadas.
        pivot_tabla = tabla.groupby(resumen)[columna_de_cantidad].agg('sum')
        
        # Se añade la tabla en turno a la tabla de resultados total.
        pivot_total = pd.merge(pivot_total, pivot_tabla, how='outer', left_index=True, right_index=True)

    # Se rellena la tabla final con ceros si no existen datos y se resetea el index de mes-año o semana-año.
    pivot_total.fillna(0, inplace=True)
    pivot_total.reset_index(inplace=True)
    
    if tipo == 'Por Mes':
        # Si el analisis es por mes, se ordenan los datos por año y despues por mes.
        pivot_total.sort_values(['Año', 'Mes'], ascending=[True, True], inplace=True)

        # Se reemplazan los datos de mes numericos con sus valores escritos.
        pivot_total['Mes'].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', \
                                    'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], inplace=True)

        # Se crea una columna con el mes y el año por cada renglon.
        pivot_total['Mes-Año'] = pivot_total['Mes'] + '-' + pivot_total['Año'].astype(str)

        # Se eliminan datos que ya no se necesitan.
        del pivot_total['Mes']
        del pivot_total['Año']

        pivot_total = pivot_total.reindex(columns=['Mes-Año'] + columnas_de_cantidad)
    else:
        # Si el analisis es por semana, se ordenan los datos por año y despues por semana.
        pivot_total.sort_values(['Año', 'Semana'], ascending=[True, True], inplace=True)
        
        # Se crea una columna con la semana y el año por cada renglon.
        pivot_total['Semana-Año'] = pivot_total['Semana'].astype(str) + '-' + pivot_total['Año'].astype(str)

        # Se eliminan datos que ya no se necesitan.
        del pivot_total['Semana']
        del pivot_total['Año']

        pivot_total = pivot_total.reindex(columns=['Semana-Año'] + columnas_de_cantidad)
    
    return pivot_total, columnas_de_cantidad, cantidad, fechas, tipo


def mostrar_estacionalidad(datos, columnas_de_cantidad, cantidad, fechas, tipo):
    """
    Se muestran los datos de estacionalidad en forma grafica y con calculos especificos.

            Parámetros:
                    datos (Pandas DataFrame): Tabla que contiene los datos calculados de estacionalidad.
                    columnas_de_cantidad (list of strings): Lista del nombre de las cantidades seleccionada en cada tabla.
                    cantidad (string): Texto que indica que cantidad se ha seleccionado, ya sea Unidades, Cajas o Tarimas.
                    fechas (tuple): Tupla de fechas que indican el rango seleccionado.
                    tipo (string): Texto que indica el tipo de analisis a efecturar, ya sea por Mes-Año o Semana-Año.

            Valor de Retorno:
                    Ninguno.
    """
    # Se muestra el periodo de analisis en dias.
    st.subheader('Período de Análisis:')
    total_dias = (fechas[1] - fechas[0]).days + 1
    st.write(f"{total_dias} día{'s' if total_dias != 1 else ''}.")

    # Se formatean las tablas para contener comas y 1 cifra despues del punto.
    st.table(datos.style.format('{:,.1f}', columnas_de_cantidad))

    # Segun su tipo, se crea la grafica correspondiente a los datos agregados.
    if tipo == 'Por Mes':
        datos_fig = pd.melt(datos, id_vars='Mes-Año', var_name='Tipo de ' + cantidad, value_name=cantidad)
        fig = px.bar(datos_fig,
                     x='Mes-Año',
                     y=cantidad,
                     color='Tipo de ' + cantidad,
                     barmode='group',
                     labels={'Mes-Año': '<b>Mes-Año</b>',
                             cantidad: f'<b>{cantidad}</b>'})

        fig.update_traces(hovertemplate='Mes-Año: %{x}<br>'+ cantidad +': %{y:,.1f}')

    else:
        datos_fig = pd.melt(datos, id_vars='Semana-Año', var_name='Tipo de ' + cantidad, value_name=cantidad)
        fig = px.bar(datos_fig,
                     x='Semana-Año',
                     y=cantidad,
                     color='Tipo de ' + cantidad,
                     barmode='group',
                     labels={'Semana-Año': '<b>Semana-Año</b>',
                             cantidad: f'<b>{cantidad}</b>'})

        fig.update_traces(hovertemplate='Semana-Año: %{x}<br>'+ cantidad +': %{y:,.1f}')

    # Se configuran las dimensiones del grafico y su titulo.
    fig.update_layout(title_text=f'<b>Estacionalidad de {cantidad}</b>', 
                      title_x=0.5,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

    
    # Se crea la fuente de datos y se cambian los datos de mes de forma numerica a sus nombres en espanol.
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

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Inventarios, Recibos, Embarques y Devoluciones<br>' +
                            f'del periodo que comprende del {fechas[0].day} de {meses[fechas[0].month]} de {fechas[0].year} al ' +
                            f'{fechas[1].day} de {meses[fechas[1].month]} de {fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.35,
                       showarrow=False,
                       font={'size': 11})
    
    # Se muestra la figura
    st.plotly_chart(fig)

    # Se calculan datos especificos de estacionalidad.
    st.subheader('Rotación de Inventario:')
    rotacion = datos[cantidad + ' Embarcadas'].sum() / datos[cantidad + ' de Inventario'].sum()
    st.write(f'{rotacion:.2f}')
    
    st.subheader('DDI Promedio:')
    st.write(f'{rotacion * 31:.2f}')
    
    st.subheader('% de Devoluciones:')
    st.write(f'{datos[cantidad + " Devueltas"].sum() / datos[cantidad + " Embarcadas"].sum():.2%}')
    


    
# fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
#                         xref='paper', yref='paper',
#                         x=1.15, y=-0.25,
#                         sizex=0.17, sizey=0.17,
#                         xanchor='right', yanchor='bottom'))
