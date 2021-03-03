import pandas as pd
import plotly.figure_factory as ff
import streamlit as st


def mostrar_comparacion_cliente_absoluta(datos):
    """
    docstring
    """
    tabla_confusion = pd.crosstab(datos['Clasificación ABC de Sintec'],
                                  datos['Clasificación ABC del Cliente'],
                                  rownames=['Sintec'],
                                  colnames=['Cliente'],
                                  margins=True,
                                  margins_name='Todo')
    
    texto_x = [f'{tabla_confusion.columns.name}: {valor_cliente}' for valor_cliente in tabla_confusion.columns]
    texto_y = [f'{tabla_confusion.index.name}: {valor_sintec}' for valor_sintec in tabla_confusion.index[::-1]]

    tabla_confusion.values[-1][-1] = sum(tabla_confusion.values[i][i] for i in range(3))
    valores_confusion = list(reversed(tabla_confusion.values))
    valores_confusion_texto = [[f'{valor:.1f}' for valor in sublista] for sublista in valores_confusion]

    fig = ff.create_annotated_heatmap(valores_confusion,
                                      x=texto_x,
                                      y=texto_y,
                                      annotation_text=valores_confusion_texto,
                                      colorscale='blues',
                                      showscale=True)
    
    fig.update_layout(title_text='<b>Clasificación ABC Sintec vs Clasificación ABC Cliente</b>',
                      title_x=0.5,
                      title_y=0.97,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  t=130,
                                  b=150,
                                  pad=5),
                      xaxis = dict(title='<b>Cliente</b>'),
                      yaxis = dict(title='<b>Sintec</b>'))

    fig.update_traces(hovertemplate='%{x}<br>%{y}<br>Cantidad de SKU: %{z:.1f}', name='')

    fig.add_annotation(dict(font=dict(color="black", size=14),
                            x=0.5,
                            y=-0.15,
                            showarrow=False,
                            text="",
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="black", size=14),
                            x=-0.35,
                            y=0.5,
                            showarrow=False,
                            text="",
                            textangle=-90,
                            xref="paper",
                            yref="paper"))

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                             xref='paper', yref='paper',
    #                             x=1.14, y=-0.15,
    #                             sizex=0.2, sizey=0.2,
    #                             xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.18,
                        showarrow=False,
                        font={'size': 11})
    
    st.plotly_chart(fig)


def mostrar_comparacion_cliente_porcentual(datos):
    """
    docstring
    """
    tabla_confusion = pd.crosstab(datos['Clasificación ABC de Sintec'],
                                  datos['Clasificación ABC del Cliente'],
                                  colnames=['Cliente'],
                                  rownames=['Sintec'],
                                  margins=True,
                                  margins_name='Todo',
                                  normalize='all')
    
    texto_x = [f'{tabla_confusion.columns.name}: {valor_cliente}' for valor_cliente in tabla_confusion.columns]
    texto_y = [f'{tabla_confusion.index.name}: {valor_sintec}' for valor_sintec in tabla_confusion.index[::-1]]

    tabla_confusion.values[-1][-1] = sum(tabla_confusion.values[i][i] for i in range(3))
    valores_confusion = [[valor * 100 for valor in sublista] for sublista in tabla_confusion.values]
    valores_confusion_texto = [[f'{valor * 100:.1f}%' for valor in sublista] for sublista in tabla_confusion.values]
    
    fig = ff.create_annotated_heatmap(list(reversed(valores_confusion)),
                                      x=texto_x,
                                      y=texto_y,
                                      annotation_text=list(reversed(valores_confusion_texto)),
                                      colorscale='blues',
                                      showscale=True)
    
    fig.update_layout(title_text='<b>Clasificación ABC Sintec vs Clasificación ABC Cliente</b>',
                      title_x=0.5,
                      title_y=0.97,
                      width=950,
                      height=600,
                      margin=dict(l=50,
                                  r=50,
                                  t=130,
                                  b=150,
                                  pad=5),
                      xaxis = dict(title='<b>Cliente</b>'),
                      yaxis = dict(title='<b>Sintec</b>'))

    fig.update_traces(hovertemplate='%{x}<br>%{y}<br>% de SKU: %{z:.1f}%', name='')

    fig.add_annotation(dict(font=dict(color="black", size=14),
                            x=0.5,
                            y=-0.15,
                            showarrow=False,
                            text="",
                            xref="paper",
                            yref="paper"))

    fig.add_annotation(dict(font=dict(color="black", size=14),
                            x=-0.35,
                            y=0.5,
                            showarrow=False,
                            text="",
                            textangle=-90,
                            xref="paper",
                            yref="paper"))

    # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
    #                             xref='paper', yref='paper',
    #                             x=1.14, y=-0.15,
    #                             sizex=0.2, sizey=0.2,
    #                             xanchor='right', yanchor='bottom'))

    fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.18,
                        showarrow=False,
                        font={'size': 11})
    
    st.plotly_chart(fig)
