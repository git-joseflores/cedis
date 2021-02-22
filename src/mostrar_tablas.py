import streamlit as st

# Nombre de todas las tablas.
nombres_tablas = ['Información SKU',
                  'Foto de Inventarios',
                  'Base de Recibo',
                  'Base de Embarque',
                  'Base de Devoluciones']

def mostrar_tablas(*args):
    """
    Funcion que muestra el nombre de cada tabla junto a su contenido
    """
    st.title('Mostrar Tablas')
    for nombre, tabla in zip(nombres_tablas, args):
        with st.beta_expander(nombre):
            st.dataframe(tabla)