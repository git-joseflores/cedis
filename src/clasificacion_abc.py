import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff


@st.cache
def calcular_clasificacion_abc(datos, cantidad, peso_volumen, peso_frecuencia, peso_variablidad):
    """
    docstring
    """
    datos_abc_parcial = datos.groupby('ID del Producto', as_index=False)[cantidad + ' Embarcadas'].agg({
                              'volumen':'sum',
                              'frecuencia': 'count',
                              'promedio': 'mean',
                              'stdev': 'std'})

    datos_abc_parcial['variabilidad'] = datos_abc_parcial['stdev'] / datos_abc_parcial['promedio']
    del datos_abc_parcial['stdev']
    del datos_abc_parcial['promedio']


    datos_abc_parcial.sort_values(by=['volumen'], ascending=False, inplace=True)
    volumen_total = datos_abc_parcial['volumen'].sum()
    datos_abc_parcial['volumen_acumulado'] = datos_abc_parcial['volumen'].cumsum() / volumen_total

    rangos = [0, 0.8, 0.95, 0.99, np.inf]
    etiquetas = ['A', 'B', 'C', 'D']
    datos_abc_parcial['abc_volumen'] = pd.cut(datos_abc_parcial['volumen_acumulado'],
                                      bins=rangos,
                                      labels=etiquetas,
                                      precision=0)
    del datos_abc_parcial['volumen_acumulado']
    del datos_abc_parcial['volumen']


    datos_abc_parcial.sort_values(by=['frecuencia'], ascending=False, inplace=True)
    datos_abc_parcial['abc_frecuencia'] = pd.qcut(datos_abc_parcial['frecuencia'].rank(method='first'),
                                          q=4,
                                          labels=list(reversed(etiquetas)),
                                          precision=0)
    del datos_abc_parcial['frecuencia']


    datos_abc_parcial.sort_values(by=['variabilidad'], ascending=True, inplace=True)
    datos_abc_parcial['abc_variablidad']= pd.qcut(datos_abc_parcial['variabilidad'].rank(method='first'),
                                          q=4,
                                          labels=etiquetas,
                                          precision=0)
    del datos_abc_parcial['variabilidad']

    datos_abc_final = datos_abc_parcial.replace(['A', 'B', 'C', 'D'], [4, 3, 2, 1])
    datos_abc_final['puntuacion'] = datos_abc_final['abc_volumen'] * peso_volumen + \
                                    datos_abc_final['abc_frecuencia'] * peso_frecuencia + \
                                    datos_abc_final['abc_variablidad'] * peso_variablidad

    del datos_abc_final['abc_volumen']
    del datos_abc_final['abc_frecuencia']
    del datos_abc_final['abc_variablidad']

    datos_abc_final.sort_values(by=['puntuacion'], ascending=False, inplace=True)
    puntuacion_total = datos_abc_final['puntuacion'].sum()
    datos_abc_final['puntuacion_acumulada'] = datos_abc_final['puntuacion'].cumsum() / puntuacion_total

    datos_abc_final['Clasificación ABC Sintec'] = pd.cut(datos_abc_final['puntuacion_acumulada'],
                                                         bins=[0, 0.2, 0.5, 1],
                                                         labels=['A', 'B', 'C'],
                                                         precision=0)

    del datos_abc_final['puntuacion']
    del datos_abc_final['puntuacion_acumulada']

    return datos_abc_parcial, datos_abc_final


def mostrar_clasificacion_abc(datos_parciales, datos_finales, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    lista_analisis = [(datos_parciales, 'abc_volumen', 'Clasificación ABC por Volumen', True),
                      (datos_parciales, 'abc_variablidad', 'Clasificación ABC por Variabilidad', True),
                      (datos_parciales, 'abc_frecuencia', 'Clasificación ABC por Frecuencia', False),
                      (datos_finales, 'Clasificación ABC Sintec', 'Clasificación ABC Ponderada', True)]

    for datos, columna, analisis, orden in lista_analisis:
        columna_conteo = datos[columna].value_counts()\
                        .reset_index().rename(columns={"index": "Categoría", columna: "Conteo"})\
                        .sort_values(by=['Categoría'], ascending=orden)

        fig = px.bar(columna_conteo,
                     x='Categoría',
                     y='Conteo',
                     color='Categoría',
                     labels={'Categoría': '<b>Categoría<b>',
                             'Conteo': '<b>Conteo<b>'})

        fig.update_layout(title_text=f'<b>{analisis}<b>', title_x=0.5)
        
        fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                                  xref='paper', yref='paper',
                                  x=1.14, y=-0.15,
                                  sizex=0.2, sizey=0.2,
                                  xanchor='right', yanchor='bottom'))

        fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Embarques<br>' +
                                f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                                f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                           xref='paper', yref='paper',
                           x=0.5, y=-0.27,
                           showarrow=False,
                           font={'size': 11})

        st.plotly_chart(fig)

    return datos_finales


def mostrar_comparacion_absoluta(datos_cliente, datos_sintec, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    datos_juntos = pd.merge(datos_cliente,
                            datos_sintec,
                            on='ID del Producto',
                            how='outer')

    tabla_confusion = pd.crosstab(datos_juntos['Clasificación ABC Sintec'],
                                  datos_juntos['Clasificación ABC del Cliente'],
                                  rownames=['Sintec'],
                                  colnames=['Cliente'],
                                  margins=True)
    
    valores_confusion = list(reversed(tabla_confusion.values.tolist()))
    valores_confusion_texto = [[f'{valor}' for valor in sublista] for sublista in valores_confusion]

    fig = ff.create_annotated_heatmap(valores_confusion,
                                      x=list(['A', 'B', 'C', 'Todo']),
                                      y=list(reversed(['A', 'B', 'C', 'Todo'])),
                                      annotation_text=valores_confusion_texto,
                                      colorscale='blues')
    
    fig.update_layout(title_text='<b>Clasificación ABC Sintec vs Clasificación ABC Cliente</b>',
                      title_x=0.5,
                      title_y=0.97,
                      xaxis = dict(title='<b>Cliente</b>'),
                      yaxis = dict(title='<b>Sintec</b>'))

    # add custom xaxis title
    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=0.5,
                            y=-0.15,
                            showarrow=False,
                            text="",
                            xref="paper",
                            yref="paper"))

    # add custom yaxis title
    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=-0.35,
                            y=0.5,
                            showarrow=False,
                            text="",
                            textangle=-90,
                            xref="paper",
                            yref="paper"))

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                                xref='paper', yref='paper',
                                x=1.14, y=-0.15,
                                sizex=0.2, sizey=0.2,
                                xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.17,
                        showarrow=False,
                        font={'size': 11})

    # add colorbar
    fig['data'][0]['showscale'] = True
    
    st.plotly_chart(fig)


def mostrar_comparacion_porcentual(datos_cliente, datos_sintec, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    datos_juntos = pd.merge(datos_cliente,
                            datos_sintec,
                            on='ID del Producto',
                            how='outer')

    tabla_confusion = pd.crosstab(datos_juntos['Clasificación ABC Sintec'],
                                  datos_juntos['Clasificación ABC del Cliente'],
                                  rownames=['Sintec'],
                                  colnames=['Cliente'],
                                  margins=True)
    
    valores_confusion = list(reversed(tabla_confusion.values.tolist()))
    valores_confusion = [[valor / valores_confusion[0][3] * 100 for valor in sublista] for sublista in valores_confusion]
    valores_confusion_texto = [[f'{valor:.2f}%' for valor in sublista] for sublista in valores_confusion]

    fig = ff.create_annotated_heatmap(valores_confusion,
                                      x=list(['Cliente A', 'Cliente B', 'Cliente C', 'Todo']),
                                      y=list(reversed(['Sintec A', 'Sintec B', 'Sintec C', 'Todo'])),
                                      annotation_text=valores_confusion_texto,
                                      colorscale='blues',
                                      hoverinfo='z')
    
    fig.update_layout(title_text='<b>Clasificación ABC Sintec vs Clasificación ABC Cliente</b>',
                      title_x=0.5,
                      title_y=0.97,
                      xaxis = dict(title='<b>Cliente</b>'),
                      yaxis = dict(title='<b>Sintec</b>'))

    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=0.5,
                            y=-0.15,
                            showarrow=False,
                            text="",
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="black",size=14),
                            x=-0.35,
                            y=0.5,
                            showarrow=False,
                            text="",
                            textangle=-90,
                            xref="paper",
                            yref="paper"))

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                                xref='paper', yref='paper',
                                x=1.14, y=-0.15,
                                sizex=0.2, sizey=0.2,
                                xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.17,
                        showarrow=False,
                        font={'size': 11})

    fig['data'][0]['showscale'] = True
    
    st.plotly_chart(fig)


def calcular_abc_comparativo(datos_inventario, datos_embarques, df, cantidad, columna_tiempo):
    """
    docstring
    """
    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    datos_comparativo_inventario = datos_inventario.groupby('ID del Producto', as_index=False)[cantidad + ' de Inventario'].agg({'Suma Inventario':'sum'})
    datos_comparativo_embarque = datos_embarques.groupby('ID del Producto', as_index=False)[cantidad + ' Embarcadas'].agg({'Suma Embarque':'sum'})


    datos_comparativo_inventario = pd.merge(datos_comparativo_inventario,
                                           df,
                                           on='ID del Producto',
                                           how='outer').fillna('C')

    datos_comparativo_inventario.columns = ['ID del Producto', 'Suma Inventario', 'ABC']
   
   
    datos_comparativo_embarque = pd.merge(datos_comparativo_embarque,
                                           df,
                                           on='ID del Producto',
                                           how='outer').fillna('C')
    datos_comparativo_embarque.columns = ['ID del Producto', 'Suma Embarque', 'ABC']
   

    datos_comparativo_inventario = datos_comparativo_inventario.groupby('ABC', as_index=False)['Suma Inventario'].agg({' Inventario': 'sum'})
    datos_comparativo_inventario['Inventario'] = \
        datos_comparativo_inventario[' Inventario'] / datos_comparativo_inventario[' Inventario'].sum()
   
    datos_comparativo_embarque = datos_comparativo_embarque.groupby('ABC', as_index=False)['Suma Embarque'].agg({' Embarques': 'sum'})
    datos_comparativo_embarque['Embarques'] = \
        datos_comparativo_embarque[' Embarques'] / datos_comparativo_embarque[' Embarques'].sum()
  
    datos_comparativo = pd.merge(datos_comparativo_embarque,
                                 datos_comparativo_inventario,
                                 on='ABC',
                                 how='outer')

    # st.write(datos_comparativo.astype('object'))



    fig = px.bar(datos_comparativo,
                 x='ABC',
                 y=[' Embarques', ' Inventario'],
                 barmode='group',
                 labels={'ABC': '<b>Clasificación<b>',
                         'value': f'<b>{cantidad}<b>'},
                #  hover_data={'': ':,.0f'}
                 )

    
    fig.update_layout(title_text=f'<b>ABC Comparativo<b>', title_x=0.5)
    fig.update_layout(legend_title_text='')
    fig.update_yaxes(tickformat=",.0f")
    
    fig.update_traces(hovertemplate='Clasificación: %{x} <br>'+cantidad+': %{y:,.0f}')


    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.25, y=0.5,
                              sizex=0.2, sizey=0.2,
                              xanchor='right', yanchor='top'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU, Inventarios y Embarques<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.27,
                        showarrow=False,
                        font={'size': 11})

    st.plotly_chart(fig)



    fig = px.bar(datos_comparativo,
                 x='ABC',
                 y=['Embarques', 'Inventario'],
                 barmode='group',
                 labels={'ABC': '<b>Clasificación<b>',
                         'value': '<b>Porcentaje<b>'})

    fig.update_layout(legend_title_text='')
    # fig.update_layout(showlegend=False)
    fig.update_yaxes(tickformat=".0%")

    fig.update_traces(hovertemplate='Clasificación: %{x} <br>Porcentaje: %{y:.2%}')

    fig.update_layout(title_text=f'<b>ABC Comparativo<b>', title_x=0.5)
    

    fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
                              xref='paper', yref='paper',
                              x=1.25, y=0.5,
                              sizex=0.2, sizey=0.2,
                              xanchor='right', yanchor='top'))

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                             xref='paper', yref='paper',
    #                             x=1.14, y=-0.15,
    #                             sizex=0.2, sizey=0.2,
    #                             xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU, Inventarios y Embarques<br>' +
                            f'del periodo {tiempo_min.day}-{tiempo_min.month}-{tiempo_min.year} al ' +
                            f'{tiempo_max.day}-{tiempo_max.month}-{tiempo_max.year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.26,
                        showarrow=False,
                        font={'size': 11})

    st.plotly_chart(fig)    