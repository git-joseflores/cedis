import base64
import numpy as np
import pandas as pd
import re
import streamlit as st
import uuid

errores = {1: 'Error 001: No se encontró una hoja de cálculo llamada "*" en el archivo cargado.',
           2: 'Error 002: La siguiente columna no se encontró en "*": "*".',
           3: 'Error 003: Se encontraron datos vacíos en la siguiente columna de "*": "*".',
           4: 'Error 004: Se encontraron datos desconocidos en la siguiente columna de "*": "*".',
           5: 'Error 005: Las secciones de horario seleccionadas se superponen entre sí.',
           6: 'Error 006: Selecciona un rango de fechas válido.',
           7: 'Error 007: Selecciona una combinación de pesos porcentuales para la clasificación ABC ponderada igual a 100%.',
           8: 'Error 008: Existen valores de "ID del Producto" en "Foto de Inventarios" que no se encuentran en "Información de SKU"'}

# st.write(abc_volumen_conteo.astype('object'))

def mostrar_error(codigo, *args):
    """
    Funcion que toma un codigo de error y rellena su contenido con los argumentos dados, para
    despues mostrarlo.
    """
    error = errores[codigo]
    for arg in args:
        error = error.replace('*', arg, 1)
    st.error(error)


def ocultar_indice():
    """
    docstring
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


def checar_valores_vacios_columna(columna):
    """
    DOCSTRING
    """
    if columna.isnull().values.any():
        return True
    return False


def checar_integridad_fecha(datos_fecha):
    """
    DOCSTRING
    """
    lista_errores = []
    columna, nombre_tabla, nombre_columna = datos_fecha
    if checar_valores_vacios_columna(columna):
        lista_errores.append((3, nombre_tabla, nombre_columna))        
    try:
        pd.to_datetime(columna)
    except:
        lista_errores.append((4, nombre_tabla, nombre_columna))
    
    return lista_errores


@st.cache
def checar_integridad_fechas(fecha_inventario=[], fecha_recibo=[], fecha_embarque=[], fecha_devolucion=[]):
    """
    DOCSTRING
    """
    datos_fechas = [(fecha_inventario, 'Foto de Inventarios', 'Fecha de Inventario'),
                    (fecha_recibo, 'Base de Recibo', 'Fecha de Recibo'),
                    (fecha_embarque, 'Base de Embarque', 'Fecha de Embarque'),
                    (fecha_devolucion, 'Base de Devoluciones', 'Fecha de Devolución')]
    
    lista_errores = []
    for datos_fecha in datos_fechas:
        if isinstance(datos_fecha[0], pd.Series):
            lista_errores.extend(checar_integridad_fecha(datos_fecha))
    return lista_errores


@st.cache
def obtener_fecha_minmax(fecha_inventario=[], fecha_recibo=[], fecha_embarque=[], fecha_devolucion=[], obten_min=False):
    """
    DOCSTRING
    """
    fechas_obtenidas = []
    for fecha_en_turno in (fecha_inventario, fecha_recibo, fecha_embarque, fecha_devolucion):
        if isinstance(fecha_en_turno, pd.Series):
            if obten_min:
                fechas_obtenidas.append(fecha_en_turno.min())
            else:
                fechas_obtenidas.append(fecha_en_turno.max())

    if obten_min:
        return min(fechas_obtenidas)
    else:
        return max(fechas_obtenidas)


def boton_de_descarga(url_descarga, nombre_de_descarga, texto_boton):
    """
    Funcion que genera un boton de descarga basada en el url de un archivo,
    especificando el nombre de la descarga y el texto en el boton.
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
