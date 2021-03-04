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
from src.resumenes_por_dia import calcular_resumen_generales, calcular_resumenes_acotados, mostrar_resumenes
# Análisis 5: Clasificación ABC Ponderada
from src.clasificacion_abc_ponderada import calcular_clasificacion_abc, mostrar_clasificacion_abc, descargar_clasificacion_abc
# Análisis 6: Comparación ABC Sintec vs ABC Cliente
from src.comparacion_abc_cliente import mostrar_comparacion_cliente_absoluta, mostrar_comparacion_cliente_porcentual
# Análisis 7: Comparación ABC Sintec vs Inventario
from src.comparacion_abc_inventario import mostrar_comparacion_inventario
# Análisis 8: Distribución de Volumen Mensual
from src.distribucion_volumen_mensual import calcular_distribucion_volumen, mostrar_distribucion_volumen, descargar_distribucion_volumen
# Análisis 9: Distribución Incremental de Ordenes
from src.distribucion_incremental_ordenes import calcular_distribucion_ordenes, mostrar_distribucion_ordenes
# Análisis 10: Distribución Completa/Parcial/Mixta
from src.distribucion_comparacion import calcular_distribucion_comparacion, mostrar_distribucion_comparacion


def estacionalidad(datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):
        estacionalidad_fechas_contenedor = st.beta_container()

        estacionalidad_cantidad = st.radio('Selecciona las Cantidades:',
                                            ['Unidades', 'Cajas', 'Tarimas'],
                                            index=0)

        estacionalidad_tipo = st.radio('Selecciona el Tipo de Resumen:',
                                        ['Por Mes', 'Por Semana'],
                                        index=0)

    lista_fechas_errores = checar_integridad_fechas(datos_inventario['Fecha de Inventario'],
                                                    datos_recibos['Fecha de Recibo'],
                                                    datos_embarques['Fecha de Embarque'],
                                                    datos_devoluciones['Fecha de Devolución'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
                                            True)

        fecha_max = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
                                            False)

        estacionalidad_fechas = estacionalidad_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                            value=(fecha_min, fecha_max),
                                                                            min_value=fecha_min,
                                                                            max_value=fecha_max,
                                                                            key='estacionalidad_fechas')

        ocultar_indice()
        try:
            mostrar_estacionalidad(calcular_estacionalidad(datos_inventario.loc[(datos_inventario['Fecha de Inventario'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                (datos_inventario['Fecha de Inventario'].dt.date <= estacionalidad_fechas[1]),
                                                                                [estacionalidad_cantidad + ' de Inventario', 'Fecha de Inventario']],
                                                            datos_recibos.loc[(datos_recibos['Fecha de Recibo'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                (datos_recibos['Fecha de Recibo'].dt.date <= estacionalidad_fechas[1]),
                                                                            [estacionalidad_cantidad + ' Recibidas', 'Fecha de Recibo']],
                                                            datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                (datos_embarques['Fecha de Embarque'].dt.date <= estacionalidad_fechas[1]),
                                                                                [estacionalidad_cantidad + ' Embarcadas', 'Fecha de Embarque']],
                                                            datos_devoluciones.loc[(datos_devoluciones['Fecha de Devolución'].dt.date >= estacionalidad_fechas[0]) & \
                                                                                    (datos_devoluciones['Fecha de Devolución'].dt.date <= estacionalidad_fechas[1]),
                                                                                    [estacionalidad_cantidad + ' Devueltas', 'Fecha de Devolución']],
                                                            estacionalidad_cantidad,
                                                            estacionalidad_tipo),
                                    estacionalidad_cantidad,
                                    estacionalidad_fechas,
                                    estacionalidad_tipo)
        except IndexError:
                        mostrar_error(6)


def cargas_operativas(datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):
        cargas_fechas_contenedor = st.beta_container()
        
        cargas_cantidad = st.radio('Selecciona las Cantidades:',
                                    ['Unidades', 'Cajas', 'Tarimas'],
                                    index=0)

        cargas_periodo = st.radio('Selecciona el Período de Tiempo:',
                                    ['Turno', 'Horario'],
                                    index=0)
        
        cargas_secciones_contenedor = st.beta_container()


    lista_fechas_errores = checar_integridad_fechas(datos_inventario['Fecha de Inventario'],
                                                    datos_recibos['Fecha de Recibo'],
                                                    datos_embarques['Fecha de Embarque'],
                                                    datos_devoluciones['Fecha de Devolución'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
                                            True)

        fecha_max = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
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
                    mostrar_cargas(*calcular_cargas(datos_recibos.loc[(datos_recibos['Fecha de Recibo'].dt.date >= cargas_fechas[0]) & \
                                                                    (datos_recibos['Fecha de Recibo'].dt.date <= cargas_fechas[1]),
                                                                    [cargas_cantidad + ' Recibidas', 'Horario de Recibo']],
                                                    datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= cargas_fechas[0]) & \
                                                                        (datos_embarques['Fecha de Embarque'].dt.date <= cargas_fechas[1]),
                                                                    [cargas_cantidad + ' Embarcadas', 'Horario de Embarque']],
                                                    datos_devoluciones.loc[(datos_devoluciones['Fecha de Devolución'].dt.date >= cargas_fechas[0]) & \
                                                                        (datos_devoluciones['Fecha de Devolución'].dt.date <= cargas_fechas[1]),
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
                mostrar_cargas(*calcular_cargas(datos_recibos.loc[(datos_recibos['Fecha de Recibo'].dt.date >= cargas_fechas[0]) & \
                                                                  (datos_recibos['Fecha de Recibo'].dt.date <= cargas_fechas[1]),
                                                                 [cargas_cantidad + ' Recibidas', 'Turno de Recibo']],
                                                datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= cargas_fechas[0]) & \
                                                                    (datos_embarques['Fecha de Embarque'].dt.date <= cargas_fechas[1]),
                                                                   [cargas_cantidad + ' Embarcadas', 'Turno de Embarque']],
                                                datos_devoluciones.loc[(datos_devoluciones['Fecha de Devolución'].dt.date >= cargas_fechas[0]) & \
                                                                       (datos_devoluciones['Fecha de Devolución'].dt.date <= cargas_fechas[1]),
                                                                      [cargas_cantidad + ' Devueltas', 'Turno de Devolución']],
                                                cargas_cantidad,
                                                cargas_periodo,
                                                cargas_fechas),
                                cargas_cantidad,
                                cargas_periodo,
                                cargas_fechas)
            except IndexError:
                mostrar_error(6)


def resumenes_por_dia(datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    resumenes_lista_tablas = [datos_recibos, datos_embarques, datos_devoluciones]

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

        resumenes_minimo_contenedor = st.beta_container()

        resumenes_maximo_contenedor = st.beta_container()


        resumenes_secciones = st.number_input('Selecciona el Número de Secciones del Histograma:', 1, 20, 10)
    

    lista_fechas_errores = checar_integridad_fechas(datos_inventario['Fecha de Inventario'],
                                                    datos_recibos['Fecha de Recibo'],
                                                    datos_embarques['Fecha de Embarque'],
                                                    datos_devoluciones['Fecha de Devolución'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
                                            True)

        fecha_max = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                            datos_recibos['Fecha de Recibo'],
                                            datos_embarques['Fecha de Embarque'],
                                            datos_devoluciones['Fecha de Devolución'],
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
                tabla_general = calcular_resumen_generales(tabla.loc[(tabla[columna_tiempo].dt.date >= resumenes_fechas[0]) & \
                                                                   (tabla[columna_tiempo].dt.date <= resumenes_fechas[1]),
                                                                  [columna_tiempo, columna_cantidades]],
                                                         columna_tiempo,
                                                         columna_cantidades,
                                                         resumenes_fechas)

                resumenes_minimo = resumenes_minimo_contenedor.number_input(f'Selecciona el Mínimo de {resumenes_cantidad} a Contar:',
                                                                            min_value=tabla_general['Mínimo'].iloc[0].astype(int),
                                                                            value=tabla_general['Mínimo'].iloc[0].astype(int),
                                                                            max_value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
                                                                            step=1)

                resumenes_maximo = resumenes_maximo_contenedor.number_input(f'Selecciona el Máximo de {resumenes_cantidad} a Contar:',
                                                                            min_value=tabla_general['Mínimo'].iloc[0].astype(int),
                                                                            value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
                                                                            max_value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
                                                                            step=1)

                mostrar_resumenes(*calcular_resumenes_acotados(tabla.loc[(tabla[columna_tiempo].dt.date >= resumenes_fechas[0]) & \
                                                                (tabla[columna_tiempo].dt.date <= resumenes_fechas[1]),
                                                                [columna_tiempo, columna_cantidades]],
                                                        resumenes_minimo,
                                                        resumenes_maximo,
                                                        columna_tiempo,
                                                        columna_cantidades,
                                                        resumenes_fechas),
                                    tabla_general,
                                    resumenes_tipo,
                                    columna_tiempo,
                                    columna_cantidades,
                                    resumenes_fechas,
                                    resumenes_secciones)
                                    
            except IndexError:
                mostrar_error(6)


def clasificacion_abc_ponderada(datos_sku, datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):

        abc_cantidad = st.radio('Selecciona las Cantidades:',
                                        ['Unidades', 'Cajas', 'Tarimas'],
                                        index=0)

        abc_peso_volumen = st.number_input('Selecciona el Valor Porcentual del ABC por Volumen:', 
                                                    min_value=0,
                                                    max_value=100,
                                                    value=50)

        abc_peso_variabilidad = st.number_input('Selecciona el Valor Porcentual del ABC por Variabilidad:', 
                                                        min_value=0,
                                                        max_value=100,
                                                        value=30)

        abc_peso_frecuencia = st.number_input('Selecciona el Valor Porcentual del ABC por Frecuencia:', 
                                                        min_value=0,
                                                        max_value=100,
                                                    value=20)

    if abc_peso_volumen + abc_peso_variabilidad + abc_peso_frecuencia == 100:
        mostrar_clasificacion_abc(*calcular_clasificacion_abc(datos_embarques[['ID del Producto', abc_cantidad + ' Embarcadas']],
                                                              abc_cantidad,
                                                              abc_peso_volumen,
                                                              abc_peso_frecuencia,
                                                              abc_peso_variabilidad),
                                  datos_embarques['Fecha de Embarque'])

        descargar_clasificacion_abc(calcular_clasificacion_abc(datos_embarques[['ID del Producto', abc_cantidad + ' Embarcadas']],
                                                               abc_cantidad,
                                                               abc_peso_volumen,
                                                               abc_peso_frecuencia,
                                                               abc_peso_variabilidad)[1],
                                    datos_sku)

        st.markdown(boton_de_descarga('./data/cedis_clasificacion_abc_ponderada.xlsx',
                                    'cedis_clasificacion_abc_ponderada.xlsx',
                                    'Descargar la Clasificación ABC Ponderada'),
                    unsafe_allow_html=True)
    else:
        mostrar_error(7)


def comparacion_abc_cliente(datos_sku):
    """
    docstring
    """
    if datos_sku['Clasificación ABC de Sintec'].str.contains('SR').any():
        with st.sidebar.beta_expander('Configuración de Análisis'):
            comparacion_abc_cliente_sr_contenedor = st.beta_container()
        
        if comparacion_abc_cliente_sr_contenedor.checkbox("Ocultar valores 'SR' de la Clasificación ABC de Sintec"):
            mostrar_comparacion_cliente_absoluta(datos_sku.loc[~datos_sku['Clasificación ABC de Sintec'].str.contains('SR'),
                                            ['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
            mostrar_comparacion_cliente_porcentual(datos_sku.loc[~datos_sku['Clasificación ABC de Sintec'].str.contains('SR'),
                                            ['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
        else:
            mostrar_comparacion_cliente_absoluta(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
            mostrar_comparacion_cliente_porcentual(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
    else:
        mostrar_comparacion_cliente_absoluta(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
        mostrar_comparacion_cliente_porcentual(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])


def comparacion_abc_inventario(datos_sku, datos_inventario, datos_embarques):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):

        comparacion_abc_inventario_cantidad = st.radio('Selecciona las Cantidades:',
                                                       ['Unidades', 'Cajas', 'Tarimas'],
                                                       index=0)

        comparacion_abc_inventario_tipo = st.radio('Selecciona el Tipo de Análisis:',
                                                   ['Por Sumatoria', 'Por Promedio', 'Por Última Foto de Inventario'],
                                                   index=0)

    lista_fechas_errores = checar_integridad_fechas(fecha_inventario=datos_inventario['Fecha de Inventario'],
                                                    fecha_embarque=datos_embarques['Fecha de Embarque'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(fecha_inventario=datos_inventario['Fecha de Inventario'],
                                         fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=True)

        fecha_max = obtener_fecha_minmax(fecha_inventario=datos_inventario['Fecha de Inventario'],
                                         fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=False)

        if comparacion_abc_inventario_tipo == 'Por Sumatoria':
            mostrar_comparacion_inventario(datos_sku[['ID del Producto', 'Clasificación ABC de Sintec']],
                                        datos_inventario[['ID del Producto', comparacion_abc_inventario_cantidad + ' de Inventario']],
                                        datos_embarques[['ID del Producto', comparacion_abc_inventario_cantidad + ' Embarcadas']],
                                        comparacion_abc_inventario_cantidad,
                                        'sum',
                                        False,
                                        (fecha_min, fecha_max))

        elif comparacion_abc_inventario_tipo == 'Por Promedio':
            mostrar_comparacion_inventario(datos_sku[['ID del Producto', 'Clasificación ABC de Sintec']],
                                        datos_inventario[['ID del Producto', comparacion_abc_inventario_cantidad + ' de Inventario']],
                                        datos_embarques[['ID del Producto', comparacion_abc_inventario_cantidad + ' Embarcadas']],
                                        comparacion_abc_inventario_cantidad,
                                        'mean',
                                        False,
                                        (fecha_min, fecha_max))

        else:
            mostrar_comparacion_inventario(datos_sku[['ID del Producto', 'Clasificación ABC de Sintec']],
                                        datos_inventario[['ID del Producto', 'Fecha de Inventario', comparacion_abc_inventario_cantidad + ' de Inventario']],
                                        datos_embarques[['ID del Producto', comparacion_abc_inventario_cantidad + ' Embarcadas']],
                                        comparacion_abc_inventario_cantidad,
                                        'sum',
                                        True,
                                        (fecha_min, fecha_max))


def distribucion_volumen_mensual(datos_sku, datos_embarques):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):
        volumen_mensual_fechas_contenedor = st.beta_container()
        volumen_mensual_secciones_contenedor = st.beta_container()
        volumen_mensual_cuartiles_contenedor = st.beta_container()


    lista_fechas_errores = checar_integridad_fechas(fecha_embarque=datos_embarques['Fecha de Embarque'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=True)

        fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=False)

        volumen_mensual_fechas = volumen_mensual_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                                value=(fecha_min, fecha_max),
                                                                                min_value=fecha_min,
                                                                                max_value=fecha_max,
                                                                                key='volumen_mensual_fechas')

        try:
            volumen_mensual_valores_cuartiles = calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
                                                                              datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
                                                                                                  (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
                                                                                                 ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']])\
                                                                                                     ['Volumen Promedio Mensual'].quantile([0, .25, .5, .75, 1]).tolist()

            volumen_mensual_valores_cuartiles[4] += 1

            volumen_mensual_cuartiles = volumen_mensual_cuartiles_contenedor.checkbox('Seleccionar Secciones por Cuartiles')

            if volumen_mensual_cuartiles:
                volumen_mensual_secciones = volumen_mensual_secciones_contenedor.number_input("Selecciona el Número de Secciones del Volumen Promedio Mensual:",
                                                                                                min_value=4,
                                                                                                max_value=4,
                                                                                                value=4)
            else:
                volumen_mensual_secciones = volumen_mensual_secciones_contenedor.number_input("Selecciona el Número de Secciones del Volumen Promedio Mensual:",
                                                                                                min_value=1,
                                                                                                max_value=10,
                                                                                                value=1,
                                                                                                step=1)
            volumen_mensual_cortes = []
            for index in range(volumen_mensual_secciones +  1):
                if volumen_mensual_cuartiles:
                    corte = volumen_mensual_secciones_contenedor.number_input(f'Corte de Volumen Promedio Mensual {index + 1}:',
                                                                                min_value=int(volumen_mensual_valores_cuartiles[0]),
                                                                                max_value=int(volumen_mensual_valores_cuartiles[4]),
                                                                                value=int(volumen_mensual_valores_cuartiles[index]),
                                                                                step=1,
                                                                                key=f'volumen_mensual_corte_{index}')
                else:
                    corte = volumen_mensual_secciones_contenedor.number_input(f'Corte de Volumen Promedio Mensual {index + 1}:',
                                                                                min_value=int(volumen_mensual_valores_cuartiles[0]),
                                                                                max_value=int(volumen_mensual_valores_cuartiles[4]),
                                                                                value=int(volumen_mensual_valores_cuartiles[0]),
                                                                                step=1,
                                                                                key=f'volumen_mensual_corte_{index}')
                    
                volumen_mensual_cortes.append(corte)


            if checar_integridad_secciones(volumen_mensual_cortes):

                mostrar_distribucion_volumen(*calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
                                                                            datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
                                                                                                (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
                                                                                               ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']],
                                                                            True,
                                                                            volumen_mensual_cortes),
                                             volumen_mensual_fechas)


                descargar_distribucion_volumen(calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
                                                                            datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
                                                                                                (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
                                                                                               ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']],
                                                                            True,
                                                                            volumen_mensual_cortes)[0])

                st.markdown(boton_de_descarga('./data/cedis_distribucion_volumen_mensual.xlsx',
                                            'cedis_distribucion_volumen_mensual.xlsx',
                                            'Descargar Distribución de Volumen Mensual'),
                            unsafe_allow_html=True)

            else:
                mostrar_error(5)

        except IndexError:
            mostrar_error(6)


def distribucion_incremental_ordenes(datos_sku, datos_embarques):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):
        incremental_fechas_contenedor = st.beta_container()
        incremental_cliente = st.selectbox('Selecciona el ID del Cliente:',
                                            ['Todos'] +  sorted(datos_embarques['ID del Cliente'].unique().tolist()),
                                            key='incremental_cliente')
        incremental_familia_1_contenedor = st.beta_container()
        incremental_checkbox_1_contenedor = st.beta_container()
        incremental_familia_2_contenedor = st.beta_container()
        incremental_checkbox_2_contenedor = st.beta_container()
        incremental_familia_3_contenedor = st.beta_container()
        incremental_checkbox_3_contenedor = st.beta_container()


    lista_fechas_errores = checar_integridad_fechas(fecha_embarque=datos_embarques['Fecha de Embarque'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=True)

        fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=False)

        incremental_fechas = incremental_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                        value=(fecha_min, fecha_max),
                                                                        min_value=fecha_min,
                                                                        max_value=fecha_max,
                                                                        key='incremental_fechas')

        if incremental_checkbox_1_contenedor.checkbox('Seleccionar Todas', key='incremental_familia_1'):
            incremental_familia_1 = incremental_familia_1_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                datos_sku['Familia de Almacén I'].unique().tolist(),
                                                                                datos_sku['Familia de Almacén I'].unique().tolist())
        else:
            incremental_familia_1 = incremental_familia_1_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                datos_sku['Familia de Almacén I'].unique().tolist())

        if incremental_familia_1:
            if incremental_checkbox_2_contenedor.checkbox('Seleccionar Todas', key='incremental_familia_2'):
                incremental_familia_2 = incremental_familia_2_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(incremental_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist(),
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(incremental_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist())
            else:
                incremental_familia_2 = incremental_familia_2_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(incremental_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist())     

            if incremental_familia_2:
                if incremental_checkbox_3_contenedor.checkbox('Seleccionar Todas', key='incremental_familia_3'):
                    incremental_familia_3 = incremental_familia_3_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(incremental_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist(),
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(incremental_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist())
                else:
                    incremental_familia_3 = incremental_familia_3_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(incremental_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist())                        
                
                if incremental_familia_3:            
                    try:
                        if incremental_cliente == 'Todos':
                            mostrar_distribucion_ordenes(calcular_distribucion_ordenes(datos_sku.loc[datos_sku['Familia de Almacén I'].isin(incremental_familia_1) & \
                                                                                                        datos_sku['Familia de Almacén II'].isin(incremental_familia_2) & \
                                                                                                        datos_sku['Familia de Almacén III'].isin(incremental_familia_3),
                                                                                                        ['ID del Producto', 'Cajas x Tarima']],
                                                                                        datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= incremental_fechas[0]) & \
                                                                                                            (datos_embarques['Fecha de Embarque'].dt.date <= incremental_fechas[1]),
                                                                                                        ['ID del Producto', 'Cajas Embarcadas']]),
                                                            incremental_fechas)
                        else:
                            mostrar_distribucion_ordenes(calcular_distribucion_ordenes(datos_sku.loc[datos_sku['Familia de Almacén I'].isin(incremental_familia_1) & \
                                                                                                        datos_sku['Familia de Almacén II'].isin(incremental_familia_2) & \
                                                                                                        datos_sku['Familia de Almacén III'].isin(incremental_familia_3),
                                                                                                        ['ID del Producto', 'Cajas x Tarima']],
                                                                                        datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= incremental_fechas[0]) & \
                                                                                                            (datos_embarques['Fecha de Embarque'].dt.date <= incremental_fechas[1]) & \
                                                                                                            (datos_embarques['ID del Cliente'] == incremental_cliente),
                                                                                                        ['ID del Producto', 'Cajas Embarcadas']]),
                                                            incremental_fechas)
                    except IndexError:
                        mostrar_error(6)


def distribucion_comparacion(datos_sku, datos_embarques):
    """
    docstring
    """
    with st.sidebar.beta_expander('Configuración de Análisis'):
        comparacion_fechas_contenedor = st.beta_container()
        comparacion_cliente = st.selectbox('Selecciona el ID del Cliente:',
                                            ['Todos'] +  sorted(datos_embarques['ID del Cliente'].unique().tolist()),
                                            key='comparacion_cliente')
        comparacion_familia_1_contenedor = st.beta_container()
        comparacion_checkbox_1_contenedor = st.beta_container()
        comparacion_familia_2_contenedor = st.beta_container()
        comparacion_checkbox_2_contenedor = st.beta_container()
        comparacion_familia_3_contenedor = st.beta_container()
        comparacion_checkbox_3_contenedor = st.beta_container()


    lista_fechas_errores = checar_integridad_fechas(fecha_embarque=datos_embarques['Fecha de Embarque'])

    if lista_fechas_errores:
        for error in lista_fechas_errores:
            mostrar_error(*error)
    else:
        fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=True)

        fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
                                         obten_min=False)

        comparacion_fechas = comparacion_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                        value=(fecha_min, fecha_max),
                                                                        min_value=fecha_min,
                                                                        max_value=fecha_max,
                                                                        key='comparacion_fechas')

        if comparacion_checkbox_1_contenedor.checkbox('Seleccionar Todas', key='comparacion_familia_1'):
            comparacion_familia_1 = comparacion_familia_1_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                datos_sku['Familia de Almacén I'].unique().tolist(),
                                                                                datos_sku['Familia de Almacén I'].unique().tolist())
        else:
            comparacion_familia_1 = comparacion_familia_1_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén I':",
                                                                                datos_sku['Familia de Almacén I'].unique().tolist())

        if comparacion_familia_1:
            if comparacion_checkbox_2_contenedor.checkbox('Seleccionar Todas', key='comparacion_familia_2'):
                comparacion_familia_2 = comparacion_familia_2_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(comparacion_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist(),
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(comparacion_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist())
            else:
                comparacion_familia_2 = comparacion_familia_2_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén II':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén I'].isin(comparacion_familia_1),\
                                                                                        'Familia de Almacén II'].unique().tolist())     

            if comparacion_familia_2:
                if comparacion_checkbox_3_contenedor.checkbox('Seleccionar Todas', key='comparacion_familia_3'):
                    comparacion_familia_3 = comparacion_familia_3_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(comparacion_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist(),
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(comparacion_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist())
                else:
                    comparacion_familia_3 = comparacion_familia_3_contenedor.multiselect("Selecciona la(s) 'Familia de Almacén III':",
                                                                                    datos_sku.loc[datos_sku['Familia de Almacén II'].isin(comparacion_familia_2),\
                                                                                        'Familia de Almacén III'].unique().tolist())                        
                
                if comparacion_familia_3:            
                    try:
                        if comparacion_cliente == 'Todos':
                            mostrar_distribucion_comparacion(calcular_distribucion_comparacion(datos_sku.loc[datos_sku['Familia de Almacén I'].isin(comparacion_familia_1) & \
                                                                                                        datos_sku['Familia de Almacén II'].isin(comparacion_familia_2) & \
                                                                                                        datos_sku['Familia de Almacén III'].isin(comparacion_familia_3),
                                                                                                        ['ID del Producto', 'Cajas x Tarima']],
                                                                                        datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= comparacion_fechas[0]) & \
                                                                                                            (datos_embarques['Fecha de Embarque'].dt.date <= comparacion_fechas[1]),
                                                                                                        ['Pedido', 'ID del Producto', 'Cajas Embarcadas']]),
                                                            comparacion_fechas)
                        else:
                            mostrar_distribucion_comparacion(calcular_distribucion_comparacion(datos_sku.loc[datos_sku['Familia de Almacén I'].isin(comparacion_familia_1) & \
                                                                                                        datos_sku['Familia de Almacén II'].isin(comparacion_familia_2) & \
                                                                                                        datos_sku['Familia de Almacén III'].isin(comparacion_familia_3),
                                                                                                        ['ID del Producto', 'Cajas x Tarima']],
                                                                                        datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= comparacion_fechas[0]) & \
                                                                                                            (datos_embarques['Fecha de Embarque'].dt.date <= comparacion_fechas[1]) & \
                                                                                                            (datos_embarques['ID del Cliente'] == comparacion_cliente),
                                                                                                        ['Pedido', 'ID del Producto', 'Cajas Embarcadas']]),
                                                            comparacion_fechas)

                    except IndexError:
                        mostrar_error(6)


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
                                 6: 'ABC Sintec vs ABC Cliente',
                                 7: 'ABC de Embarques vs Inventario',
                                 8: 'Distribución de Volumen Mensual',
                                 9: 'Distribución Incremental de Ordenes',
                                 10: 'Distribución Completa/Parcial/Mixta'}
                                 
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
                estacionalidad(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones)    
            
            elif analisis_seleccionado[0] == 3:
                cargas_operativas(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones)
                
            elif analisis_seleccionado[0] == 4:
                resumenes_por_dia(tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones)

            elif analisis_seleccionado[0] == 5:
                clasificacion_abc_ponderada(tabla_sku, tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones)

            elif analisis_seleccionado[0] == 6:
                comparacion_abc_cliente(tabla_sku)

            elif analisis_seleccionado[0] == 7:
                comparacion_abc_inventario(tabla_sku, tabla_inventario, tabla_embarques)
                
            elif analisis_seleccionado[0] == 8:
                distribucion_volumen_mensual(tabla_sku, tabla_embarques)

            elif analisis_seleccionado[0] == 9:
                distribucion_incremental_ordenes(tabla_sku, tabla_embarques)
                            
            elif analisis_seleccionado[0] == 10:
                distribucion_comparacion(tabla_sku, tabla_embarques)
                            
    else:
        st.success('Para hacer uso correcto de la herramienta, descarga la' + 
                   ' siguiente plantilla base y llena las columnas con los datos correspondientes:')

        st.markdown(boton_de_descarga('./data/plantilla.xlsx',
                                      'plantilla.xlsx',
                                      'Descarga aquí la plantilla'),
                    unsafe_allow_html=True)


if __name__ == "__main__":
        main()
