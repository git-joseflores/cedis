import pandas as pd
import plotly.express as px
from src.utilidades import checar_valores_vacios_columna, mostrar_error
import streamlit as st


def mostrar_comparacion_inventario(datos_sku, datos_inventario, datos_embarques, cantidad, operacion, ultima_foto, rango_fechas):
    """
    docstring
    """
    if ultima_foto:
        datos_inventario = datos_inventario.sort_values('Fecha de Inventario').groupby('ID del Producto').tail(1)

    # st.write(datos_inventario)
    sumatorias_inventario = datos_inventario.groupby('ID del Producto', as_index=False)\
                                            [cantidad + ' de Inventario']\
                                            .agg({'Suma de Inventarios por SKU': operacion})

    sumatorias_embarque = datos_embarques.groupby('ID del Producto', as_index=False)\
                                          [cantidad + ' Embarcadas']\
                                          .agg({'Suma de Embarques por SKU': operacion}) 

    # st.write(sumatorias_inventario)
    # st.write(sumatorias_embarque)
    sumatorias = pd.merge(datos_sku,
                          sumatorias_inventario,
                          on='ID del Producto',
                          how='outer').merge(sumatorias_embarque,
                                             on='ID del Producto',
                                             how='outer')

    # st.write(sumatorias)
    if checar_valores_vacios_columna(sumatorias['Clasificación ABC de Sintec']):
        mostrar_error(8)
    else:
        sumatorias.fillna(0, inplace=True)

        datos_comparativo = sumatorias.groupby('Clasificación ABC de Sintec', as_index=False)\
                                       [['Suma de Inventarios por SKU', 'Suma de Embarques por SKU']]\
                                       .agg({'Suma de Inventarios por SKU': 'sum', 'Suma de Embarques por SKU': 'sum'})

        datos_comparativo['Inventarios'] = \
                        datos_comparativo['Suma de Inventarios por SKU'] / datos_comparativo['Suma de Inventarios por SKU'].sum()

        datos_comparativo['Embarques'] = \
                        datos_comparativo['Suma de Embarques por SKU'] / datos_comparativo['Suma de Embarques por SKU'].sum()


        # st.write(datos_comparativo)
        fig = px.bar(datos_comparativo,
                     x='Clasificación ABC de Sintec',
                     y=['Embarques', 'Inventarios'],
                     barmode='group')
    
        fig.update_layout(title_text='<b>Comparativo de Clasificación ABC de Embarques vs Inventarios</b>',
                          title_x=0.5,
                          title_y=0.97,
                          width=950,
                          height=600,
                          legend_title_text=f'Tipo de {cantidad}',
                          margin=dict(l=50,
                                      r=50,
                                      b=150,
                                      t=50,
                                      pad=5),
                          xaxis = dict(title='<b>Clasificación ABC de Sintec</b>'),
                          yaxis = dict(title=f'<b>% de {cantidad}</b>'))

        fig.update_traces(hovertemplate='Clasificación: %{x} <br> % de ' + cantidad + ': %{y:.1%}')
        fig.update_yaxes(tickformat=".0%")


        # fig.add_layout_image(dict(source="https://raw.githubusercontent.com/git-joseflores/sintec/main/logo.png",
        #                           xref='paper', yref='paper',
        #                           x=1.25, y=0.5,
        #                           sizex=0.2, sizey=0.2,
        #                           xanchor='right', yanchor='top'))

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

        fig.add_annotation(text=f'Fuente: El gráfico se construye con información de SKU, Inventarios y Embarques<br>' +
                                f'del periodo que comprende del {rango_fechas[0].day} de {meses[rango_fechas[0].month]} de {rango_fechas[0].year} al ' +
                                f'{rango_fechas[1].day} de {meses[rango_fechas[1].month]} de {rango_fechas[1].year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.23,
                        showarrow=False,
                        font={'size': 11})

        st.plotly_chart(fig)
        