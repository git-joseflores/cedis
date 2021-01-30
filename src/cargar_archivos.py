import pandas as pd
import streamlit as st

# Nombre de todas las tablas/hojas del archivo Excel.
nombres_tablas = ['Información SKU',
                  'Foto de Inventarios',
                  'Base de Recibo',
                  'Base de Embarque',
                  'Base de Devoluciones']

# Columnas de la tabla de Información SKU.
columnas_sku = ['Clave',
                'Nombre SKU',
                'Clasificación ABC Cliente',
                'Clasificación ABC Sintec',
                'Política de Inventario',
                'Volumen x Pieza',
                'Peso x Pieza',
                'Piezas x Caja',
                'Peso x Caja',
                'Volumen x Caja',
                'Cajas x Tarima',
                'ID Categoría',
                'Categoría',
                'ID Subcategoría',
                'Sub-Categoría',
                'Familia Almacén I',
                'Familia Almacén II',
                'Familia Almacén III',
                'Zona de Completitud',
                'Modo de Almacenamiento',
                'Densidad de Pickeo']

# Columnas de la tabla de Foto de Inventarios.
columnas_inventario = ['ID Producto',
                       'Descripción Producto',
                       'Unidades de Inventario',
                       'Cajas de Inventario',
                       'Tarimas de Inventario',
                       'Semana',
                       'Mes']

# Columnas de la tabla de Base de Recibo.
columnas_recibos = ['ID Proveedor',
                    'Nombre Proveedor',
                    'Pedido',
                    'Línea',
                    'ID Producto',
                    'Descripción Producto',
                    'Unidades Recibidas',
                    'Cajas Recibidas',
                    'Tarimas Recibidas',
                    'Fecha Recibo',
                    'Horario Recibo',
                    'Turno Recibo']

# Columnas de la tabla de Base de Embarque.
columnas_embarques = ['ID Canal',
                      'Canal',
                      'ID Cliente',
                      'Nombre Cliente',
                      'ID Destino',
                      'Nombre Destino',
                      'Pedido',
                      'Línea',
                      'ID Producto',
                      'Descripción Producto',
                      'Unidades Embarcadas',
                      'Cajas Embarcadas',
                      'Tarimas Embarcadas',
                      'Fecha Embarque',
                      'Horario Embarque',
                      'Turno Embarque']

# Columnas de la tabla de Base de Devoluciones.
columnas_devoluciones = ['ID Canal',
                         'Canal',
                         'ID Cliente',
                         'Nombre Cliente',
                         'ID Destino',
                         'Nombre Destino',
                         'Pedido',
                         'Línea',
                         'ID Producto',
                         'Descripción Producto',
                         'Unidades Devueltas',
                         'Cajas Devueltas',
                         'Tarimas Devueltas',
                         'Fecha Devolución',
                         'Horario Devolución',
                         'Turno Devolución']

# Lista de todas las columnas de cada tabla.
columnas_tablas = [columnas_sku,
                   columnas_inventario,
                   columnas_recibos,
                   columnas_embarques,
                   columnas_devoluciones]

@st.cache
def leer_archivo_a_tablas(archivo):
    """
    Funcion que lee un archivo excel a las tablas que se usaran en analisis posteriores.
    Si existe algun error al leer el archivo, se genera una lista de tuplas de errores en su lugar.
    Se regresean tanto las tablas leidas como los errores encontrados.
    """
    lista_tablas = []
    lista_errores = []
    
    # Dado el formato de nombre y columnas de cada tabla, se lee cada una de ellas a 
    # partir de su hoja en el archivo excel.
    for hoja, columnas in zip(nombres_tablas, columnas_tablas):
        try:
            tabla = pd.read_excel(archivo,
                                  engine="openpyxl",
                                  sheet_name=hoja) 

            # Despues, se checa que no se agreguen columnas con nombres vacios, o renglones 
            # sin informacion.
            tabla = tabla.loc[:, ~tabla.columns.str.contains('^Unnamed')].dropna(how='all')
            
            # Mas adelante, se checa que la tabla leida contenga las columnas indicadas.
            lista_errores_columnas = checar_columnas(tabla.columns.values.tolist(), columnas, hoja)
            if lista_errores_columnas:
                # Si no se encuentran las columnas indicadas, se agregan los errores encontrados a
                # una lista general de errores.
                lista_errores.extend(lista_errores_columnas)
            else:
                # Si se encuentran las columnas indicadas, se agrega la tabla a una lista general de tablas.
                lista_tablas.append(tabla)

        except KeyError:
            # Si no se encuentra una tabla en las hojas del archivo exccel, se agrega una tupla
            # con el codigo y la informacion del error encontrado a una lista general de errores.
            lista_errores.append((1, hoja))

    
    # Si regresean tanto las tablas leidas como los errores encontrados.
    return lista_tablas, lista_errores


def checar_columnas(tabla_columnas, lista_columnas, hoja):
    """
    Funcion que checa que las columnas de una tabla [tabla_columnas] concuerden con 
    los dados en una lista [lista_columnas].

    Por cada columna de la lista que no se encuentre en la tabla, se agrega una tupla
    con el codigo y la informacion del error encontrado a una lista de errores.
    Al terminar de checar todas las columnas, se regresa la lista de errores encontrados.

    Si todas las columnas de la lista se encuentran en la tabla,
    se regresa una lista de errores vacia.
    """
    lista_errores_columnas = []
    for columna in lista_columnas:
        if columna not in tabla_columnas:
            lista_errores_columnas.append((2, hoja, columna))
    return lista_errores_columnas