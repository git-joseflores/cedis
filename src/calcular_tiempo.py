import streamlit as st

@st.cache(suppress_st_warning=True)
def calcular_valores_timedelta(time_delta):
    """
    docstring
    """
    return time_delta.days, time_delta.seconds // 3600, time_delta.seconds // 60 % 60


def calcular_periodo(recibo):
    """
    docstring
    """
    periodo_tiempo = recibo.loc[:, 'Fecha Recibo'].max()\
        - recibo.loc[:, 'Fecha Recibo'].min()

    st.subheader('Periodo de Análisis:')
    dias, horas, minutos = calcular_valores_timedelta(periodo_tiempo)
    st.write(f'{dias} días, {horas} horas, {minutos} minutos. \n ')
    return dias
