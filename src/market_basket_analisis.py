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
    # st.write(datos)

    datasets_frecuentes = apriori(datos, min_support=0.1, use_colnames=True)
    # st.table(datasets_frecuentes)


    
    datasets_reglas = association_rules(datasets_frecuentes, metric='lift', min_threshold=0.8)
    # st.write(datasets_reglas)
    

    # with pd.ExcelWriter("./data/market_basket_analisis.xlsx") as writer:
    #     datasets_reglas.to_excel(writer, sheet_name="Market Basket Analisis", index=False)
        # datos_inventario.to_excel(writer, sheet_name="Foto de Inventarios", index=False)
        # datos_recibos.to_excel(writer, sheet_name="Base de Recibo", index=False)
        # datos_embarques.to_excel(writer, sheet_name="Base de Embarque", index=False)
        # datos_devoluciones.to_excel(writer, sheet_name="Base de Devoluciones", index=False)