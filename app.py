# Importando Librerias
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import seaborn as sns

@st.cache(suppress_st_warning=True)
def leer_archivo_a_tablas(archivo):
    """
    docstring
    """
    dataframes = pd.read_excel(
        archivo,
        engine="openpyxl",
        sheet_name=[0, 1, 2, 3, 4]
    )

    for dataframe in dataframes.values():
        for col_name in dataframe.columns:
            if col_name.startswith('Unnamed'):
                dataframe.drop(columns=col_name, inplace=True)

    return dataframes[0], dataframes[1], dataframes[2], dataframes[3], dataframes[4]


def mostrar_dataframes(sku, inventario, recibo, embarque, devoluciones):
    """
    docstring
    """
    with st.beta_expander('Información SKU'):
        st.dataframe(sku)

    with st.beta_expander('Foto de Inventarios'):
        st.dataframe(inventario)

    with st.beta_expander('Base de Recibo'):
        st.dataframe(recibo)

    with st.beta_expander('Base de Embaque'):
        st.dataframe(embarque)

    with st.beta_expander('Base de Devoluciones'):
        st.dataframe(devoluciones)


def checar_datos_completos(datos):
    """
    docstring
    """
    return not (datos.isnull().values.any())


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


@st.cache(suppress_st_warning=True)
def preparar_datos_estacionalidad(recibo, embarque, devoluciones, inventario, cantidad):
    """
    docstring
    """
    rec = recibo.loc[:, [cantidad + ' Recibidas', 'Fecha Recibo']]
    emb = embarque.loc[:, [cantidad + ' Embarcadas', 'Fecha Embarque']]
    dev = devoluciones.loc[:, [cantidad + ' Devueltas', 'Fecha Devolución']]
    inv = inventario.loc[:, [cantidad + ' de Inventario', 'Mes']]

    rec.loc[:, 'Fecha Recibo'] = rec.loc[:, 'Fecha Recibo'].dt.strftime('%m')
    emb.loc[:, 'Fecha Embarque'] = emb.loc[:, 'Fecha Embarque'].dt.strftime('%m')
    dev.loc[:, 'Fecha Devolución'] = dev.loc[:, 'Fecha Devolución'].dt.strftime('%m')
    inv.loc[:, 'Mes'] = pd.to_datetime(inv.loc[:, 'Mes'], format='%m')
    inv.loc[:, 'Mes'] = inv.loc[:, 'Mes'].dt.strftime('%m')
    
    datos_completos = checar_datos_completos(rec) and checar_datos_completos(emb) and checar_datos_completos(dev)

    pivot_rec = pd.pivot_table(rec, index='Fecha Recibo', aggfunc='sum').sort_index()
    pivot_emb = pd.pivot_table(emb, index='Fecha Embarque', aggfunc='sum').sort_index()
    pivot_dev = pd.pivot_table(dev, index='Fecha Devolución', aggfunc='sum').sort_index()
    pivot_inv = pd.pivot_table(inv, index='Mes', aggfunc='sum').sort_index()

    pivot_todos = pd.concat([pivot_rec, pivot_emb, pivot_dev, pivot_inv], axis=1)
    pivot_todos['Mes'] = pd.to_datetime(pivot_todos.index, format='%m').month_name()
    
    cols = [
        cantidad + ' Recibidas',
        cantidad + ' Embarcadas', 
        cantidad + ' Devueltas',
        cantidad + ' de Inventario'
    ]
    pivot_comas = pd.DataFrame(columns=['Mes'] + cols)

    for col in cols:
        pivot_comas[col] = pivot_todos.apply(lambda column: "{:,}".format(column[col]), axis=1)

    pivot_comas['Mes'] = pd.to_datetime(pivot_comas.index, format='%m').month_name()

    return pivot_todos, pivot_comas, cantidad, datos_completos


def estacionalidad(datos, datos_comas, cantidad, datos_completos):
    """
    docstring
    """
    if datos_completos:
        st.table(datos_comas)

        cols = [
            cantidad + ' Recibidas',
            cantidad + ' Embarcadas', 
            cantidad + ' Devueltas',
            cantidad + ' de Inventario'
        ]
        datos_fig = pd.melt(datos, id_vars='Mes', var_name='Tipo de Cantidad', value_name=cantidad)
        fig = px.bar(
            datos_fig,
            x='Mes',
            y=cantidad,
            color='Tipo de Cantidad',
            barmode='group',
            color_discrete_map={
                cols[0]: "#231262",
                cols[1]: "#4BA76B",
                cols[2]: "#951E41",
                cols[3]: "#E4B657"
            }
        )
        fig.update_layout(yaxis={'title': ''}, xaxis={'title': ''})
        st.plotly_chart(fig)

        col1, col2, col3 = st.beta_columns(3)
        with col1:
            st.subheader('Rotación de Inventario:')
            rot = datos.loc[:, cols[1]].sum() / datos.loc[:, cols[3]].sum()
            if pd.notnull(rot):
                st.write(rot)
            else:
                st.write('No hay datos.')

        with col2:
            st.subheader('DDI Promedio:')
            ddi = rot * 31
            if pd.notnull(ddi):
                st.write(ddi)
            else:
                st.write('No hay datos.')

        with col3:
            st.subheader('% de Devoluciones:')
            dev_emb = datos.loc[:, cols[2]].sum() / datos.loc[:, cols[1]].sum() * 100
            if pd.notnull(dev_emb):
                st.write(dev_emb)
            else:
                st.write('No hay datos.')
    else:
        st.info('No hay Datos Completos.')


@st.cache(suppress_st_warning=True)
def preparar_datos_cargas_operativas(recibo, embarque, devoluciones, cantidad, periodo, dias):
    """
    docstring
    """
    rec = recibo.loc[:, [cantidad + ' Recibidas', periodo + ' Recibo']]
    emb = embarque.loc[:, [cantidad + ' Embarcadas', periodo + ' Embarque']]
    dev = devoluciones.loc[:, [cantidad + ' Devueltas', periodo + ' Devolución']]
    
    datos_completos = checar_datos_completos(rec) and checar_datos_completos(emb) and checar_datos_completos(dev)

    pivot_rec = pd.pivot_table(rec, index=periodo + ' Recibo', aggfunc='sum').sort_index() / dias
    pivot_emb = pd.pivot_table(emb, index=periodo + ' Embarque', aggfunc='sum').sort_index() / dias
    pivot_dev = pd.pivot_table(dev, index=periodo + ' Devolución', aggfunc='sum').sort_index() / dias
    pivot_todos = pd.concat([pivot_rec, pivot_emb, pivot_dev], axis=1)
    pivot_todos.index.name = 'Turno'

    return pivot_todos, cantidad, datos_completos


def cargas_operativas(datos, cantidad, datos_completos):
    """
    docstring
    """
    if datos_completos:
        st.table(datos)

        datos = datos.reset_index()
        datos['Turno'] = datos['Turno'].astype(str)
        cols = [
            cantidad + ' Recibidas',
            cantidad + ' Embarcadas', 
            cantidad + ' Devueltas'
        ]
        datos_fig = pd.melt(datos, id_vars='Turno', var_name='Tipo de Cantidad', value_name=cantidad)
        fig = px.bar(
            datos_fig,
            x='Turno',
            y=cantidad,
            color='Tipo de Cantidad',
            barmode='group',
            color_discrete_map={
                cols[0]: "#231262",
                cols[1]: "#4BA76B",
                cols[2]: "#951E41"
            }
        )
        fig.update_layout(yaxis={'title': ''})
        st.plotly_chart(fig)
    else:
        st.info('No hay Datos Completos.')


@st.cache(suppress_st_warning=True)
def preparar_datos_resumenes(datos, cantidad, periodo, tipo):
    """
    docstring
    """
    fecha = 'Fecha'
    if tipo == 'Recibos':
        cantidad += ' Recibidas'
        fecha += ' Recibo'
    elif tipo == 'Embarques':
        cantidad += ' Embarcadas'
        fecha += ' Embarque'
    else:
        cantidad += ' Devueltas'
        fecha += ' Devolución'


    pivot_datos = pd.pivot_table(datos, values=cantidad, index=fecha, aggfunc='sum').sort_index()

    return pivot_datos, cantidad, fecha, checar_datos_completos(datos.loc[:, [cantidad, fecha]])


def resumenes(datos, cantidad, fecha, datos_completos, num_secciones):
    """
    docstring
    """
    if datos_completos:
        dict_resumen = {
            'Máximo': datos.max(),
            'Mínimo': datos.min(),
            'Promedio': datos.mean(),
            'Desviación Estándar': datos.std()
        }

        df_resumen = pd.DataFrame.from_dict(dict_resumen)

        # df.head().style.format({"col1": "{:,.0f}", "col2": "{:,.0f}"})
        st.table(df_resumen.head().style.format("{:,.2f}"))
        
        datos = datos.reset_index()

        st.subheader('Box and Whisker')
        datos.loc[:, 'Variable'] = 'Cajas Recibidas'
        fig = px.box(datos, x='Variable', y=cantidad, points="all")
        fig.update_layout(yaxis={'title': ''}, xaxis={'visible': False})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Serie de Tiempo')
        fig = px.line(datos, x=fecha, y=cantidad)
        fig.update_layout(yaxis={'title': ''}, xaxis={'title': ''})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Histograma')
        secciones = np.linspace(datos[cantidad].min(), datos[cantidad].max(), num_secciones + 1)
        datos['Secciones'] = pd.cut(datos[cantidad], secciones, include_lowest=True)
        acumulado = datos['Secciones'].value_counts()
        acumulado = acumulado.sort_index().to_frame().reset_index()
        acumulado.rename(columns={'index': 'Secciones', 'Secciones': 'Conteo'}, inplace=True)
        acumulado["Secciones"] = acumulado["Secciones"].astype("str")
        fig = px.bar(acumulado, x='Secciones', y="Conteo")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info('No hay Datos Completos.')


def main():
    """
    docstring
    """
    st.set_page_config(page_title='CEDIS', page_icon='img/icon.PNG')
    st.sidebar.title('CEDIS')
    file = st.sidebar.file_uploader('Selecciona el Archivo:', type=['xlsx'])

    if file:
        df_sku, df_inventario, df_recibo, df_embarque, df_devoluciones = \
            leer_archivo_a_tablas(file)

        menu_options = [
            'Mostrar Tablas',
            'Estacionalidad',
            'Cargas Operativas',
            'Resúmenes',
            ''
        ]
        analisis = st.sidebar.selectbox(
            'Selecciona el Análisis a Ejecutar:',
            options=menu_options
        )

        if analisis == menu_options[0]:
            st.title(analisis)
            mostrar_dataframes(
                df_sku.head(10),
                df_inventario.head(10),
                df_recibo.head(10),
                df_embarque.head(10),
                df_devoluciones.head(10)
            )

        elif analisis == menu_options[1]:
            estacionalidad_cantidad = st.sidebar.radio(
                'Selecciona las Cantidades a Usar:',
                ['Unidades', 'Cajas', 'Tarimas'],
                index=0
            )

            st.title(analisis + ' por ' + estacionalidad_cantidad)

            calcular_periodo(df_recibo)
            estacionalidad(
                *preparar_datos_estacionalidad(
                    df_recibo,
                    df_embarque,
                    df_devoluciones,
                    df_inventario,
                    estacionalidad_cantidad
                )
            )

        elif analisis == menu_options[2]:
            cargas_cantidad = st.sidebar.radio(
                'Selecciona las Cantidades a Usar:',
                ['Unidades', 'Cajas', 'Tarimas'],
                index=0
            )

            cargas_periodo = st.sidebar.radio(
                'Selecciona el Período de Tiempo a Usar:',
                ['Turno', 'Horario'],
                index=0
            )

            st.title(analisis + ' de ' + cargas_cantidad + ' por ' + cargas_periodo)

            dias = calcular_periodo(df_recibo)
            cargas_operativas(
                *preparar_datos_cargas_operativas(
                df_recibo,
                df_embarque,
                df_devoluciones,
                cargas_cantidad,
                cargas_periodo,
                dias
                )
            )
            
        elif analisis == menu_options[3]:
            resumen_tipo = st.sidebar.radio(
                'Selecciona el Tipo de Datos a Usar:',
                ['Recibos', 'Embarques', 'Devoluciones'],
                index=0
            )
            resumen_cantidad = st.sidebar.radio(
                'Selecciona las Cantidades a Usar:',
                ['Unidades', 'Cajas', 'Tarimas'],
                index=0
            )

            resumen_periodo = st.sidebar.radio(
                'Selecciona el Período de Tiempo a Usar:',
                ['Días', 'Meses', 'Años'],
                index=0
            )

            resumen_secciones = st.sidebar.number_input(
                'Selecciona el Número de Secciones del Histograma:',
                1,
                20,
                10
            )
            
            if resumen_tipo == 'Recibos':
                st.title(analisis + ' de ' + resumen_cantidad + ' Recibidas por ' + resumen_periodo)
                resumenes(
                    *preparar_datos_resumenes(
                        df_recibo,
                        resumen_cantidad,
                        resumen_periodo,
                        resumen_tipo
                    ),
                    resumen_secciones
                )

            elif resumen_tipo == 'Embarques':
                st.title(analisis + ' de ' + resumen_cantidad + ' Embarcadas por ' + resumen_periodo)
                resumenes(
                    *preparar_datos_resumenes(
                        df_embarque,
                        resumen_cantidad,
                        resumen_periodo,
                        resumen_tipo
                    ),
                    resumen_secciones
                )
            else:
                st.title(analisis + ' de ' + resumen_cantidad + ' Devueltas por ' + resumen_periodo)
                resumenes(
                    *preparar_datos_resumenes(
                        df_devoluciones,
                        resumen_cantidad,
                        resumen_periodo,
                        resumen_tipo
                    ),
                    resumen_secciones
                )
                




if __name__ == "__main__":
    main()
