# Herramienta CEDIs con Streamlit
Esta aplicación busca hacer más rápidos los análisis iniciales de proyectos relacionados a CEDIs.
Los análisis incluidos son los siguientes:
- Estacionalidad
- Comparativo de Cargas Operativas por Turno
- Comparativo de Cargas Operativas por Horario
- Análisis de Embarques Diarios
- Análisis de Recibos Diarios
- Distribución de Volumen Embarcado por mes
- Distribución Incremental de Ordenes
- Distribución de Tarimas Completas/Parciales/Mixtas
- Clasificación ABC de Productos
- ABC Sintec vs ABC Cliente
- ABC Sintec vs Foto de Inventario
- Completitud de Pedidos por Producto
- Market Basket Análisis A Priori
- Completitud de Pedido por Agrupación
- Densidad de Pickeo
- Matriz de Productos
- Distribución de Pedidos por lineas/m3
- Cálculo de Espacio para Pickeo
- Cálculo de Espacio para Armado de Pedidos
- Handling Mix Profile por Unidad/Caja 

## Uso local:
- Crear un nuevo entorno de desarrollo e instalar los paquetes descritos en requirements.txt
- Activar el entorno de desarrollo
- Correr el archivo de streamlit usando el comando: streamlit run app.py

## Deployment en Google Cloud Platform:
- Asociar la cuenta de Google con el proyecto 'iniciativa-cedis-production' (contactate con Sintec Digital para el acceso y permisos necesarios para modificar el proyecto)
- Selecciona el projecto: gcloud config set iniciativa-cedis-production
- Implementa los cambios: gcloud app deploy