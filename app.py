# Importando Librerias
import streamlit as st

# Libreria de Utilidades
from src.utilidades import boton_de_descarga, mostrar_error, checar_integridad_fechas, obtener_fecha_minmax, ocultar_indice, checar_integridad_secciones
# Análisis 0: Leer Tablas
from src.cargar_archivos import leer_archivo_a_tablas
# Análisis 1: Mostrar Tablas
from src.mostrar_tablas import mostrar_tablas
# Análisis 2: Estacionalidad
from src.estacionalidad import calcular_estacionalidad, mostrar_estacionalidad
# Análisis 3: Cargas Operativas
from src.cargas_operativas import calcular_cargas, mostrar_cargas
# Análisis 4: Resúmenes
from src.resumenes_por_dia import calcular_resumenes, mostrar_resumenes
# Análisis 5: Clasificación ABC Ponderado
from src.clasificacion_abc import calcular_clasificacion_abc, mostrar_clasificacion_abc, mostrar_comparacion_absoluta, mostrar_comparacion_porcentual, calcular_abc_comparativo
# Análisis 6: Distribución de Volumen Mensual
from src.distribucion_volumen_mensual import calcular_distribucion_volumen, mostrar_distribucion_volumen
# Análisis 7: Distribución Incremental de Ordenes
from src.distribucion_incremental_ordenes import calcular_distribucion_ordenes, mostrar_distribucion_ordenes
# Análisis 8: Distribución Completa/Parcial/Mixta
from src.distribucion_comparacion import calcular_distribucion_comparacion, mostrar_distribucion_comparacion


def main():
    """
    docstring
    """
    st.set_page_config(page_title='CEDIS', page_icon='img/icon.png')
    
    st.sidebar.title('CEDIS')

    archivo = st.sidebar.file_uploader('Selecciona el archivo a analizar:', type=['xlsx'])

    if archivo:
        lista_tablas, lista_tablas_errores = leer_archivo_a_tablas(archivo)

        if lista_tablas_errores:
            for error in lista_tablas_errores:
                mostrar_error(*error)
        else:
            tabla_sku, tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones = lista_tablas

            opciones_analisis = {1: 'Mostrar Tablas',
                                 2: 'Estacionalidad',
                                 3: 'Cargas Operativas',
                                 4: 'Resúmenes por Día',
                                 5: 'Clasificación ABC Ponderada',
                                 6: 'Distribución de Volumen Mensual',
                                 7: 'Distribución Incremental de Ordenes',
                                 8: 'Distribución Completa/Parcial/Mixta'}
                                 
            analisis_seleccionado = st.sidebar.selectbox('Selecciona el Análisis a Ejecutar:',
                                                          options=list(opciones_analisis.items()),
                                                          index=0,
                                                          format_func=lambda opcion: opcion[1])

            if analisis_seleccionado[0] == 1:

                mostrar_tablas(tabla_sku.head(10),
                               tabla_inventario.head(10),
                               tabla_recibos.head(10),
                               tabla_embarques.head(10),
                               tabla_devoluciones.head(10))

            elif analisis_seleccionado[0] == 2:

                with st.sidebar.beta_expander('Configuración de Análisis'):
                    estacionalidad_fechas_contenedor = st.beta_container()

                    estacionalidad_cantidad = st.radio('Selecciona las Cantidades:',
                                                       ['Unidades', 'Cajas', 'Tarimas'],
                                                       index=0)

                    estacionalidad_tipo = st.radio('Selecciona el Tipo de Resumen:',
                                                   ['Por Mes', 'Por Semana'],
                                                   index=0)

                lista_fechas_errores = checar_integridad_fechas(tabla_inventario['Fecha de Inventario'],
                                                                tabla_recibos['Fecha de Recibo'],
                                                                tabla_embarques['Fecha de Embarque'],
                                                                tabla_devoluciones['Fecha de Devolución'])

                if lista_fechas_errores:
                    for error in lista_fechas_errores:
                        mostrar_error(*error)
                else:
                    fecha_min = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     True)

                    fecha_max = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     False)

                    estacionalidad_fechas = estacionalidad_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                                        value=(fecha_min, fecha_max),
                                                                                        min_value=fecha_min,
                                                                                        max_value=fecha_max,
                                                                                        key='estacionalidad_fechas')

                    ocultar_indice()
                    try:
                        mostrar_estacionalidad(calcular_estacionalidad(tabla_inventario.loc[(tabla_inventario['Fecha de Inventario'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                            (tabla_inventario['Fecha de Inventario'].dt.date <= estacionalidad_fechas[1]),
                                                                                            [estacionalidad_cantidad + ' de Inventario', 'Fecha de Inventario']],
                                                                        tabla_recibos.loc[(tabla_recibos['Fecha de Recibo'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                            (tabla_recibos['Fecha de Recibo'].dt.date <= estacionalidad_fechas[1]),
                                                                                        [estacionalidad_cantidad + ' Recibidas', 'Fecha de Recibo']],
                                                                        tabla_embarques.loc[(tabla_embarques['Fecha de Embarque'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                            (tabla_embarques['Fecha de Embarque'].dt.date <= estacionalidad_fechas[1]),
                                                                                            [estacionalidad_cantidad + ' Embarcadas', 'Fecha de Embarque']],
                                                                        tabla_devoluciones.loc[(tabla_devoluciones['Fecha de Devolución'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                                (tabla_devoluciones['Fecha de Devolución'].dt.date <= estacionalidad_fechas[1]),
                                                                                                [estacionalidad_cantidad + ' Devueltas', 'Fecha de Devolución']],
                                                                        estacionalidad_cantidad,
                                                                        estacionalidad_tipo),
                                                estacionalidad_cantidad,
                                                estacionalidad_fechas,
                                                estacionalidad_tipo)
                    except IndexError:
                        mostrar_error(6)
                                                   
            elif analisis_seleccionado[0] == 3:

                with st.sidebar.beta_expander('Configuración de Análisis'):
                    cargas_fechas_contenedor = st.beta_container()
                    
                    cargas_cantidad = st.radio('Selecciona las Cantidades:',
                                               ['Unidades', 'Cajas', 'Tarimas'],
                                               index=0)

                    cargas_periodo = st.radio('Selecciona el Período de Tiempo:',
                                               ['Turno', 'Horario'],
                                               index=0)
                    
                    cargas_secciones_contenedor = st.beta_container()


                lista_fechas_errores = checar_integridad_fechas(tabla_inventario['Fecha de Inventario'],
                                                                tabla_recibos['Fecha de Recibo'],
                                                                tabla_embarques['Fecha de Embarque'],
                                                                tabla_devoluciones['Fecha de Devolución'])

                if lista_fechas_errores:
                    for error in lista_fechas_errores:
                        mostrar_error(*error)
                else:
                    fecha_min = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     True)

                    fecha_max = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     False)

                    cargas_fechas = cargas_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                        value=(fecha_min, fecha_max),
                                                                        min_value=fecha_min,
                                                                        max_value=fecha_max,
                                                                        key='cargas_fechas')
   

                    if cargas_periodo == 'Horario':
                        cargas_secciones = cargas_secciones_contenedor.number_input("Selecciona el Número de Secciones del Horario:",
                                                                                    min_value=1,
                                                                                    max_value=12,
                                                                                    value=1,
                                                                                    step=1)

                        cargas_cortes = []
                        for i in range(cargas_secciones +  1):
                            corte = cargas_secciones_contenedor.number_input(f'Corte de Horario {i + 1}:',
                                                                             min_value=0,
                                                                             max_value=23,
                                                                             value=0,
                                                                             step=1,
                                                                             key=f'cargas_corte_{i}')
                            cargas_cortes.append(corte)

                        
                        if checar_integridad_secciones(cargas_cortes):
                            ocultar_indice()
                            try:
                                mostrar_cargas(*calcular_cargas(tabla_recibos.loc[(tabla_recibos['Fecha de Recibo'].dt.date >= cargas_fechas[0]) & \
                                                                                (tabla_recibos['Fecha de Recibo'].dt.date <= cargas_fechas[1]),
                                                                                [cargas_cantidad + ' Recibidas', 'Horario de Recibo']],
                                                                tabla_embarques.loc[(tabla_embarques['Fecha de Embarque'].dt.date >= cargas_fechas[0]) & \
                                                                                    (tabla_embarques['Fecha de Embarque'].dt.date <= cargas_fechas[1]),
                                                                                [cargas_cantidad + ' Embarcadas', 'Horario de Embarque']],
                                                                tabla_devoluciones.loc[(tabla_devoluciones['Fecha de Devolución'].dt.date >= cargas_fechas[0]) & \
                                                                                    (tabla_devoluciones['Fecha de Devolución'].dt.date <= cargas_fechas[1]),
                                                                                    [cargas_cantidad + ' Devueltas', 'Horario de Devolución']],
                                                                cargas_cantidad,
                                                                cargas_periodo,
                                                                cargas_fechas,
                                                                cargas_cortes),
                                                cargas_cantidad,
                                                cargas_periodo,
                                                cargas_fechas)
                            except IndexError:
                                mostrar_error(6)

                        else:
                            mostrar_error(5)

                    else:
                        ocultar_indice()
                        try:
                            mostrar_cargas(*calcular_cargas(tabla_recibos.loc[(tabla_recibos['Fecha de Recibo'].dt.date >= cargas_fechas[0]) & \
                                                                            (tabla_recibos['Fecha de Recibo'].dt.date <= cargas_fechas[1]),
                                                                            [cargas_cantidad + ' Recibidas', 'Turno de Recibo']],
                                                            tabla_embarques.loc[(tabla_embarques['Fecha de Embarque'].dt.date >= cargas_fechas[0]) & \
                                                                                (tabla_embarques['Fecha de Embarque'].dt.date <= cargas_fechas[1]),
                                                                            [cargas_cantidad + ' Embarcadas', 'Turno de Embarque']],
                                                            tabla_devoluciones.loc[(tabla_devoluciones['Fecha de Devolución'].dt.date >= cargas_fechas[0]) & \
                                                                                (tabla_devoluciones['Fecha de Devolución'].dt.date <= cargas_fechas[1]),
                                                                                [cargas_cantidad + ' Devueltas', 'Turno de Devolución']],
                                                            cargas_cantidad,
                                                            cargas_periodo,
                                                            cargas_fechas),
                                            cargas_cantidad,
                                            cargas_periodo,
                                            cargas_fechas)
                        except IndexError:
                            mostrar_error(6)

            elif analisis_seleccionado[0] == 4:
   
                resumenes_lista_tablas = [tabla_recibos, tabla_embarques, tabla_devoluciones]
   
                resumenes_lista_tipos = ['Recibos',
                                         'Embarques',
                                         'Devoluciones']
   
                resumenes_columnas_tiempo = ['Fecha de Recibo',
                                             'Fecha de Embarque',
                                             'Fecha de Devolución']

                with st.sidebar.beta_expander('Configuración de Análisis'):
                    resumenes_fechas_contenedor = st.beta_container()

                    resumenes_tipo = st.radio('Selecciona el Tipo de Datos:',
                                              resumenes_lista_tipos,
                                              index=0)

                    resumenes_cantidad = st.radio('Selecciona las Cantidades:',
                                                  ['Unidades', 'Cajas', 'Tarimas'],
                                                  index=0)

                    resumenes_minimo = st.number_input(f'Selecciona el Mínimo de {resumenes_cantidad} a Contar:',
                                                          min_value=0, value=0, step=1)

                    resumenes_maximo = st.number_input(f'Selecciona el Máximo de {resumenes_cantidad} a Contar:',
                                                          min_value=0, value=100_000, step=1)

                    resumenes_secciones = st.number_input('Selecciona el Número de Secciones del Histograma:',
                                                          1, 20, 10)
                

                lista_fechas_errores = checar_integridad_fechas(tabla_inventario['Fecha de Inventario'],
                                                                tabla_recibos['Fecha de Recibo'],
                                                                tabla_embarques['Fecha de Embarque'],
                                                                tabla_devoluciones['Fecha de Devolución'])

                if lista_fechas_errores:
                    for error in lista_fechas_errores:
                        mostrar_error(*error)
                else:
                    fecha_min = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     True)

                    fecha_max = obtener_fecha_minmax(tabla_inventario['Fecha de Inventario'],
                                                     tabla_recibos['Fecha de Recibo'],
                                                     tabla_embarques['Fecha de Embarque'],
                                                     tabla_devoluciones['Fecha de Devolución'],
                                                     False)

                    resumenes_fechas = resumenes_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                              value=(fecha_min, fecha_max),
                                                                              min_value=fecha_min,
                                                                              max_value=fecha_max,
                                                                              key='resumenes_fechas')

                
                resumenes_columnas_cantidades = [resumenes_cantidad + ' Recibidas',
                                                 resumenes_cantidad + ' Embarcadas',
                                                 resumenes_cantidad + ' Devueltas']

                for tabla, tipo, columna_tiempo, columna_cantidades in zip(resumenes_lista_tablas,
                                                                               resumenes_lista_tipos,
                                                                               resumenes_columnas_tiempo ,
                                                                               resumenes_columnas_cantidades):
                    if resumenes_tipo == tipo:
                        ocultar_indice()
                        try:
                            mostrar_resumenes(*calcular_resumenes(tabla.loc[(tabla[columna_tiempo].dt.date >= resumenes_fechas[0]) & \
                                                                            (tabla[columna_tiempo].dt.date <= resumenes_fechas[1]),
                                                                           [columna_tiempo, columna_cantidades]],\
                                                                  resumenes_minimo,
                                                                  resumenes_maximo,
                                                                  columna_tiempo,
                                                                  columna_cantidades,
                                                                  resumenes_fechas),
                                              resumenes_tipo,
                                              columna_tiempo,
                                              columna_cantidades,
                                              resumenes_fechas,
                                              resumenes_secciones)
                        except IndexError:
                            mostrar_error(6)

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

                df = mostrar_clasificacion_abc(*calcular_clasificacion_abc(tabla_embarques[['ID del Producto', abc_cantidad + ' Embarcadas']],
                                                                      abc_cantidad,
                                                                      abc_peso_volumen,
                                                                      abc_peso_frecuencia,
                                                                      abc_peso_variabilidad),
                                                tabla_recibos['Fecha de Recibo'])
                
                mostrar_comparacion_absoluta(tabla_sku[['ID del Producto', 'Clasificación ABC del Cliente']],
                                             df,
                                             tabla_recibos['Fecha de Recibo'])

                mostrar_comparacion_porcentual(tabla_sku[['ID del Producto', 'Clasificación ABC del Cliente']],
                                               df,
                                               tabla_recibos['Fecha de Recibo'])

                calcular_abc_comparativo(tabla_inventario[['ID del Producto', abc_cantidad + ' de Inventario']],
                                         tabla_embarques[['ID del Producto', abc_cantidad + ' Embarcadas']],
                                         df,
                                         abc_cantidad,
                                         tabla_recibos['Fecha de Recibo'])
                
                # del tabla_sku['Clasificación ABC Sintec']

                # df_total = pd.merge(tabla_sku, df, how='inner', on='ID del Producto')

                # with pd.ExcelWriter(".\data\cedis_abc.xlsx") as writer:
                #     df_total.to_excel(writer, sheet_name="Información SKU", index=False)
                #     tabla_inventario.to_excel(writer, sheet_name="Foto de Inventarios", index=False)
                #     tabla_recibos.to_excel(writer, sheet_name="Base de Recibo", index=False)
                #     tabla_embarques.to_excel(writer, sheet_name="Base de Embarque", index=False)
                #     tabla_devoluciones.to_excel(writer, sheet_name="Base de Devoluciones", index=False)

                # st.markdown(boton_de_descarga('.\data\cedis_abc.xlsx',
                #                             'cedis_abc.xlsx',
                #                             'Descarga aquí la Clasificación ABC Ponderada'),
                #             unsafe_allow_html=True)

            elif analisis_seleccionado[0] == 6:
                distribucion_volumen_secciones = st.sidebar.number_input('Selecciona el Número de Secciones del Histograma:',
                                                                         1,
                                                                         20,
                                                                         7)
                
                mostrar_distribucion_volumen(calcular_distribucion_volumen(tabla_embarques[['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']],
                                                                           tabla_sku[['ID del Producto', 'Volumen x Unidad']]),
                                             distribucion_volumen_secciones,
                                             tabla_recibos['Fecha de Recibo'])

            elif analisis_seleccionado[0] == 7:
                contenedor_familia_1 = st.sidebar.beta_container()

                if st.sidebar.checkbox('Seleccionar Todas', key='familia_1'):
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist(),
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist())
                else:
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist())

                if distribucion_ordenes_familia_1:
                    contenedor_familia_2 = st.sidebar.beta_container()

                    if st.sidebar.checkbox('Seleccionar Todas', key='familia_2'):
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist(),
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist())
                    else:
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist())     

                    if distribucion_ordenes_familia_2:
                        contenedor_familia_3 = st.sidebar.beta_container()

                        if st.sidebar.checkbox('Seleccionar Todas', key='familia_3'):
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist(),
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist())
                        else:
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist())                        
                        
                        if distribucion_ordenes_familia_3:
                            mostrar_distribucion_ordenes(calcular_distribucion_ordenes(tabla_embarques[['ID del Producto', 'Cajas Embarcadas']],
                                                                                       tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1) & \
                                                                                                     tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2) & \
                                                                                                     tabla_sku['Familia de Almacén III'].isin(distribucion_ordenes_familia_3),
                                                                                                     ['ID del Producto', 'Cajas x Tarima']]),
                                                         tabla_recibos['Fecha de Recibo'])
                            
            elif analisis_seleccionado[0] == 8:
                contenedor_familia_1 = st.sidebar.beta_container()
                
                if st.sidebar.checkbox('Seleccionar Todas', key='familia_1'):
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist(),
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist())
                else:
                    distribucion_ordenes_familia_1 = contenedor_familia_1.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                      tabla_sku['Familia de Almacén I'].unique().tolist())

                if distribucion_ordenes_familia_1:
                    contenedor_familia_2 = st.sidebar.beta_container()

                    if st.sidebar.checkbox('Seleccionar Todas', key='familia_2'):
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist(),
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist())
                    else:
                        distribucion_ordenes_familia_2 = contenedor_familia_2.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                          tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1), 'Familia de Almacén II'].unique().tolist())     

                    if distribucion_ordenes_familia_2:
                        contenedor_familia_3 = st.sidebar.beta_container()

                        if st.sidebar.checkbox('Seleccionar Todas', key='familia_3'):
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist(),
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist())
                        else:
                            distribucion_ordenes_familia_3 = contenedor_familia_3.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                            tabla_sku.loc[tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2), 'Familia de Almacén III'].unique().tolist())                        
                        

                        if distribucion_ordenes_familia_3:
                            mostrar_distribucion_comparacion(calcular_distribucion_comparacion(tabla_embarques[['Pedido', 'ID del Producto', 'Cajas Embarcadas']],
                                                                                               tabla_sku.loc[tabla_sku['Familia de Almacén I'].isin(distribucion_ordenes_familia_1) & \
                                                                                                             tabla_sku['Familia de Almacén II'].isin(distribucion_ordenes_familia_2) & \
                                                                                                             tabla_sku['Familia de Almacén III'].isin(distribucion_ordenes_familia_3),
                                                                                                             ['ID del Producto', 'Cajas x Tarima']]),
                                                             tabla_recibos['Fecha de Recibo'])
                            
    else:
        st.success('Para hacer uso correcto de la herramienta, descarga la' + 
                   ' siguiente plantilla base y llena las columnas con los datos correspondientes:')

        st.markdown(boton_de_descarga('.\data\plantilla.xlsx',
                                      'plantilla.xlsx',
                                      'Descarga aquí la plantilla'),
                    unsafe_allow_html=True)


if __name__ == "__main__":
        main()
