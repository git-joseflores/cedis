# Importando Librerias
import streamlit as st


from src.cargar_archivos import leer_archivo_a_tablas
from src.descargar_archivos import boton_de_descarga
from src.mostrar_errores import mostrar_error
# Análisis 1: Mostrar Tablas
from src.mostrar_tablas import mostrar_tablas
# Análisis 2: Estacionalidad
from src.estacionalidad import calcular_estacionalidad, mostrar_estacionalidad
# Análisis 3: Cargas Operativas
from src.cargas_operativas import calcular_cargas, mostrar_cargas
# Análisis 4: Resúmenes
from src.resumenes import calcular_resumenes, mostrar_resumenes
# Análisis 5: Clasificación ABC Ponderado
from src.clasificacion_abc import calcular_clasificacion_abc, mostrar_clasificacion_abc, mostrar_comparacion_absoluta, mostrar_comparacion_porcentual, calcular_abc_comparativo
# Análisis 6: Distribución de Volumen Mensual
from src.distribucion_volumen_mensual import calcular_distribucion_volumen, mostrar_distribucion_volumen
# Análisis 7: Distribución Incremental de Ordenes
from src.distribucion_incremental_ordenes import calcular_distribucion_ordenes, mostrar_distribucion_ordenes
# Análisis 8: Distribución Completa/Parcial/Mixta
from src.distribucion_comparacion import calcular_distribucion_comparacion, mostrar_distribucion_comparacion


# st.write(abc_volumen_conteo.astype('object'))

def main():
    """
    docstring
    """
    st.set_page_config(page_title='CEDIS', page_icon='img/icon.png')
    # st.markdown("""
    #             <style>
    #             table td:nth-child(1) {
    #                 display: none
    #             }
    #             table th:nth-child(1) {
    #                 display: none
    #             }
    #             </style>""",
    #             unsafe_allow_html=True)

    # hide_decoration_bar_style = '''
    #     <style>
    #         header {visibility: hidden;}
    #     </style>
    # '''
    # st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


    st.sidebar.title('CEDIS')
    archivo = st.sidebar.file_uploader('Selecciona el archivo a analizar:', type=['xlsx'])

    if archivo:
        lista_tablas, lista_errores = leer_archivo_a_tablas(archivo)
        if lista_errores:
            for error in lista_errores:
                mostrar_error(*error)
        else:
            tabla_sku, tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones = lista_tablas

            opciones_analisis = {1: 'Mostrar Tablas',
                                 2: 'Estacionalidad',
                                 3: 'Cargas Operativas',
                                 4: 'Resúmenes',
                                 5: 'Clasificación ABC Ponderado',
                                 6: 'Distribución de Volumen Mensual',
                                 7: 'Distribución Incremental de Ordenes',
                                 8: 'Distribución Completa/Parcial/Mixta'}
                                 
            analisis_seleccionado = st.sidebar.selectbox('Selecciona el Análisis a Ejecutar:',
                                                          options=list(opciones_analisis.items()),
                                                          index=0,
                                                          format_func=lambda opcion: opcion[1])

            if analisis_seleccionado[0] == 1:
                st.title(analisis_seleccionado[1])
                mostrar_tablas(tabla_sku.head(10),
                               tabla_inventario.head(10),
                               tabla_recibos.head(10),
                               tabla_embarques.head(10),
                               tabla_devoluciones.head(10))

            elif analisis_seleccionado[0] == 2:
                estacionalidad_cantidad = st.sidebar.radio('Selecciona las Cantidades a Usar:',
                                                           ['Unidades', 'Cajas', 'Tarimas'],
                                                           index=0)
                           
                mostrar_estacionalidad(calcular_estacionalidad(tabla_inventario[[estacionalidad_cantidad + ' de Inventario', 'Mes']],
                                                               tabla_recibos[[estacionalidad_cantidad + ' Recibidas', 'Fecha Recibo']],
                                                               tabla_embarques[[estacionalidad_cantidad + ' Embarcadas', 'Fecha Embarque']],
                                                               tabla_devoluciones[[estacionalidad_cantidad + ' Devueltas', 'Fecha Devolución']]),
                                       estacionalidad_cantidad,
                                       tabla_recibos['Fecha Recibo'])

            elif analisis_seleccionado[0] == 3:
                cargas_cantidad = st.sidebar.radio('Selecciona las Cantidades a Usar:',
                                                   ['Unidades', 'Cajas', 'Tarimas'],
                                                   index=0)

                cargas_periodo = st.sidebar.radio('Selecciona el Período de Tiempo a Usar:',
                                                  ['Turno', 'Horario'],
                                                  index=0)
                
                mostrar_cargas(calcular_cargas(tabla_recibos[[cargas_cantidad + ' Recibidas', cargas_periodo + ' Recibo']],
                                               tabla_embarques[[cargas_cantidad + ' Embarcadas', cargas_periodo + ' Embarque']],
                                               tabla_devoluciones[[cargas_cantidad + ' Devueltas', cargas_periodo + ' Devolución']],
                                               cargas_periodo),
                               cargas_cantidad,
                               cargas_periodo,
                               tabla_recibos['Fecha Recibo'])

            elif analisis_seleccionado[0] == 4:
                resumenes_lista_tablas = [tabla_recibos, tabla_embarques, tabla_devoluciones]
                resumenes_lista_tipos = ['Recibos', 'Embarques', 'Devoluciones']

                resumenes_tipo = st.sidebar.radio('Selecciona el Tipo de Datos a Usar:',
                                                  resumenes_lista_tipos,
                                                  index=0)

                resumenes_cantidad = st.sidebar.radio('Selecciona las Cantidades a Usar:',
                                                      ['Unidades', 'Cajas', 'Tarimas'],
                                                      index=0)

                resumenes_secciones = st.sidebar.number_input('Selecciona el Número de Secciones del Histograma:',
                                                              1,
                                                              20,
                                                              10)
                
                columnas_de_tiempo = ['Fecha Recibo',
                                      'Fecha Embarque',
                                      'Fecha Devolución']
                
                columnas_de_cantidades = [resumenes_cantidad + ' Recibidas',
                                          resumenes_cantidad + ' Embarcadas',
                                          resumenes_cantidad + ' Devueltas']

                for tabla, tipo, columna_de_tiempo, columna_de_cantidad in zip(resumenes_lista_tablas,
                                                                               resumenes_lista_tipos,
                                                                               columnas_de_tiempo,
                                                                               columnas_de_cantidades):
                    if resumenes_tipo == tipo:
                        mostrar_resumenes(*calcular_resumenes(tabla[[columna_de_cantidad, columna_de_tiempo]],
                                                             columna_de_tiempo,
                                                             tabla_recibos['Fecha Recibo']),
                                           columna_de_cantidad,
                                           tabla_recibos['Fecha Recibo'],
                                           resumenes_tipo,
                                           resumenes_secciones)

            elif analisis_seleccionado[0] == 5:
                abc_cantidad = st.sidebar.radio(
                    'Selecciona las Cantidades a Usar:',
                    ['Unidades', 'Cajas', 'Tarimas'],
                    index=0)

                abc_peso_volumen = st.sidebar.number_input('Selecciona el valor del ABC por Volumen:', 
                                                           min_value=0,
                                                           max_value=100,
                                                           value=50)

                abc_peso_variabilidad = st.sidebar.number_input('Selecciona el valor del ABC por Variabilidad:', 
                                                                min_value=0,
                                                                max_value=100,
                                                                value=30)

                abc_peso_frecuencia = st.sidebar.number_input('Selecciona el valor del ABC por Frecuencia:', 
                                                              min_value=0,
                                                              max_value=100,
                                                              value=20)

                df = mostrar_clasificacion_abc(*calcular_clasificacion_abc(tabla_embarques[['ID Producto', abc_cantidad + ' Embarcadas']],
                                                                      abc_cantidad,
                                                                      abc_peso_volumen,
                                                                      abc_peso_frecuencia,
                                                                      abc_peso_variabilidad),
                                                tabla_recibos['Fecha Recibo'])
                
                mostrar_comparacion_absoluta(tabla_sku[['Clave', 'Clasificación ABC Cliente']],
                                             df,
                                             tabla_recibos['Fecha Recibo'])

                mostrar_comparacion_porcentual(tabla_sku[['Clave', 'Clasificación ABC Cliente']],
                                               df,
                                               tabla_recibos['Fecha Recibo'])

                calcular_abc_comparativo(tabla_inventario[['ID Producto', abc_cantidad + ' de Inventario']],
                                         tabla_embarques[['ID Producto', abc_cantidad + ' Embarcadas']],
                                         df,
                                         abc_cantidad,
                                         tabla_recibos['Fecha Recibo'])

            elif analisis_seleccionado[0] == 6:
                distribucion_volumen_secciones = st.sidebar.number_input('Selecciona el Número de Secciones del Histograma:',
                                                                         1,
                                                                         20,
                                                                         7)
                
                mostrar_distribucion_volumen(calcular_distribucion_volumen(tabla_embarques[['ID Producto', 'Unidades Embarcadas', 'Fecha Embarque']],
                                                                           tabla_sku[['ID Producto', 'Volumen x Unidad']]),
                                             distribucion_volumen_secciones,
                                             tabla_recibos['Fecha Recibo'])

            elif analisis_seleccionado[0] == 7:
                contenedor_familia_1 = st.sidebar.beta_container()

                if st.sidebar.checkbox('Seleccionar Todas', key='familia_1'):
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacenes I':",
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist(),
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist())
                else:
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacenes I':",
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist())

                if distribucion_ordenes_familia_1:
                    contenedor_familia_2 = st.sidebar.beta_container()

                    if st.sidebar.checkbox('Seleccionar Todas', key='familia_2'):
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacenes II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist(),
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist())
                    else:
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacenes II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist())     

                    if distribucion_ordenes_familia_2:
                        contenedor_familia_3 = st.sidebar.beta_container()

                        if st.sidebar.checkbox('Seleccionar Todas', key='familia_3'):
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacenes III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist(),
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist())
                        else:
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacenes III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist())                        
                        
                        if distribucion_ordenes_familia_3:
                            mostrar_distribucion_ordenes(calcular_distribucion_ordenes(tabla_embarques[['ID Producto', 'Cajas Embarcadas']],
                                                                                       tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1) & \
                                                                                                     tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2) & \
                                                                                                     tabla_sku['Familia Almacén III'].isin(distribucion_ordenes_familia_3),
                                                                                                     ['ID Producto', 'Cajas x Tarima']]),
                                                         tabla_recibos['Fecha Recibo'])
                            
            elif analisis_seleccionado[0] == 8:
                contenedor_familia_1 = st.sidebar.beta_container()
                
                if st.sidebar.checkbox('Seleccionar Todas', key='familia_1'):
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacenes I':",
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist(),
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist())
                else:
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacenes I':",
                                                                                      tabla_sku['Familia Almacén I'].unique().tolist())

                if distribucion_ordenes_familia_1:
                    contenedor_familia_2 = st.sidebar.beta_container()

                    if st.sidebar.checkbox('Seleccionar Todas', key='familia_2'):
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacenes II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist(),
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist())
                    else:
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacenes II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia Almacén II'].unique().tolist())     

                    if distribucion_ordenes_familia_2:
                        contenedor_familia_3 = st.sidebar.beta_container()

                        if st.sidebar.checkbox('Seleccionar Todas', key='familia_3'):
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacenes III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist(),
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist())
                        else:
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacenes III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia Almacén III'].unique().tolist())                        
                        

                        if distribucion_ordenes_familia_3:
                            mostrar_distribucion_comparacion(calcular_distribucion_comparacion(tabla_embarques[['Pedido', 'ID Producto', 'Cajas Embarcadas']],
                                                                                               tabla_sku.loc[tabla_sku['Familia Almacén I'].isin(distribucion_ordenes_familia_1) & \
                                                                                                             tabla_sku['Familia Almacén II'].isin(distribucion_ordenes_familia_2) & \
                                                                                                             tabla_sku['Familia Almacén III'].isin(distribucion_ordenes_familia_3),
                                                                                                             ['ID Producto', 'Cajas x Tarima']]),
                                                             tabla_recibos['Fecha Recibo'])
                            
    else:
        st.success('Para hacer uso correcto de la herramienta, descarga la' + 
                   ' siguiente plantilla base y llena las columnas con los datos correspondientes:')

        st.markdown(boton_de_descarga('.\data\plantilla.xlsx',
                                      'plantilla.xlsx',
                                      'Descarga aquí la plantilla'),
                    unsafe_allow_html=True)


if __name__ == "__main__":
        main()
