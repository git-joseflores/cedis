import base64
import uuid
import re

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

