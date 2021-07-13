import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from statistics import NormalDist


# @st.cache
def calcular_handling_mix_profile(datos_sku, datos_embarques):
    """
    docstring
    """
    datos_hmp = pd.merge(datos_sku,
                         datos_embarques,
                         on='ID del Producto',
                         how='outer')
    datos_hmp.fillna(value=0, inplace=True)

    datos_hmp['Fraccion de Cajas Embarcadas'] = datos_hmp['Unidades Embarcadas'] / datos_hmp['Unidades x Caja']
    datos_hmp['Cajas Embarcadas Enteras'] = np.where(datos_hmp['Fraccion de Cajas Embarcadas'] % 1 == 0, datos_hmp['Fraccion de Cajas Embarcadas'], 0)
    datos_hmp['Cajas Completas'] = np.where(datos_hmp['Fraccion de Cajas Embarcadas'] % 1 == 0, 1, 0)

    # st.write(datos_hmp)

    hmp_pedido = datos_hmp.groupby(['Pedido']).agg({'Cajas Completas':sum, 'Pedido':len})
    hmp_pedido.columns = ['Completitud de Pedidos', 'Lineas por Pedido']
    hmp_pedido = hmp_pedido.reset_index()

    hmp_pedido['Completitud de Pedidos en Cajas'] = np.where(hmp_pedido['Completitud de Pedidos'] == hmp_pedido['Lineas por Pedido'], 1, 0)
    hmp_pedido['Completitud de Pedidos Mixto'] = np.where((hmp_pedido['Completitud de Pedidos'] > 0) & \
                                                          (hmp_pedido['Completitud de Pedidos'] != hmp_pedido['Lineas por Pedido']), 1, 0)
    hmp_pedido['Completitud de Pedidos en Unidades'] = np.where(hmp_pedido['Completitud de Pedidos'] == 0, 1, 0)

    
    st.write(hmp_pedido)


    hmp_producto = datos_hmp.groupby(['ID del Producto']).agg({'Cajas Completas':sum, 'Pedido':len})
    hmp_producto.columns = ['Completitud de Pedidos', 'Lineas por Pedido']
    hmp_producto = hmp_producto.reset_index()


    hmp_producto['Completitud de Pedidos en Cajas'] = np.where(hmp_producto['Completitud de Pedidos'] == hmp_producto['Lineas por Pedido'], 1, 0)
    hmp_producto['Completitud de Pedidos Mixto'] = np.where((hmp_producto['Completitud de Pedidos'] > 0) & \
                                                          (hmp_producto['Completitud de Pedidos'] != hmp_producto['Lineas por Pedido']), 1, 0)
    hmp_producto['Completitud de Pedidos en Unidades'] = np.where(hmp_producto['Completitud de Pedidos'] == 0, 1, 0)

    st.write(hmp_producto)


    with pd.ExcelWriter("./data/cedis_handling_mix_profile.xlsx") as writer:
        hmp_pedido.to_excel(writer, sheet_name="Perfil por Pedido", index=False)
        hmp_producto.to_excel(writer, sheet_name="Perfil por Producto", index=False)


