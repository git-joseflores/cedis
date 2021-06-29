import base64
import numpy as np
import pandas as pd
import re
import streamlit as st
import uuid



# st.write(abc_volumen_conteo.astype('object'))
# print('Empty Counting', columna.isnull().values.sum())


# Diccionario de Errores y Advertencias
dict_errores_advertencias = {1: 'Error 001: No se encontró una hoja de cálculo llamada "*" en el archivo cargado.',
                             2: 'Error 002: La siguiente columna no se encontró en "*": "*".',
                             3: 'Error 003: Se encontraron datos vacíos en la siguiente columna de "*": "*".',
                             4: 'Error 004: Se encontraron datos desconocidos en la siguiente columna de "*": "*".',
                             5: 'Error 005: Las secciones de horario seleccionadas se superponen entre sí.',
                             6: 'Error 006: Selecciona un rango de fechas válido.',
                             7: 'Error 007: Selecciona una combinación de pesos porcentuales para la clasificación ABC ponderada igual a 100%.',
                             8: 'Error 008: Existen valores de "ID del Producto" en "Foto de Inventarios" que no se encuentran en "Información de SKU"',
                             # Errores de Integridad Numerica
                             9: 'Existen datos no numéricos en la columna "*" de "*". Estos datos erróneos no superan el 5% del total de datos.',
                             10: 'Verifique la columna "*" en "*". Existen valores no numéricos que sobrepasan el 5% del total de datos.',
                             # Errores de Integridad de Fechas
                             11: 'Existen datos que no son fechas en la columna "*" de "*". Estos datos erróneos no superan el 5% del total de datos.',
                             12: 'Verifique la columna "*" en "*". Existen valores que no son fechas que sobrepasan el 5% del total de datos.'}


def mostrar_error(codigo, *args):
    """
    Funcion que toma un codigo de error y muestra su contenido con los argumentos dados.

            Parámetros:
                    codigo (integer): Numero a buscar en el diccionario de errores.
                    *args (tuple): Tupla con los argumentos a modificar en el texto de error.
                    
            Valor de Retorno:
                    Ninguno.
    """
    error = dict_errores_advertencias[codigo]
    for arg in args:
        error = error.replace('*', arg, 1)
    st.error(error)


def mostrar_advertencia(codigo, *args):
    """
    Funcion que toma un codigo de advertencia y muestra su contenido con los argumentos dados.

            Parámetros:
                    codigo (integer): Numero a buscar en el diccionario de advertencias.
                    *args (tuple): Tupla con los argumentos a modificar en el texto de advertencia.
                    
            Valor de Retorno:
                    Ninguno.
    """
    advertencia = dict_errores_advertencias[codigo]
    for arg in args:
        advertencia = advertencia.replace('*', arg, 1)
    st.warning(advertencia)


def ocultar_indice():
    """
    Funcion que oculta el indice de la tabla a mostrar a continuacion.
    
            Parámetros:
                    Ninguno.

            Valor de Retorno:
                    Ninguno.
    """
    st.markdown("""
                <style>
                table td:nth-child(1) {
                    display: none
                }
                table th:nth-child(1) {
                    display: none
                }
                </style>""",
                unsafe_allow_html=True)
                

def boton_de_descarga(url_descarga, nombre_de_descarga, texto_boton):
    """
    Funcion que genera un boton de descarga basado en el url de un archivo, especificando el nombre de
    la descarga y el texto en el boton.
    
            Parámetros:
                    url_descarga (string): URL relativo donde se encuentra el archivo a desacargar.
                    nombre_de_descarga (string): Nombre que se desea dar al archivo a descargar.
                    texto_boton (string): Texto que se busca poner en el boton de descarga.
                    
            Valor de Retorno:
                    boton_html (string): Texto con formato html donde se ha configurado el boton de descarga.
    """
    with open(url_descarga, 'rb') as lector_archivo:
        objeto_a_descargar = lector_archivo.read()

    try:
        # Conversiones de strings <-> bytes son necesarias
        objeto_b64 = base64.b64encode(objeto_a_descargar.encode()).decode()

    except AttributeError as e:
        objeto_b64 = base64.b64encode(objeto_a_descargar).decode()

    boton_uuid = str(uuid.uuid4()).replace('-', '')
    boton_id = re.sub('\d+', '', boton_uuid)

    custom_css = f""" 
        <style>
            #{boton_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: absolute;
                top:  50%;
                left: 50%;
                transform: translate(-50%,-50%);
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{boton_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{boton_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    boton_html = custom_css + f'<a download="{nombre_de_descarga}" \
                 id="{boton_id}" href="data:file/txt;base64,{objeto_b64}">{texto_boton}</a><br></br>'

    return boton_html


def checar_integridad_numerica(nombre_tabla, nombre_columna, columna):
    """
    Regresa una lista de los errores encontrados al verificar que la columna tenga valores vacíos o no numéricos.

            Parámetros:
                    nombre_tabla (string): Nombre de la tabla a la que pertenece la cantidad a checar.
                    nombre_columna (string): Nombre de la columna de cantidad a checar.
                    columna (Pandas Series): Columna de valores correspondientes a la cantidad a checar.

            Valor de Retorno:
                    error (tuple o None): Error obtenido al verificar valores vacíos y no numéricos.
    """
    porcentaje_integridad = pd.to_numeric(columna, errors='coerce').notna().sum() / columna.size
    
    error = None
    if porcentaje_integridad < 0.95:
        error = (10, nombre_columna, nombre_tabla)
    elif porcentaje_integridad < 1:
        error =  (9, nombre_columna, nombre_tabla)

    return error


def checar_integridad_fechas(nombre_tabla, nombre_columna, columna):
    """
    Regresa una lista de los errores encontrados al verificar que la columna tenga valores vacíos o que no sean fechas.

            Parámetros:
                    nombre_tabla (string): Nombre de la tabla a la que pertenece las fechas a checar.
                    nombre_columna (string): Nombre de las fechas a checar.
                    columna (Pandas Series): Columna de valores correspondientes a las fechas a checar.

            Valor de Retorno:
                    error (tuple o None): Error obtenido al verificar valores vacíos y no correspondiente a fechas.
    """
    porcentaje_integridad = pd.to_datetime(columna, errors='coerce').notna().sum() / columna.size

    error = None
    if porcentaje_integridad < 0.95:
        error = (12, nombre_columna, nombre_tabla)
    elif porcentaje_integridad < 1:
        error = (11, nombre_columna, nombre_tabla)

    return error


@st.cache
def obtener_fecha_minmax(fecha_inventario=[], fecha_recibo=[], fecha_embarque=[], fecha_devolucion=[], obten_min=False):
    """
    Obtiene el minimo o maximo total de un grupo de fechas.

            Parámetros:
                    fecha_inventario (Pandas Series): Columna de datos correspondiente a las fechas de inventario.
                    fecha_recibo (Pandas Series): Columna de datos correspondiente a las fechas de recibos.
                    fecha_embarque (Pandas Series): Columna de datos correspondiente a las fechas de embarques.
                    fecha_devolucion (Pandas Series): Columna de datos correspondiente a las fechas de devolucion.
                    obten_min (bool): Valor que indica si se obtiene el minimo o maximo de todas las fechas.

            Valor de Retorno:
                    resultado (string): Valor minimo o maximo entre todas las fechas dadas.
    """
    fechas_min_max = []
    for fecha_en_turno in (fecha_inventario, fecha_recibo, fecha_embarque, fecha_devolucion):
        if isinstance(fecha_en_turno, pd.Series):
            if obten_min:
                fechas_min_max.append(fecha_en_turno[pd.to_datetime(fecha_en_turno, errors='coerce').notna()].min())
            else:
                fechas_min_max.append(fecha_en_turno[pd.to_datetime(fecha_en_turno, errors='coerce').notna()].max())

    if obten_min:
        resultado = min(fechas_min_max)
    else:
        resultado = max(fechas_min_max)

    return resultado








def checar_valores_vacios_columna(columna):
    """
    Regresa un valor booleano dependiendo si la columna tiene datos vacíos o no.

            Parámetros:
                    columna (Pandas Series): Columna con datos.

            Valor de Retorno:
                    columna_vacia (bool): Valor obtenido al determinar si la columna tiene datos vacíos o no.
    """
    columna_vacia = columna.isnull().values.any()
    return columna_vacia



@st.cache
def checar_integridad_secciones(secciones):
    """
    docstring
    """
    es_incremental = True
    seccion_comparacion = secciones[0]
    for seccion in secciones[1:]:
        if seccion_comparacion >= seccion:
            es_incremental = False
            break
        seccion_comparacion = seccion
    return es_incremental


def variable_a_binario(variable):
    if variable > 0:
        return 1
    return 0
