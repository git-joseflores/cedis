import streamlit as st

errores = {1 : 'Error 001: No existe una hoja de cálculo llamada "*" en el archivo cargado.',
           2 : 'Error 002: La siguiente columna no existe en "*": "*".'}

def mostrar_error(codigo, *args):
    """
    Funcion que toma un codigo de error y rellena su contenido con los argumentos dados, para
    despues mostrarlo.
    """
    error = errores[codigo]
    for arg in args:
        error = error.replace('*', arg, 1)
    st.error(error)