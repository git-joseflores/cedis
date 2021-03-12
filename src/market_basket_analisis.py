import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import streamlit as st
from src.utilidades import variable_a_binario


# @st.cache
def calcular_market_basket_analisis(datos, min_apoyo, metrica, umbral):
    """
    docstring
    """
    datos['Pedido'] = datos['Pedido'].astype('str')
    datos = datos.groupby(['Pedido', 'ID del Producto'])['Unidades Embarcadas'].sum().unstack().reset_index().fillna(0).set_index('Pedido')
    datos = datos.applymap(variable_a_binario)

    datasets_frecuentes = apriori(datos, min_support=min_apoyo, use_colnames=True)

    st.write(datasets_frecuentes)


    
    datasets_reglas = association_rules(datasets_frecuentes, metric='lift', min_threshold=umbral)

    st.write(datasets_reglas)
    
