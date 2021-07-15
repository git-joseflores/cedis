# Importando Librerias
import streamlit as st
import pandas as pd

# Libreria de Utilidades
from src.utilidades import mostrar_error, mostrar_advertencia, boton_de_descarga, checar_integridad_numerica
from src.utilidades import checar_integridad_fechas, obtener_fecha_minmax, ocultar_indice, checar_integridad_secciones

# Análisis 0: Leer Tablas
from src.cargar_archivos import leer_archivo_a_tablas
# Análisis 1: Mostrar Tablas
from src.mostrar_tablas import mostrar_tablas
# Análisis 2: Estacionalidad
from src.estacionalidad import preparar_estacionalidad, calcular_estacionalidad, mostrar_estacionalidad
# Análisis 3: Cargas Operativas
from src.cargas_operativas import preparar_cargas, calcular_cargas, mostrar_cargas
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
# Análisis 12: Densidad de Pickeo
from src.densidad_pickeo import calcular_densidad_pickeo, mostrar_densidad_pickeo
# Análisis 13: Espacio de Almacenamiento de Picking
from src.almacenamiento_picking import calcular_almancenamiento_picking, mostrar_almancenamiento_picking
# Análisis 14: Espacio de Pedidos de Picking
from src.pedidos_picking import calcular_pedidos_picking, mostrar_pedidos_picking
# Análisis 15: Handling Mix Profile
from src.handling_mix_profile import calcular_handling_mix_profile

def estacionalidad(datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    estacionalidad_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('estacionalidad'):
            estacionalidad_fechas_contenedor = st.beta_container()

            estacionalidad_cantidad_contenedor = st.beta_container()
            
            estacionalidad_tipo_contenedor = st.beta_container()

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_inventario, datos_inventario, datos_inventario,
              datos_recibos, datos_recibos, datos_recibos,
              datos_embarques, datos_embarques, datos_embarques,
              datos_devoluciones, datos_devoluciones, datos_devoluciones]

    nombre_tablas = ['Foto de Inventarios', 'Foto de Inventarios', 'Foto de Inventarios',
                     'Base de Recibo', 'Base de Recibo', 'Base de Recibo',
                     'Base de Embarque', 'Base de Embarque', 'Base de Embarque',
                     'Base de Devoluciones', 'Base de Devoluciones', 'Base de Devoluciones']

    nombre_columnas = ['Unidades de Inventario', 'Cajas de Inventario', 'Tarimas de Inventario',
                       'Unidades Recibidas', 'Cajas Recibidas', 'Tarimas Recibidas',
                       'Unidades Embarcadas', 'Cajas Embarcadas', 'Tarimas Embarcadas',
                       'Unidades Devueltas', 'Cajas Devueltas', 'Tarimas Devueltas']
    

    cantidades_estacionalidad = ['Unidades', 'Cajas', 'Tarimas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    cantidades_estacionalidad.remove('Unidades')
                except:
                    pass
            elif nombre_columna.startswith('Cajas'):
                try:
                    cantidades_estacionalidad.remove('Cajas')
                except:
                    pass
            else:
                try:
                    cantidades_estacionalidad.remove('Tarimas')
                except:
                    pass

    estacionalidad_cantidad = estacionalidad_cantidad_contenedor.radio('Selecciona las Cantidades:',
                                                                       cantidades_estacionalidad,
                                                                       index=0)


    tablas = [datos_inventario, datos_recibos, datos_embarques, datos_devoluciones]
    nombre_tablas = ['Foto de Inventarios', 'Base de Recibo', 'Base de Embarque', 'Base de Devoluciones']
    nombre_columnas = ['Fecha de Inventario', 'Fecha de Recibo', 'Fecha de Embarque', 'Fecha de Devolución']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and estacionalidad_cantidad:
        estacionalidad_titulo_contenedor.title('Estacionalidad de ' + estacionalidad_cantidad)

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

        estacionalidad_tipo = estacionalidad_tipo_contenedor.radio('Selecciona el Tipo de Resumen:',
                                                                   ['Por Mes', 'Por Semana'],
                                                                   index=0)

        ocultar_indice()

        try:
            mostrar_estacionalidad(*calcular_estacionalidad(*preparar_estacionalidad(datos_inventario,
                                                                                     datos_recibos,
                                                                                     datos_embarques,
                                                                                     datos_devoluciones,
                                                                                     estacionalidad_cantidad,
                                                                                     estacionalidad_fechas),
                                                            estacionalidad_tipo))

        except IndexError:
            mostrar_error(6)


def cargas_operativas(datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    cargas_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('cargas'):
            cargas_fechas_contenedor = st.beta_container()

            cargas_cantidad_contenedor = st.beta_container()
            
            cargas_periodo_contenedor = st.beta_container()

            cargas_secciones_contenedor = st.beta_container()

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_recibos, datos_recibos, datos_recibos,
              datos_embarques, datos_embarques, datos_embarques,
              datos_devoluciones, datos_devoluciones, datos_devoluciones]

    nombre_tablas = ['Base de Recibo', 'Base de Recibo', 'Base de Recibo',
                     'Base de Embarque', 'Base de Embarque', 'Base de Embarque',
                     'Base de Devoluciones', 'Base de Devoluciones', 'Base de Devoluciones']

    nombre_columnas = ['Unidades Recibidas', 'Cajas Recibidas', 'Tarimas Recibidas',
                       'Unidades Embarcadas', 'Cajas Embarcadas', 'Tarimas Embarcadas',
                       'Unidades Devueltas', 'Cajas Devueltas', 'Tarimas Devueltas']

    cantidades_cargas = ['Unidades', 'Cajas', 'Tarimas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    cantidades_cargas.remove('Unidades')
                except:
                    pass
            elif nombre_columna.startswith('Cajas'):
                try:
                    cantidades_cargas.remove('Cajas')
                except:
                    pass
            else:
                try:
                    cantidades_cargas.remove('Tarimas')
                except:
                    pass

    cargas_cantidad = cargas_cantidad_contenedor.radio('Selecciona las Cantidades:',
                                                       cantidades_cargas,
                                                       index=0)

    tablas = [datos_recibos, datos_embarques, datos_devoluciones]
    nombre_tablas = ['Base de Recibo', 'Base de Embarque', 'Base de Devoluciones']
    nombre_columnas = ['Fecha de Recibo', 'Fecha de Embarque', 'Fecha de Devolución']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and cargas_cantidad:
        cargas_titulo_contenedor.title('Cargas Operativas de ' + cargas_cantidad)

        fecha_min = obtener_fecha_minmax([],
                                         datos_recibos['Fecha de Recibo'],
                                         datos_embarques['Fecha de Embarque'],
                                         datos_devoluciones['Fecha de Devolución'],
                                         True)

        fecha_max = obtener_fecha_minmax([],
                                         datos_recibos['Fecha de Recibo'],
                                         datos_embarques['Fecha de Embarque'],
                                         datos_devoluciones['Fecha de Devolución'],
                                         False)

        cargas_fechas = cargas_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                            value=(fecha_min, fecha_max),
                                                            min_value=fecha_min,
                                                            max_value=fecha_max,
                                                            key='estacionalidad_fechas')

        cargas_periodo = cargas_periodo_contenedor.radio('Selecciona el Período de Tiempo:',
                                                         ['Turno', 'Horario'],
                                                         index=0)



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
                    mostrar_cargas(*calcular_cargas(*preparar_cargas(datos_recibos,
                                                                     datos_embarques,
                                                                     datos_devoluciones,
                                                                     cargas_cantidad,
                                                                     cargas_fechas,
                                                                     cargas_periodo),
                                                     cargas_cortes))

                except IndexError:
                    mostrar_error(6)

            else:
                mostrar_error(5)

        else:
            ocultar_indice()
            try:
                mostrar_cargas(*calcular_cargas(*preparar_cargas(datos_recibos,
                                                                    datos_embarques,
                                                                    datos_devoluciones,
                                                                    cargas_cantidad,
                                                                    cargas_fechas,
                                                                    cargas_periodo)))
            except IndexError:
                mostrar_error(6)


def resumenes_por_dia(datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    resumenes_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('resumenes'):
            resumenes_fechas_contenedor = st.beta_container()

            resumenes_tipo_contenedor = st.beta_container()

            resumenes_cantidad_contenedor = st.beta_container()

            resumenes_minimo_contenedor = st.beta_container()

            resumenes_maximo_contenedor = st.beta_container()

            resumenes_secciones_contenedor = st.beta_container()

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_recibos, datos_recibos, datos_recibos,
              datos_embarques, datos_embarques, datos_embarques,
              datos_devoluciones, datos_devoluciones, datos_devoluciones]

    nombre_tablas = ['Base de Recibo', 'Base de Recibo', 'Base de Recibo',
                     'Base de Embarque', 'Base de Embarque', 'Base de Embarque',
                     'Base de Devoluciones', 'Base de Devoluciones', 'Base de Devoluciones']

    nombre_columnas = ['Unidades Recibidas', 'Cajas Recibidas', 'Tarimas Recibidas',
                       'Unidades Embarcadas', 'Cajas Embarcadas', 'Tarimas Embarcadas',
                       'Unidades Devueltas', 'Cajas Devueltas', 'Tarimas Devueltas']

    resumenes_cantidades = ['Unidades', 'Cajas', 'Tarimas']
    resumenes_tipos = ['Recibos', 'Embarques', 'Devoluciones']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    resumenes_cantidades.remove('Unidades')
                except:
                    pass
            elif nombre_columna.startswith('Cajas'):
                try:
                    resumenes_cantidades.remove('Cajas')
                except:
                    pass
            else:
                try:
                    resumenes_cantidades.remove('Tarimas')
                except:
                    pass

            
            if nombre_tabla.endswith('Recibo'):
                try:
                    resumenes_tipos.remove('Recibos')
                except:
                    pass
            elif nombre_tabla.endswith('Embarque'):
                try:
                    resumenes_tipos.remove('Embarques')
                except:
                    pass
            else:
                try:
                    resumenes_tipos.remove('Devoluciones')
                except:
                    pass


    resumenes_cantidad = resumenes_cantidad_contenedor.radio('Selecciona las Cantidades:',
                                                             resumenes_cantidades,
                                                             index=0)

    resumenes_tipo = resumenes_tipo_contenedor.radio('Selecciona el Tipo de Datos:',
                                                     resumenes_tipos,
                                                     index=0)


    tablas = [datos_recibos, datos_embarques, datos_devoluciones]
    nombre_tablas = ['Base de Recibo', 'Base de Embarque', 'Base de Devoluciones']
    nombre_columnas = ['Fecha de Recibo', 'Fecha de Embarque', 'Fecha de Devolución']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and resumenes_cantidad:
        resumenes_titulo_contenedor.title( f'Resumen de {resumenes_cantidad} por Día')

        fecha_min = obtener_fecha_minmax([],
                                         datos_recibos['Fecha de Recibo'],
                                         datos_embarques['Fecha de Embarque'],
                                         datos_devoluciones['Fecha de Devolución'],
                                         True)

        fecha_max = obtener_fecha_minmax([],
                                         datos_recibos['Fecha de Recibo'],
                                         datos_embarques['Fecha de Embarque'],
                                         datos_devoluciones['Fecha de Devolución'],
                                         False)

        resumenes_fechas = resumenes_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                  value=(fecha_min, fecha_max),
                                                                  min_value=fecha_min,
                                                                  max_value=fecha_max)


        resumenes_columnas_cantidades = [resumenes_cantidad + ' Recibidas',
                                         resumenes_cantidad + ' Embarcadas',
                                         resumenes_cantidad + ' Devueltas']
                                        
        for tabla, tipo, columna_tiempo, columna_cantidades in zip(tablas,
                                                                   resumenes_tipos,
                                                                   nombre_columnas,
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

                    resumenes_secciones = resumenes_secciones_contenedor.number_input('Selecciona el Número de Secciones del Histograma:', 1, 20, 10)
    

                except IndexError:
                    mostrar_error(6)

    # resumenes_columnas_cantidades = [resumenes_cantidad + ' Recibidas',
    #                                  resumenes_cantidad + ' Embarcadas',
    #                                  resumenes_cantidad + ' Devueltas']

    # for tabla, tipo, columna_tiempo, columna_cantidades in zip(resumenes_lista_tablas,
    #                                                                 resumenes_lista_tipos,
    #                                                                 resumenes_columnas_tiempo ,
    #                                                                 resumenes_columnas_cantidades):
    #     if resumenes_tipo == tipo:
    #         ocultar_indice()
    #         try:
    #             tabla_general = calcular_resumen_generales(tabla.loc[(tabla[columna_tiempo].dt.date >= resumenes_fechas[0]) & \
    #                                                                (tabla[columna_tiempo].dt.date <= resumenes_fechas[1]),
    #                                                               [columna_tiempo, columna_cantidades]],
    #                                                      columna_tiempo,
    #                                                      columna_cantidades,
    #                                                      resumenes_fechas)

    #             resumenes_minimo = resumenes_minimo_contenedor.number_input(f'Selecciona el Mínimo de {resumenes_cantidad} a Contar:',
    #                                                                         min_value=tabla_general['Mínimo'].iloc[0].astype(int),
    #                                                                         value=tabla_general['Mínimo'].iloc[0].astype(int),
    #                                                                         max_value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
    #                                                                         step=1)

    #             resumenes_maximo = resumenes_maximo_contenedor.number_input(f'Selecciona el Máximo de {resumenes_cantidad} a Contar:',
    #                                                                         min_value=tabla_general['Mínimo'].iloc[0].astype(int),
    #                                                                         value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
    #                                                                         max_value=tabla_general['Máximo'].iloc[0].astype(int) + 1,
    #                                                                         step=1)

    #             mostrar_resumenes(*calcular_resumenes_acotados(tabla.loc[(tabla[columna_tiempo].dt.date >= resumenes_fechas[0]) & \
    #                                                             (tabla[columna_tiempo].dt.date <= resumenes_fechas[1]),
    #                                                             [columna_tiempo, columna_cantidades]],
    #                                                     resumenes_minimo,
    #                                                     resumenes_maximo,
    #                                                     columna_tiempo,
    #                                                     columna_cantidades,
    #                                                     resumenes_fechas),
    #                                 tabla_general,
    #                                 resumenes_tipo,
    #                                 columna_tiempo,
    #                                 columna_cantidades,
    #                                 resumenes_fechas,
    #                                 resumenes_secciones)
                                    
    #         except IndexError:
                # mostrar_error(6)


def clasificacion_abc_ponderada(datos_sku, datos_inventario, datos_recibos, datos_embarques, datos_devoluciones):
    """
    docstring
    """
    abc_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('abc'):
            abc_cantidad_contenedor = st.beta_container()

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

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_recibos, datos_recibos, datos_recibos,
              datos_embarques, datos_embarques, datos_embarques,
              datos_devoluciones, datos_devoluciones, datos_devoluciones]

    nombre_tablas = ['Base de Recibo', 'Base de Recibo', 'Base de Recibo',
                     'Base de Embarque', 'Base de Embarque', 'Base de Embarque',
                     'Base de Devoluciones', 'Base de Devoluciones', 'Base de Devoluciones']

    nombre_columnas = ['Unidades Recibidas', 'Cajas Recibidas', 'Tarimas Recibidas',
                       'Unidades Embarcadas', 'Cajas Embarcadas', 'Tarimas Embarcadas',
                       'Unidades Devueltas', 'Cajas Devueltas', 'Tarimas Devueltas']

    cantidades_abc = ['Unidades', 'Cajas', 'Tarimas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    cantidades_abc.remove('Unidades')
                except:
                    pass
            elif nombre_columna.startswith('Cajas'):
                try:
                    cantidades_abc.remove('Cajas')
                except:
                    pass
            else:
                try:
                    cantidades_abc.remove('Tarimas')
                except:
                    pass

    abc_cantidad = abc_cantidad_contenedor.radio('Selecciona las Cantidades:',
                                                       cantidades_abc,
                                                       index=0)


    abc_titulo_contenedor.title('Clasificación ABC Ponderada')

    if abc_peso_volumen + abc_peso_variabilidad + abc_peso_frecuencia == 100:
        mostrar_clasificacion_abc(*calcular_clasificacion_abc(datos_embarques[['ID del Producto', abc_cantidad + ' Embarcadas']],
                                                              abc_cantidad,
                                                              abc_peso_volumen,
                                                              abc_peso_frecuencia,
                                                              abc_peso_variabilidad),
                                  datos_embarques.loc[(pd.to_datetime(datos_embarques['Fecha de Embarque'], errors='coerce').notna()), ['Fecha de Embarque']])

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
    usar_sr = False
    if datos_sku['Clasificación ABC de Sintec'].str.contains('SR').any():

        with st.sidebar.beta_expander('Configuración de Análisis'):
            comparacion_abc_cliente_sr_contenedor = st.beta_container()
        
        usar_sr = comparacion_abc_cliente_sr_contenedor.checkbox("Ocultar valores 'SR' de la Clasificación ABC de Sintec")


    if usar_sr:
        mostrar_comparacion_cliente_absoluta(datos_sku.loc[~datos_sku['Clasificación ABC de Sintec'].str.contains('SR'),
                                            ['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
        mostrar_comparacion_cliente_porcentual(datos_sku.loc[~datos_sku['Clasificación ABC de Sintec'].str.contains('SR'),
                                            ['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
    else:
        mostrar_comparacion_cliente_absoluta(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])
        mostrar_comparacion_cliente_porcentual(datos_sku[['Clasificación ABC del Cliente', 'Clasificación ABC de Sintec']])


def comparacion_abc_inventario(datos_sku, datos_inventario, datos_embarques):
    """
    docstring
    """
    comparacion_abc_inventario_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('comparacion_abc_inventario'):
            comparacion_abc_inventario_fechas_contenedor = st.beta_container()

            comparacion_abc_inventario_cantidad_contenedor = st.beta_container()
            
            comparacion_abc_inventario_tipo_contenedor = st.beta_container()

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_inventario, datos_inventario, datos_inventario,
              datos_embarques, datos_embarques, datos_embarques]

    nombre_tablas = ['Foto de Inventarios', 'Foto de Inventarios', 'Foto de Inventarios',
                     'Base de Embarque', 'Base de Embarque', 'Base de Embarque']

    nombre_columnas = ['Unidades de Inventario', 'Cajas de Inventario', 'Tarimas de Inventario',
                       'Unidades Embarcadas', 'Cajas Embarcadas', 'Tarimas Embarcadas']
    
    cantidades_comparacion_abc_inventario= ['Unidades', 'Cajas', 'Tarimas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    cantidades_comparacion_abc_inventario.remove('Unidades')
                except:
                    pass
            elif nombre_columna.startswith('Cajas'):
                try:
                    cantidades_comparacion_abc_inventario.remove('Cajas')
                except:
                    pass
            else:
                try:
                    cantidades_comparacion_abc_inventario.remove('Tarimas')
                except:
                    pass

    comparacion_abc_inventario_cantidad = comparacion_abc_inventario_cantidad_contenedor.radio('Selecciona las Cantidades:',
                                                                       cantidades_comparacion_abc_inventario,
                                                                       index=0)


    tablas = [datos_inventario, datos_embarques]
    nombre_tablas = ['Foto de Inventarios', 'Base de Embarque']
    nombre_columnas = ['Fecha de Inventario', 'Fecha de Embarque']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and comparacion_abc_inventario_cantidad:
        comparacion_abc_inventario_titulo_contenedor.title('Comparativo de Clasificación ABC de Embarques vs Inventarios')

        fecha_min = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         True)

        fecha_max = obtener_fecha_minmax(datos_inventario['Fecha de Inventario'],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         False)

        comparacion_abc_inventario_fechas = comparacion_abc_inventario_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                            value=(fecha_min, fecha_max),
                                                                            min_value=fecha_min,
                                                                            max_value=fecha_max)

        comparacion_abc_inventario_tipo = comparacion_abc_inventario_tipo_contenedor.radio('Selecciona el Tipo de Análisis:',
                                                   ['Por Sumatoria', 'Por Promedio', 'Por Última Foto de Inventario'],
                                                   index=0)


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


def distribucion_volumen_mensual(datos_sku, datos_embarques, datos_recibos, datos_inventario):
    """
    docstring
    """
    volumen_mensual_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):

        with st.form('volumen_mensual'):
            volumen_mensual_fechas_contenedor = st.beta_container()

            volumen_mensual_secciones_contenedor = st.beta_container()

            volumen_mensual_cuartiles_contenedor = st.beta_container()

            st.form_submit_button("Calcular Análisis")

    tablas = [datos_embarques, datos_inventario, datos_recibos]

    nombre_tablas = ['Base de Embarque', 'Foto de Inventarios', 'Base de Recibo']

    nombre_columnas = ['Unidades Embarcadas', 'Unidades de Inventario', 'Unidades Recibidas']
    

    cantidades_volumen_mensual = ['Unidades']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Unidades'):
                try:
                    cantidades_volumen_mensual.remove('Unidades')
                except:
                    pass


    tablas = [datos_embarques]
    nombre_tablas = ['Base de Embarque']
    nombre_columnas = ['Fecha de Embarque']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and cantidades_volumen_mensual:
        volumen_mensual_titulo_contenedor.title('Distribución del Volumen Mensual Embarcado')

        fecha_min = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         True)

        fecha_max = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         False)

        volumen_mensual_fechas = volumen_mensual_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                            value=(fecha_min, fecha_max),
                                                                            min_value=fecha_min,
                                                                            max_value=fecha_max)

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





    # with st.sidebar.beta_expander('Configuración de Análisis'):
    #     volumen_mensual_fechas_contenedor = st.beta_container()
    #     volumen_mensual_secciones_contenedor = st.beta_container()
    #     volumen_mensual_cuartiles_contenedor = st.beta_container()



    # if lista_fechas_errores:
    #     for error in lista_fechas_errores:
    #         mostrar_error(*error)
    # else:
    #     fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=True)

    #     fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=False)

    #     volumen_mensual_fechas = volumen_mensual_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
    #                                                                             value=(fecha_min, fecha_max),
    #                                                                             min_value=fecha_min,
    #                                                                             max_value=fecha_max,
    #                                                                             key='volumen_mensual_fechas')

    #     try:
    #         volumen_mensual_valores_cuartiles = calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
    #                                                                           datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
    #                                                                                               (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
    #                                                                                              ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']])\
    #                                                                                                  ['Volumen Promedio Mensual'].quantile([0, .25, .5, .75, 1]).tolist()

    #         volumen_mensual_valores_cuartiles[4] += 1

    #         volumen_mensual_cuartiles = volumen_mensual_cuartiles_contenedor.checkbox('Seleccionar Secciones por Cuartiles')

    #         if volumen_mensual_cuartiles:
    #             volumen_mensual_secciones = volumen_mensual_secciones_contenedor.number_input("Selecciona el Número de Secciones del Volumen Promedio Mensual:",
    #                                                                                             min_value=4,
    #                                                                                             max_value=4,
    #                                                                                             value=4)
    #         else:
    #             volumen_mensual_secciones = volumen_mensual_secciones_contenedor.number_input("Selecciona el Número de Secciones del Volumen Promedio Mensual:",
    #                                                                                             min_value=1,
    #                                                                                             max_value=10,
    #                                                                                             value=1,
    #                                                                                             step=1)
    #         volumen_mensual_cortes = []
    #         for index in range(volumen_mensual_secciones +  1):
    #             if volumen_mensual_cuartiles:
    #                 corte = volumen_mensual_secciones_contenedor.number_input(f'Corte de Volumen Promedio Mensual {index + 1}:',
    #                                                                             min_value=int(volumen_mensual_valores_cuartiles[0]),
    #                                                                             max_value=int(volumen_mensual_valores_cuartiles[4]),
    #                                                                             value=int(volumen_mensual_valores_cuartiles[index]),
    #                                                                             step=1,
    #                                                                             key=f'volumen_mensual_corte_{index}')
    #             else:
    #                 corte = volumen_mensual_secciones_contenedor.number_input(f'Corte de Volumen Promedio Mensual {index + 1}:',
    #                                                                             min_value=int(volumen_mensual_valores_cuartiles[0]),
    #                                                                             max_value=int(volumen_mensual_valores_cuartiles[4]),
    #                                                                             value=int(volumen_mensual_valores_cuartiles[0]),
    #                                                                             step=1,
    #                                                                             key=f'volumen_mensual_corte_{index}')
                    
    #             volumen_mensual_cortes.append(corte)


    #         if checar_integridad_secciones(volumen_mensual_cortes):

    #             mostrar_distribucion_volumen(*calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
    #                                                                         datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
    #                                                                                             (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
    #                                                                                            ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']],
    #                                                                         True,
    #                                                                         volumen_mensual_cortes),
    #                                          volumen_mensual_fechas)


    #             descargar_distribucion_volumen(calcular_distribucion_volumen(datos_sku[['ID del Producto', 'Volumen x Unidad']],
    #                                                                         datos_embarques.loc[(datos_embarques['Fecha de Embarque'].dt.date >= volumen_mensual_fechas[0]) & \
    #                                                                                             (datos_embarques['Fecha de Embarque'].dt.date <= volumen_mensual_fechas[1]),
    #                                                                                            ['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']],
    #                                                                         True,
    #                                                                         volumen_mensual_cortes)[0])

    #             st.markdown(boton_de_descarga('./data/cedis_distribucion_volumen_mensual.xlsx',
    #                                         'cedis_distribucion_volumen_mensual.xlsx',
    #                                         'Descargar Distribución de Volumen Mensual'),
    #                         unsafe_allow_html=True)

    #         else:
    #             mostrar_error(5)

    #     except IndexError:
    #         mostrar_error(6)


def distribucion_incremental_ordenes(datos_sku, datos_embarques, datos_inventario, datos_recibos):
    """
    docstring
    """
    incremental_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('incremental'):
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

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_embarques, datos_inventario, datos_recibos]

    nombre_tablas = ['Base de Embarque', 'Foto de Inventarios', 'Base de Recibo']

    nombre_columnas = ['Cajas Embarcadas', 'Unidades de Inventario', 'Unidades Recibidas']
    

    cantidades_volumen_mensual = ['Cajas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Cajas'):
                try:
                    cantidades_volumen_mensual.remove('Cajas')
                except:
                    pass


    tablas = [datos_embarques]
    nombre_tablas = ['Base de Embarque']
    nombre_columnas = ['Fecha de Embarque']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and cantidades_volumen_mensual:
        incremental_titulo_contenedor.title('Distribución Incremental de Órdenes')

        fecha_min = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         True)

        fecha_max = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         False)

        incremental_fechas = incremental_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                            value=(fecha_min, fecha_max),
                                                                            min_value=fecha_min,
                                                                            max_value=fecha_max)



    # with st.sidebar.beta_expander('Configuración de Análisis'):
    #     incremental_fechas_contenedor = st.beta_container()
    #     incremental_cliente = st.selectbox('Selecciona el ID del Cliente:',
    #                                         ['Todos'] +  sorted(datos_embarques['ID del Cliente'].unique().tolist()),
    #                                         key='incremental_cliente')
    #     incremental_familia_1_contenedor = st.beta_container()
    #     incremental_checkbox_1_contenedor = st.beta_container()
    #     incremental_familia_2_contenedor = st.beta_container()
    #     incremental_checkbox_2_contenedor = st.beta_container()
    #     incremental_familia_3_contenedor = st.beta_container()
    #     incremental_checkbox_3_contenedor = st.beta_container()


    # lista_fechas_errores = checar_integridad_fechas(fecha_embarque=datos_embarques['Fecha de Embarque'])

    # if lista_fechas_errores:
    #     for error in lista_fechas_errores:
    #         mostrar_error(*error)
    # else:
    #     fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=True)

    #     fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=False)

    #     incremental_fechas = incremental_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
    #                                                                     value=(fecha_min, fecha_max),
    #                                                                     min_value=fecha_min,
    #                                                                     max_value=fecha_max,
    #                                                                     key='incremental_fechas')

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


def distribucion_comparacion(datos_sku, datos_embarques, datos_inventario, datos_recibos):
    """
    docstring
    """

    comparacion_titulo_contenedor = st.beta_container()

    with st.sidebar.beta_expander('Configuración de Análisis'):
        with st.form('comparacion'):
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

            st.form_submit_button("Calcular Análisis")


    tablas = [datos_embarques, datos_inventario, datos_recibos]

    nombre_tablas = ['Base de Embarque', 'Foto de Inventarios', 'Base de Recibo']

    nombre_columnas = ['Cajas Embarcadas', 'Unidades de Inventario', 'Unidades Recibidas']
    

    cantidades_comparacion = ['Cajas']
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_numerica(nombre_tabla, nombre_columna, tabla[nombre_columna])
        
        if error and error[0] == 9:
            mostrar_advertencia(*error)

        if error and error[0] == 10:
            mostrar_error(*error)

            if nombre_columna.startswith('Cajas'):
                try:
                    cantidades_comparacion.remove('Cajas')
                except:
                    pass


    tablas = [datos_embarques]
    nombre_tablas = ['Base de Embarque']
    nombre_columnas = ['Fecha de Embarque']
    
    usar_fechas = True
    for tabla, nombre_tabla, nombre_columna in zip(tablas, nombre_tablas, nombre_columnas):
        error = checar_integridad_fechas(nombre_tabla, nombre_columna, tabla[nombre_columna])

        if error and error[0] == 11:
            mostrar_advertencia(*error)

        if error and error[0] == 12:
            mostrar_error(*error)
            usar_fechas = False


    if usar_fechas and cantidades_comparacion:
        comparacion_titulo_contenedor.title('Comparación de Embarques Completos, Incompletos y Mixtos')

        fecha_min = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         True)

        fecha_max = obtener_fecha_minmax([],
                                         [],
                                         datos_embarques['Fecha de Embarque'],
                                         [],
                                         False)

        comparacion_fechas = comparacion_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
                                                                            value=(fecha_min, fecha_max),
                                                                            min_value=fecha_min,
                                                                            max_value=fecha_max)







    # with st.sidebar.beta_expander('Configuración de Análisis'):
    #     comparacion_fechas_contenedor = st.beta_container()
    #     comparacion_cliente = st.selectbox('Selecciona el ID del Cliente:',
    #                                         ['Todos'] +  sorted(datos_embarques['ID del Cliente'].unique().tolist()),
    #                                         key='comparacion_cliente')
    #     comparacion_familia_1_contenedor = st.beta_container()
    #     comparacion_checkbox_1_contenedor = st.beta_container()
    #     comparacion_familia_2_contenedor = st.beta_container()
    #     comparacion_checkbox_2_contenedor = st.beta_container()
    #     comparacion_familia_3_contenedor = st.beta_container()
    #     comparacion_checkbox_3_contenedor = st.beta_container()


    # lista_fechas_errores = checar_integridad_fechas(fecha_embarque=datos_embarques['Fecha de Embarque'])

    # if lista_fechas_errores:
    #     for error in lista_fechas_errores:
    #         mostrar_error(*error)
    # else:
    #     fecha_min = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=True)

    #     fecha_max = obtener_fecha_minmax(fecha_embarque=datos_embarques['Fecha de Embarque'],
    #                                      obten_min=False)

    #     comparacion_fechas = comparacion_fechas_contenedor.date_input('Selecciona el Rango de Fechas:',
    #                                                                     value=(fecha_min, fecha_max),
    #                                                                     min_value=fecha_min,
    #                                                                     max_value=fecha_max,
    #                                                                     key='comparacion_fechas')

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


def densidad_pickeo(datos_sku, datos_embarques):
    st.title('Densidad de Pickeo')

    # mostrar_densidad_pickeo(*
    calcular_densidad_pickeo(datos_sku[['ID del Producto', 'Volumen x Unidad', 'Zona de Completitud']],
                             datos_embarques[['ID del Producto', 'Unidades Embarcadas', 'Fecha de Embarque']])
                                                    #   ,
                                                                # True,
                                                                # volumen_mensual_cortes
                                                                # ),
                                    # volumen_mensual_fechas
                                    # )

    
    st.markdown(boton_de_descarga('./data/cedis_densidad_de_pickeo.xlsx',
                                    'cedis_densidad_de_pickeo.xlsx',
                                    'Descarga aquí el resultado del análisis'),
                unsafe_allow_html=True)


def almacenamiento_picking(datos_sku, datos_embarques):
    st.title('Espacio de Almacenamiento de Picking')

    ocultar_indice()
    calcular_almancenamiento_picking(datos_sku[['ID del Producto', 'Cajas x Tarima']],
                                     datos_embarques[['ID del Producto', 'Fecha de Embarque', 'Cajas Embarcadas']])

    st.markdown(boton_de_descarga('./data/cedis_almacenamiento_picking.xlsx',
                                    'cedis_almacenamiento_picking.xlsx',
                                    'Descarga aquí el resultado del análisis'),
                unsafe_allow_html=True)


def pedidos_picking(datos_sku, datos_embarques):
    st.title('Espacio de Pedidos de Picking')
    
    ocultar_indice()
    calcular_pedidos_picking(datos_sku[['ID del Producto', 'Cajas x Tarima']],
                             datos_embarques[['ID del Producto', 'Pedido', 'Fecha de Embarque', 'Cajas Embarcadas']])

    st.markdown(boton_de_descarga('./data/cedis_pedidos_picking.xlsx',
                                    'cedis_pedidos_picking.xlsx',
                                    'Descarga aquí el resultado del análisis'),
                unsafe_allow_html=True)


def handling_mix_profile(datos_sku, datos_embarques):
    st.title('Handling Mix Profile')
    
    # ocultar_indice()
    calcular_handling_mix_profile(datos_sku[['ID del Producto', 'Unidades x Caja']],
                                  datos_embarques[['ID del Producto', 'Pedido', 'Unidades Embarcadas']])

    st.markdown(boton_de_descarga('./data/cedis_handling_mix_profile.xlsx',
                                    'cedis_handling_mix_profile.xlsx',
                                    'Descarga aquí el resultado del análisis'),
                unsafe_allow_html=True)


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
                                 10: 'Distribución Completa/Parcial/Mixta',
                                #  11: 'Market Basket Análisis',
                                 12: 'Densidad de Pickeo',
                                 13: 'Espacio de Almacenamiento de Picking',
                                 14: 'Espacio de Pedidos de Picking',
                                 15: 'Handling Mix Profile'}
                                 
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
                cargas_operativas(tabla_recibos, tabla_embarques, tabla_devoluciones)
                
            elif analisis_seleccionado[0] == 4:
                resumenes_por_dia(tabla_recibos, tabla_embarques, tabla_devoluciones)

            elif analisis_seleccionado[0] == 5:
                clasificacion_abc_ponderada(tabla_sku, tabla_inventario, tabla_recibos, tabla_embarques, tabla_devoluciones)

            elif analisis_seleccionado[0] == 6:
                comparacion_abc_cliente(tabla_sku)

            elif analisis_seleccionado[0] == 7:
                comparacion_abc_inventario(tabla_sku, tabla_inventario, tabla_embarques)
                
            elif analisis_seleccionado[0] == 8:
                distribucion_volumen_mensual(tabla_sku, tabla_embarques, tabla_recibos, tabla_inventario)

            elif analisis_seleccionado[0] == 9:
                distribucion_incremental_ordenes(tabla_sku, tabla_embarques, tabla_inventario, tabla_recibos)
                            
            elif analisis_seleccionado[0] == 10:
                distribucion_comparacion(tabla_sku, tabla_embarques, tabla_inventario, tabla_recibos)

            elif analisis_seleccionado[0] == 12:
                densidad_pickeo(tabla_sku, tabla_embarques)

            elif analisis_seleccionado[0] == 13:
                almacenamiento_picking(tabla_sku, tabla_embarques)

            elif analisis_seleccionado[0] == 14:
                pedidos_picking(tabla_sku, tabla_embarques)    

            elif analisis_seleccionado[0] == 15:
                handling_mix_profile(tabla_sku, tabla_embarques)

    else:
        st.success('Para hacer uso correcto de la herramienta, descarga la' + 
                   ' siguiente plantilla base y llena las columnas con los datos correspondientes:')

        st.markdown(boton_de_descarga('./data/plantilla.xlsx',
                                      'plantilla.xlsx',
                                      'Descarga aquí la plantilla'),
                    unsafe_allow_html=True)


if __name__ == "__main__":
        main()
