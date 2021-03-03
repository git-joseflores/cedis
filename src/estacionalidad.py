import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache
def calcular_estacionalidad(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones, cantidad, tipo):
    """
    docstring
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

    if tipo == 'Por Mes':
        resumen = ['Mes', 'Año']
    else:
        resumen = ['Semana', 'Año']

    pivot_total = pd.DataFrame(columns=resumen)
    pivot_total.set_index(resumen, inplace=True)

    for tabla, columna_de_tiempo, columna_de_cantidad in zip(tablas, columnas_de_tiempo, columnas_de_cantidad):    
        if tipo == 'Por Mes':
            tabla['Mes'] = tabla[columna_de_tiempo].dt.month
        else:
            tabla['Semana'] = tabla[columna_de_tiempo].dt.isocalendar().week

        tabla['Año'] = tabla[columna_de_tiempo].dt.year

        pivot_tabla = tabla.groupby(resumen)[columna_de_cantidad].agg('sum')
        pivot_total = pd.merge(pivot_total, pivot_tabla, how='outer', left_index=True, right_index=True)

    pivot_total.fillna(0, inplace=True)
    pivot_total.reset_index(inplace=True)
    
    if tipo == 'Por Mes':
        pivot_total.sort_values(['Año', 'Mes'], ascending=[True, True], inplace=True)
        pivot_total['Mes'].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', \
                                    'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'], inplace=True)
        pivot_total['Mes-Año'] = pivot_total['Mes'] + '-' + pivot_total['Año'].astype(str)

        del pivot_total['Mes']
        del pivot_total['Año']

        pivot_total = pivot_total.reindex(columns=['Mes-Año'] + columnas_de_cantidad)
    else:
        pivot_total.sort_values(['Año', 'Semana'], ascending=[True, True], inplace=True)
        pivot_total['Semana-Año'] = pivot_total['Semana'].astype(str) + '-' + pivot_total['Año'].astype(str)

        del pivot_total['Semana']
        del pivot_total['Año']

        pivot_total = pivot_total.reindex(columns=['Semana-Año'] + columnas_de_cantidad)
    
    return pivot_total


def mostrar_estacionalidad(datos, cantidad, rango_fechas, tipo):
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
    total_dias = (rango_fechas[1] - rango_fechas[0]).days + 1
    st.write(f"{total_dias} día{'s' if total_dias != 1 else ''}.")

    st.table(datos.style.format('{:,.1f}', datos_cols))

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

    fig.update_layout(title_text=f'<b>{titulo}</b>', 
                      title_x=0.5,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

        
    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                         xref='paper', yref='paper',
    #                         x=1.15, y=-0.25,
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

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Inventarios, Recibos, Embarques y Devoluciones<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year} al ' +
                            f'{rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.35,
                       showarrow=False,
                       font={'size': 11})
                  
    st.plotly_chart(fig)

    st.subheader('Rotación de Inventario:')
    rotacion = datos[cantidad + ' Embarcadas'].sum() / datos[cantidad + ' de Inventario'].sum()
    st.write(f'{rotacion:.2f}')
    
    st.subheader('DDI Promedio:')
    st.write(f'{rotacion * 31:.2f}')
    
    st.subheader('% de Devoluciones:')
    st.write(f'{datos[cantidad + " Devueltas"].sum() / datos[cantidad + " Embarcadas"].sum():.2%}')
    