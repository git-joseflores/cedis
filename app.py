# Importando Librerias
import streamlit as st

from src.cargar_archivos import leer_archivo_a_tablas
from src.descargar_archivos import boton_de_descarga
from src.mostrar_errores import mostrar_error
# Analisis 1: Mostrar Tablas
from src.mostrar_tablas import mostrar_tablas
# Analisis 2: Estacionalidad
from src.estacionalidad import calcular_estacionalidad, mostrar_estacionalidad


def main():
    """
    docstring
    """
    st.set_page_config(page_title='CEDIS', page_icon='img/icon.png')

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
                                 5: 'Clasificación ABC Ponderado'}
                                 
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
                           
                mostrar_estacionalidad(*calcular_estacionalidad(tabla_inventario[[estacionalidad_cantidad + ' de Inventario', 'Mes']],
                                                                tabla_recibos[[estacionalidad_cantidad + ' Recibidas', 'Fecha Recibo']],
                                                                tabla_embarques[[estacionalidad_cantidad + ' Embarcadas', 'Fecha Embarque']],
                                                                tabla_devoluciones[[estacionalidad_cantidad + ' Devueltas', 'Fecha Devolución']]),
                                        estacionalidad_cantidad)

                # st.title(analisis + ' por ' + estacionalidad_cantidad)

                # calcular_periodo(df_recibo)
                # estacionalidad(
                #     *preparar_datos_estacionalidad(
                #         df_recibo,
                #         df_embarque,
                #         df_devoluciones,
                #         df_inventario,``
                #         estacionalidad_cantidad
                #     )
                # )


    else:
        st.success('Para hacer uso correcto de la herramienta, descarga la' + 
                   ' siguiente plantilla base y llena las columnas con los datos correspondientes:')

        st.markdown(boton_de_descarga('.\data\plantilla.xlsx',
                                      'plantilla.xlsx',
                                      'Descarga aquí la plantilla'),
                    unsafe_allow_html=True)



        # elif analisis == menu_options[1]:
        #     estacionalidad_cantidad = st.sidebar.radio(
        #         'Selecciona las Cantidades a Usar:',
        #         ['Unidades', 'Cajas', 'Tarimas'],
        #         index=0
        #     )

        #     st.title(analisis + ' por ' + estacionalidad_cantidad)

        #     calcular_periodo(df_recibo)
        #     estacionalidad(
        #         *preparar_datos_estacionalidad(
        #             df_recibo,
        #             df_embarque,
        #             df_devoluciones,
        #             df_inventario,``
        #             estacionalidad_cantidad
        #         )
        #     )




        # elif analisis == menu_options[2]:
        #     cargas_cantidad = st.sidebar.radio(
        #         'Selecciona las Cantidades a Usar:',
        #         ['Unidades', 'Cajas', 'Tarimas'],
        #         index=0
        #     )

        #     cargas_periodo = st.sidebar.radio(
        #         'Selecciona el Período de Tiempo a Usar:',
        #         ['Turno', 'Horario'],
        #         index=0
        #     )

        #     st.title(analisis + ' de ' + cargas_cantidad + ' por ' + cargas_periodo)

        #     dias = calcular_periodo(df_recibo)
        #     cargas_operativas(
        #         *preparar_datos_cargas_operativas(
        #         df_recibo,
        #         df_embarque,
        #         df_devoluciones,
        #         cargas_cantidad,
        #         cargas_periodo,
        #         dias
        #         )
        #     )
            
        # elif analisis == menu_options[3]:
        #     resumen_tipo = st.sidebar.radio(
        #         'Selecciona el Tipo de Datos a Usar:',
        #         ['Recibos', 'Embarques', 'Devoluciones'],
        #         index=0
        #     )
        #     resumen_cantidad = st.sidebar.radio(
        #         'Selecciona las Cantidades a Usar:',
        #         ['Unidades', 'Cajas', 'Tarimas'],
        #         index=0
        #     )

        #     resumen_periodo = ''
        #     # resumen_periodo = st.sidebar.radio(
        #     #     'Selecciona el Período de Tiempo a Usar:',
        #     #     ['Días', 'Meses', 'Años'],
        #     #     index=0
        #     # )

        #     resumen_secciones = st.sidebar.number_input(
        #         'Selecciona el Número de Secciones del Histograma:',
        #         1,
        #         20,
        #         10
        #     )
            
        #     if resumen_tipo == 'Recibos':
        #         st.title(analisis + ' de ' + resumen_cantidad + ' Recibidas')
        #         # st.title(analisis + ' de ' + resumen_cantidad + ' Recibidas por ' + resumen_periodo)
        #         resumenes(
        #             *preparar_datos_resumenes(
        #                 df_recibo,
        #                 resumen_cantidad,
        #                 resumen_periodo,
        #                 resumen_tipo
        #             ),
        #             resumen_secciones
        #         )

        #     elif resumen_tipo == 'Embarques':
        #         st.title(analisis + ' de ' + resumen_cantidad + ' Embarcadas')
        #         resumenes(
        #             *preparar_datos_resumenes(
        #                 df_embarque,
        #                 resumen_cantidad,
        #                 resumen_periodo,
        #                 resumen_tipo
        #             ),
        #             resumen_secciones
        #         )
        #     else:
        #         st.title(analisis + ' de ' + resumen_cantidad + ' Devueltas')
        #         resumenes(
        #             *preparar_datos_resumenes(
        #                 df_devoluciones,
        #                 resumen_cantidad,
        #                 resumen_periodo,
        #                 resumen_tipo
        #             ),
        #             resumen_secciones
        #         )
                
        # elif analisis == menu_options[4]:
        #     st.title(analisis)
        #     abc_cantidad = st.sidebar.radio(
        #         'Selecciona las Cantidades a Usar:',
        #         ['Unidades', 'Cajas', 'Tarimas'],
        #         index=0
        #     )

        #     abc_peso_volumen = st.sidebar.number_input('Selecciona el valor del ABC por Volumen:', 
        #                                                 min_value=0.00, max_value=100.00, value=50.00
        #                                                 )

        #     abc_peso_variabilidad = st.sidebar.number_input('Selecciona el valor del ABC por Variabilidad:', 
        #                                                     min_value=0.00, max_value=100.00, value=30.00
        #                                                     )

        #     abc_peso_frecuencia = st.sidebar.number_input('Selecciona el valor del ABC por Frecuencia:', 
        #                                                     min_value=0.00, max_value=100.00, value=20.00
        #                                                     )

        #     if abc_peso_volumen + abc_peso_variabilidad + abc_peso_frecuencia != 100:
        #         st.sidebar.warning('Verifica que los valores de ABC sumen 100%.')
        #         st.stop()
                
        #     clasificacion_ponderada_abc(
        #         clasificacion_variabilidad_abc(
        #             clasificacion_frecuencia_abc(
        #                 clasificacion_volumen_abc(
        #                     preparar_datos_clasificacion_abc(df_embarque, abc_cantidad)))),
        #                     abc_peso_volumen, abc_peso_variabilidad, abc_peso_frecuencia)


if __name__ == "__main__":
        main()
