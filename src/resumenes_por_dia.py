import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache
def calcular_resumenes(datos, minimo, maximo, tiempo, cantidad, fechas):
    """
    docstring
    """
    fechas_indice = pd.date_range(fechas[0], fechas[1])
    pivot_datos = datos.groupby(tiempo)[cantidad].agg('sum')
    pivot_datos.index = pd.DatetimeIndex(pivot_datos.index)
    pivot_datos = pivot_datos.reindex(fechas_indice, fill_value=0)

    resumen_general = {'Mínimo': [pivot_datos.min()],
                       'Máximo': [pivot_datos.max()],
                       'Promedio': [pivot_datos.mean()],
                       'Desviación Estándar': [pivot_datos.std()],
                       'Coeficiente de Variación': [pivot_datos.std() / pivot_datos.mean()]}

    tabla_general = pd.DataFrame.from_dict(resumen_general).fillna(0)

    pivot_datos = pivot_datos[(pivot_datos >= minimo) & (pivot_datos <= maximo)]
    
    resumen_acotado = {'Mínimo': [pivot_datos.min()],
                       'Máximo': [pivot_datos.max()],
                       'Promedio': [pivot_datos.mean()],
                       'Desviación Estándar': [pivot_datos.std()],
                       'Coeficiente de Variación': [pivot_datos.std() / pivot_datos.mean()]}

    tabla_acotada = pd.DataFrame.from_dict(resumen_acotado).fillna(0)

    return pivot_datos, tabla_general, tabla_acotada


def mostrar_resumenes(datos, resumen_general, resumen_acotada, tipo, tiempo, cantidad, rango_fechas, numero_secciones):
    """
    docstring
    """
    titulo = f'Resumen de {cantidad} por Día'
    st.title(titulo)
    
    st.markdown("<h3 style='text-align: center;'>Resumen Diario General</h3>",
                unsafe_allow_html=True)

    st.subheader('Periodo de Análisis:') 
    total_dias = (rango_fechas[1] - rango_fechas[0]).days + 1
    st.write(f"{total_dias} día{'s' if total_dias != 1 else ''}.")

    st.table(resumen_general.style.format('{:,.1f}'))


    st.markdown("<h3 style='text-align: center;'>Resumen Diario Acotado</h3>",
                unsafe_allow_html=True)

    st.subheader('Periodo de Análisis:') 
    total_dias = len(datos)
    st.write(f"{total_dias} día{'s' if total_dias != 1 else ''}.")

    st.table(resumen_acotada.style.format('{:,.1f}'))

    datos = datos.reset_index()
    fig = px.box(datos,
                 y=cantidad,
                 points="all",
                 labels={cantidad: f'<b>{cantidad}</b>'})
                 
    fig.update_traces(hovertemplate=cantidad +': %{y:,.1f}')    
    fig.update_layout(title_text=f'<b>Box & Whisker de {cantidad}</b>', 
                      title_x=0.5,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                           xref='paper', yref='paper',
    #                           x=1.14, y=-0.15,
    #                           sizex=0.2, sizey=0.2,
    #                           xanchor='right', yanchor='bottom'))

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

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year}' +
                            f' al {rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.15,
                       showarrow=False,
                       font={'size': 11})

    st.plotly_chart(fig)
    

    fig = px.line(datos,
                  x='index',
                  y=cantidad,
                  labels={'index': f'<b>{tiempo}</b>',
                          cantidad: f'<b>{cantidad}</b>'})
  

    fig.update_traces(hovertemplate=tiempo +': %{x} <br>'+ cantidad +': %{y:,.1f}')    
    fig.update_layout(title_text=f'<b>Serie de Tiempo de {cantidad}</b>',  
                      title_x=0.5,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

    fig.update_xaxes(tickformat="%d-%m-%Y")

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                           xref='paper', yref='paper',
    #                           x=1.14, y=-0.15,
    #                           sizex=0.2, sizey=0.2,
    #                           xanchor='right', yanchor='bottom'))
        
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

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
                            f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year}' +
                            f' al {rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                       xref='paper', yref='paper',
                       x=0.5, y=-0.22,
                       showarrow=False,
                       font={'size': 11})

    st.plotly_chart(fig)


    secciones = np.linspace(datos[cantidad].min(), datos[cantidad].max(), numero_secciones + 1)

    etiquetas = [f'({secciones[i]:,.1f}, {secciones[i + 1]:,.1f}]' for i in range(len(secciones) - 1)]
    etiquetas[0] = etiquetas[0].replace("(", "[")

    datos['Secciones'] = pd.cut(datos[cantidad],
                                secciones,
                                labels=etiquetas,
                                include_lowest=True)

    acumulado = datos['Secciones'].value_counts()
    acumulado = acumulado.sort_index().to_frame().reset_index()
    acumulado.rename(columns={'index': 'Secciones', 'Secciones': 'Conteo'}, inplace=True)
    acumulado["Secciones"] = acumulado["Secciones"].astype("str")

    fig = px.bar(acumulado,
                 x='Secciones',
                 y="Conteo",
                 labels={'Secciones': f'<b>Secciones de {cantidad}</b>',
                          'Conteo': f'<b>Conteo</b>'})

    fig.update_traces(hovertemplate='Sección de ' + cantidad +': %{x} <br>Conteo: %{y:,.1f}')
    fig.update_layout(title_text=f'<b>Histograma de {cantidad}</b>',
                      title_x=0.5,
                    #   xaxis={'tickfont': {'size': 8}},
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  b=150,
                                  t=35,
                                  pad=5))

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                           xref='paper', yref='paper',
    #                           x=1.14, y=0.5,
    #                           sizex=0.13, sizey=0.13,
    #                           xanchor='right', yanchor='bottom'))

    # fig.add_annotation(text=f'Fuente: El gráfico se construye con información de {tipo}<br>' +
    #                         f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year}' +
    #                         f' al {rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
    #                    xref='paper', yref='paper',
    #                    x=0.5, y=-0.3,
    #                    showarrow=False,
    #                    font={'size': 11})

    st.plotly_chart(fig)
