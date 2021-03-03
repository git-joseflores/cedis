import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


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

    datos_abc_final['Clasificación ABC de Sintec'] = pd.cut(datos_abc_final['puntuacion_acumulada'],
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

    tiempo_min = columna_tiempo.min()
    tiempo_max = columna_tiempo.max()

    lista_analisis = [(datos_parciales, 'abc_volumen', 'Clasificación ABC por Volumen', True),
                      (datos_parciales, 'abc_variablidad', 'Clasificación ABC por Variabilidad', True),
                      (datos_parciales, 'abc_frecuencia', 'Clasificación ABC por Frecuencia', False),
                      (datos_finales, 'Clasificación ABC de Sintec', 'Clasificación ABC Ponderada', True)]

    for datos, columna, analisis, orden in lista_analisis:
        columna_conteo = datos[columna].value_counts()\
                        .reset_index().rename(columns={"index": "Categoría", columna: "Conteo"})\
                        .sort_values(by=['Categoría'], ascending=orden)

        fig = px.bar(columna_conteo,
                     x='Categoría',
                     y='Conteo',
                     color='Categoría',
                     labels={'Categoría': '<b>Categoría</b>',
                             'Conteo': '<b>Cantidad de SKU</b>'})

        fig.update_traces(hovertemplate='Categoría: %{x}<br>Cantidad de SKU: %{y:,.0f}')

        fig.update_layout(title_text=f'<b>{analisis}</b>', 
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

        fig.add_annotation(text=f'Fuente: El gráfico se construye con información de Embarques<br>' +
                                f'del periodo que comprende del {tiempo_min.day} de {meses[tiempo_min.month]} de {tiempo_min.year}' +
                                f' al {tiempo_max.day} de {meses[tiempo_max.month]} de {tiempo_max.year}.',
                        xref='paper', yref='paper',
                        x=0.5, y=-0.22,
                        showarrow=False,
                        font={'size': 11})

        st.plotly_chart(fig)


@st.cache
def descargar_clasificacion_abc(datos_abc_sintec, datos_sku, datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    datos_sku_total = pd.merge(datos_sku, datos_abc_sintec, how='outer', on='ID del Producto', suffixes=('', '_y'))
    datos_sku_total['Clasificación ABC de Sintec'] = datos_sku_total['Clasificación ABC de Sintec_y'].astype('string').fillna('SR')
    del datos_sku_total['Clasificación ABC de Sintec_y']
    
    # st.write(datos_inventario['Fecha de Inventario'])
    # st.write(datos_inventario['Fecha de Inventario'].dtype)
    # datos = pd.to_datetime(datos_inventario['Fecha de Inventario'])
    # datos = datos.dt.strftime('%m/%d/%Y')
    # st.write(datos)
    # st.write(datos.dtype)

    # st.write(datos_inventario['Horario de Inventario'])
    # st.write(datos_inventario['Horario de Inventario'].dtype)
    # datos = datos_inventario['Horario de Inventario'].astype(str).str.split(' ').str[-1].str.strip()
    # st.write(datos)
    # st.write(datos.dtype)
    

    with pd.ExcelWriter(".\data\cedis_abc.xlsx") as writer:
        datos_sku_total.to_excel(writer, sheet_name="Información SKU", index=False)
        datos_inventario.to_excel(writer, sheet_name="Foto de Inventarios", index=False)
        datos_recibos.to_excel(writer, sheet_name="Base de Recibo", index=False)
        datos_embarques.to_excel(writer, sheet_name="Base de Embarque", index=False)
        datos_devoluciones.to_excel(writer, sheet_name="Base de Devoluciones", index=False)
