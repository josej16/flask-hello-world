"""
Chatbot para tienda de mascotas utilizando Gemini API a través de LangChain
Este script implementa un asistente virtual que gestiona recordatorios de compras
y almacena información de clientes y sus mascotas.
"""

import pymysql
import time
import random
import datetime
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# --- Configuración del modelo LLM ---
API_KEY = os.environ.get("API_KEY")
if API_KEY is None:
    raise ValueError("The GEMINI_API_KEY environment variable is not set.")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    google_api_key=API_KEY,
    temperature=0.7
)
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# --- Configuración de la base de datos ---
def inicializar_base_datos():
    """Inicializa la conexión a la base de datos y crea las tablas si no existen"""
    print("[INFO] Inicializando base de datos...")
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            port=3306,
            password="root",
            database="analytics_chatbot_ia",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        # Tabla message_log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_log (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                telefono_cliente VARCHAR(255),
                fecha_mensaje DATETIME,
                mensaje TEXT,
                message_direction VARCHAR(255),
                servicio VARCHAR(255),
                step VARCHAR(255)
            )
        ''')

        # Tabla recordatorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordatorios (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                usuario VARCHAR(255),
                fecha_recordatorio DATE,
                numero_semanas INTEGER
            )
        ''')

        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                whatsapp VARCHAR(255) UNIQUE,
                nombre VARCHAR(255),
                mascota_tipo VARCHAR(255),
                mascota_nombre VARCHAR(255),
                preferencias TEXT
            )
        ''')

        conn.commit()
        print("[INFO] Base de datos inicializada correctamente")
        return conn, cursor
    except Exception as e:
        print(f"[ERROR] Error al inicializar la base de datos: {e}")
        return None, None

conn, cursor = inicializar_base_datos()

# --- Funciones de base de datos ---
def obtener_info_cliente(whatsapp):
    """Obtiene la información de un cliente por su número de WhatsApp"""
    try:
        if conn and cursor:
            cursor.execute("SELECT * FROM clientes WHERE whatsapp = %s", (whatsapp,))
            cliente = cursor.fetchone()
            if cliente:
                print(f"[INFO] Cliente encontrado: ID={cliente['id']}, WhatsApp={cliente['whatsapp']}")
            else:
                print(f"[INFO] Cliente no encontrado: WhatsApp={whatsapp}")
            return cliente
        else:
            print("[ERROR] No hay conexión a la base de datos.")
            return None
    except Exception as e:
        print(f"[ERROR] Error al obtener información del cliente: {e}")
        return None

def guardar_info_cliente(whatsapp, datos):
    """Guarda o actualiza la información de un cliente en la base de datos"""
    print(f"[INFO] Guardando información del cliente: {whatsapp}")
    print(f"[INFO] Datos a guardar: {datos}")
    try:
        if conn and cursor:
            cursor.execute("""
            INSERT INTO clientes (whatsapp, nombre, mascota_tipo, mascota_nombre, preferencias)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                nombre=%s,
                mascota_tipo=%s,
                mascota_nombre=%s,
                preferencias=%s
            """, (
                whatsapp,
                datos['nombre'],
                datos.get('mascota_tipo'),
                datos.get('mascota_nombre'),
                datos.get('preferencias'),
                datos['nombre'],
                datos.get('mascota_tipo'),
                datos.get('mascota_nombre'),
                datos.get('preferencias')
            ))

            conn.commit()
            print(f"[INFO] Información del cliente guardada correctamente")
        else:
            print("[ERROR] No hay conexión a la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error al guardar información del cliente: {e}")

def guardar_recordatorio(usuario, fecha_recordatorio, numero_semanas):
    """Guarda un recordatorio para un cliente"""
    print(f"[INFO] Guardando recordatorio para usuario={usuario}")
    print(f"[INFO] Fecha: {fecha_recordatorio}, Numero de Semanas: {numero_semanas}")
    try:
        if conn and cursor:
            cursor.execute(
                "INSERT INTO recordatorios (usuario, fecha_recordatorio, numero_semanas) VALUES (%s, %s, %s)",
                (usuario, fecha_recordatorio, numero_semanas)
            )

            conn.commit()
            print(f"[INFO] Recordatorio guardado correctamente")
        else:
            print("[ERROR] No hay conexión a la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error al guardar el recordatorio: {e}")

def guardar_message_log(telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, previous_step):
    """Guarda un mensaje en la tabla message_log"""
    print(f"[INFO] Guardando mensaje en message_log para telefono_cliente={telefono_cliente}")
    print(f"[INFO] Fecha: {fecha_mensaje}, Mensaje: {mensaje}, Direccion: {message_direction}, Servicio: {servicio}, Step: {previous_step}")

    try:
        cursor.execute(
            "INSERT INTO message_log (telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, step) VALUES (%s, %s, %s, %s, %s, %s)",
            (telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, previous_step)
        )

        conn.commit()
        print(f"[INFO] Mensaje guardado correctamente en message_log")
    except Exception as e:
        print(f"[ERROR] Error al guardar el mensaje en message_log: {e}")

def insert_manual_message(telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, step):
    """Inserts a message into the message_log table manually"""
    try:
        if conn and cursor:
            cursor.execute(
                "INSERT INTO message_log (telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, step) VALUES (%s, %s, %s, %s, %s, %s)",
                (telefono_cliente, fecha_mensaje, mensaje, message_direction, servicio, step)
            )
            conn.commit()
            print("[INFO] Manual message inserted successfully")
        else:
            print("[ERROR] No hay conexión a la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error al insert manual message: {e}")

def obtener_message_history(telefono_cliente):
    """Obtiene el historial de mensajes de un cliente"""
    try:
        if conn and cursor:
            cursor.execute("SELECT mensaje, message_direction, step FROM message_log WHERE telefono_cliente = %s ORDER BY fecha_mensaje DESC", (telefono_cliente,))
            message_history = cursor.fetchall()
            print(f"[INFO] Obteniendo historial de mensajes para telefono_cliente={telefono_cliente}")
            print(f"[INFO] Historial de mensajes: {message_history}")
            return message_history
        else:
            print("[ERROR] No hay conexión a la base de datos.")
            return []
    except Exception as e:
        print(f"[ERROR] Error al obtener el historial de mensajes: {e}")
        return []

def convertir_a_semanas(intervalo, unidad):
    """Convierte un intervalo de tiempo a semanas."""
    unidad = unidad.lower()
    if unidad == "dias" or unidad == "dia":
        return int(intervalo) / 7
    elif unidad == "semanas" or unidad == "semana":
        return int(intervalo)
    elif unidad == "meses" or unidad == "mes":
        return int(intervalo) * 4.34524
    else:
        # Si no se especifica la unidad, se asume que son semanas
        return int(intervalo)

# --- Configuración del prompt para el modelo ---
template = """Eres un asistente amigable y servicial de una tienda de mascotas.
Tu objetivo es ayudar a los clientes a recordar sus próximas compras. Considera que cada cliente es un cliente reciente.

Debes seguir estos pasos en orden jerárquico. No pases al siguiente paso hasta que el actual esté completo:

1. Saluda al cliente y preséntate, pregúntale si desea programar un recordatorio para su próxima compra.
2. Si dice que sí, pregunta el intervalo de tiempo en semanas.
   - Si el usuario especifica un intervalo de tiempo, debes:
     * Calcular el número equivalente de SEMANAS (como un NÚMERO ENTERO).
     * Incluir una clave "intervalo" en tu respuesta con ese valor numérico.
     * Si el usuario no especifica un intervalo después de solicitarlo, NO incluyas la clave "intervalo" en tu respuesta.

3. Solicita el Nombre de su mascota de manera amable y animosa.
4. Solicita los alimentos favoritos de su mascota de manera amable y animosa.
5. Solicita la raza de su mascota de manera amable y animosa.
6. Confirmar al usuario que se ha programado un recordatorio para la proxima compra de alimento de [Preferencia] para [Nombre_mascota].

Siempre sé amable, empático y usa un lenguaje formal.

Devuelve tu respuesta SIEMPRE en formato de diccionario de Python con estas reglas:

1. SIEMPRE incluye la clave "respuesta" con el texto conversacional para el usuario.
2. SOLO si el usuario proporciona un intervalo de tiempo, añade la clave "intervalo" con el número de semanas.
3. SOLO si el usuario proporciona el nombre de su mascota, añade la clave "Nombre_mascota" con el nombre de la mascota.
4. SOLO si el usuario proporciona alguna preferencia de comida para su mascota, añade la clave "preferencia" con la preferencia de comida.
5. SOLO si el usuario proporciona la raza de su mascota, añade la clave "raza_mascota" con la raza de la mascota.
6. SIEMPRE incluye la clave "step" con el número del paso actual en la conversación.

IMPORTANTE:
- Devuelve SOLO el diccionario, sin texto adicional antes o después.
- No incluyas la palabra "json" ni ninguna otra explicación.
- El formato debe ser exactamente como en los ejemplos para que funcione con dict() en Python.
- NO uses comillas simples, usa SIEMPRE comillas dobles para las claves y valores de texto.
- SIEMPRE incluye la clave "step" con el número del paso actual.

Ejemplos de formato correcto:
- Paso 1, saludo inicial y solicitud de recordatorio: {{"respuesta": "¡Hola! Soy el asistente de la tienda de mascotas, ¿Le gustaría que le programemos un recordatorio para su próxima compra?", "step": 1}}
- Paso 2, especificación de intervalo: {{"respuesta": "¡Perfecto! ¿En cuantas semanas le gustaria recibir un recordatorio de su proxima compra?", "step": 2}}
- Paso 3, solicitud de nombre de mascota: {{"respuesta": "¡Genial! ¿Cuál es el nombre de su mascota?", "step": 3, "intervalo": 8}}
- Paso 4, solicitud de preferencia de comida: {{"respuesta": "¡Excelente! ¿Qué alimentos le gustan a su mascota?", "step": 4, "Nombre_mascota": "Firulais"}}
- Paso 5, solicitud de raza de mascota: {{"respuesta": "¡Maravilloso! ¿Y cuál es la raza de su mascota?", "step": 5, "preferencia": "Royal Canin"}}
- Paso 6, confirmación de recordatorio: {{"respuesta": "¡Excelente! Le recordaré el 17 de mayo de 2025 su próxima compra de alimento para [Nombre_mascota].", "step": 6, "raza_mascota": "Golden Retriever"}}
- Ejemplo con toda la información: {{"respuesta": "¡Gracias por la información! Le recordaré el 17 de mayo de 2025 su próxima compra de Royal Canin para Firulais.", "Nombre_mascota": "Firulais", "preferencia": "Royal Canin", "raza_mascota": "Golden Retriever", "step": 6}}
- Ejemplo con solo el nombre de la mascota: {{"respuesta": "¡Gracias! Le recordaré el 17 de mayo de 2025 su próxima compra de alimento para Firulais.", "Nombre_mascota": "Firulais", "step": 6}}
- Ejemplo con nombre y preferencia: {{"respuesta": "¡Perfecto! Le recordaré el 17 de mayo de 2025 su próxima compra de Royal Canin para Firulais.", "Nombre_mascota": "Firulais", "preferencia": "Royal Canin", "step": 6}}

{history}
Cliente: {input}
"""

prompt = PromptTemplate(
    input_variables=["history", "input", "step"],
    template=template
)

# --- Configuración de la cadena de conversación ---
conversation = ConversationChain(
    prompt=prompt,
    llm=llm,
    verbose=False,
    memory=memory
)

# --- Función principal de interacción ---
def interactuar(mensaje_usuario, whatsapp_id):
    """
    Procesa un mensaje del usuario y genera una respuesta

    Args:
        mensaje_usuario: El mensaje enviado por el usuario
        whatsapp_id: El número de WhatsApp del usuario

    Returns:
        La respuesta generada para el usuario
    """
    print(f"\n[INFO] Procesando mensaje: '{mensaje_usuario}' de WhatsApp: {whatsapp_id}")

    # Obtener información del cliente
    cliente = obtener_info_cliente(whatsapp_id)
    datos_cliente = {}
    datos_nuevos = {}

    # Get the current step for the user
    if cliente:
        step = cliente['step']
        previous_step = step
        print(f"[INFO] Cliente encontrado, current step: {step}")
    else:
        step = 0
        previous_step = 0
        print("[INFO] Cliente no encontrado, starting at step 0")
        # Create a new client with the initial step
        datos_nuevos = {"nombre": "Desconocido", "step": 0}
        guardar_info_cliente(whatsapp_id, datos_nuevos)
        cliente = obtener_info_cliente(whatsapp_id)  # Obtener el cliente recién creado

    if cliente:
        datos_cliente = {
            "nombre": cliente['nombre'],
            "mascota_tipo": cliente['mascota_tipo'],
            "mascota_nombre": cliente['mascota_nombre'],
            "preferencias": cliente['preferencias'],
        }
        print(f"[INFO] Datos del cliente: {datos_cliente}")

    # Get the message history of the client
    message_history = obtener_message_history(whatsapp_id)
    print(f"[INFO] Historial de mensajes del cliente: {message_history}")

    # Limit the history to the last 3 messages
    # Format message history for the prompt
    formatted_history = ""
    for message in message_history:
        formatted_history += f"Cliente: {message['mensaje']}\n"
        
    # Combine the history with the prompt
    prompt_con_historial = template.format(history=formatted_history, input=mensaje_usuario, step=step)

    # Retry system for the API
    max_reintentos = 5
    reintentos = 0
    espera = 1

    # Intentar obtener respuesta del modelo
    while reintentos < max_reintentos:
        try:
            print(f"[INFO] Enviando mensaje al modelo (intento {reintentos+1}/{max_reintentos})")

            # Obtener respuesta del modelo
            respuesta_raw = conversation.predict(input=prompt_con_historial)

            # Limpiar y parsear la respuesta
            respuesta_limpia = respuesta_raw.strip().replace("json", "", 1).replace("```", "").replace("\n", " ").replace("\r", " ").replace('   ', '').replace(" ", "", 1).replace("python", "", 1)
            print(f"[INFO] Respuesta recibida: {respuesta_limpia}")

            # Convertir a diccionario
            try:
                respuesta_ia = eval(respuesta_limpia)
                print(f"[INFO] Respuesta convertida a diccionario: {respuesta_ia}")
                break
            except Exception as e:
                print(f"[ERROR] Error al convertir la respuesta a diccionario: {e}")
                return "Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."
        except Exception as e:
            reintentos += 1
            if "Resource has been exhausted" in str(e) or "429" in str(e):
                print(f"[ERROR] Intento {reintentos}/{max_reintentos}: Límite de cuota alcanzado. Esperando {espera} segundos...")
                time.sleep(espera)
                espera *= 2
                espera += random.uniform(0, 0.1)
            else:
                print(f"[ERROR] Error inesperado: {e}")
                return "Hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."
    else:
        print(f"[ERROR] Se alcanzó el número máximo de reintentos ({max_reintentos}).")
        return "No se pudo obtener una respuesta de la IA. Por favor, inténtalo de nuevo más tarde."

    # Extract the step from the response
    try:
        step = respuesta_ia['step']
        print(f"[INFO] Step IA detectado: {step}")
    except KeyError:
        print("[WARNING] No se proporcionó un step en la respuesta de la IA, usando el step anterior.")

    # Guardar the current step for the user's message
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_message_log(whatsapp_id, fecha_actual, mensaje_usuario, "inbound", "SRR", previous_step)

    # Procesar la respuesta y manejar recordatorios e información de mascota
    intervalo = None
    nombre_mascota = None
    preferencia = None
    raza_mascota = None
    try:
        # Verificar si hay un intervalo en la respuesta
        if 'intervalo' in respuesta_ia:
            intervalo = respuesta_ia['intervalo']
            print(f"[INFO] Intervalo detectado: {intervalo}")

        if 'Nombre_mascota' in respuesta_ia:
            nombre_mascota = respuesta_ia['Nombre_mascota']
            print(f"[INFO] Nombre de mascota detectado: {nombre_mascota}")

        if 'preferencia' in respuesta_ia:
            preferencia = respuesta_ia['preferencia']
            print(f"[INFO] Preferencia detectada: {preferencia}")

        if 'raza_mascota' in respuesta_ia:
            raza_mascota = respuesta_ia['raza_mascota']
            print(f"[INFO] Raza detectada: {raza_mascota}")

        if intervalo is not None:
            # Convertir a entero y calcular fecha de recordatorio
            intervalo = int(intervalo)
            fecha_recordatorio = datetime.date.today() + datetime.timedelta(weeks=intervalo)
            print(f"[INFO] Fecha de recordatorio calculada: {fecha_recordatorio}")

            # Guardar recordatorio en la base de datos
            if not cliente:
                # Crear un nuevo cliente si no existe
                datos_nuevos = {"nombre": "Desconocido", "step": 0}
                guardar_info_cliente(whatsapp_id, datos_nuevos)
                cliente = obtener_info_cliente(whatsapp_id)  # Obtener el cliente recién creado

            # Update the step in the database
            if cliente:
                cursor.execute("UPDATE clientes SET step = %s WHERE whatsapp = %s", (step, whatsapp_id))
                conn.commit()
                print(f"[INFO] Step actualizado en la base de datos para el cliente {whatsapp_id} a {step}")
            else:
                # Create a new client with the initial step
                datos_nuevos = {"nombre": "Desconocido", "step": step}
                guardar_info_cliente(whatsapp_id, datos_nuevos)
                print(f"[INFO] Nuevo cliente creado con step inicial {step}")

            if cliente:
                guardar_recordatorio(
                    whatsapp_id,
                    fecha_recordatorio.strftime("%Y-%m-%d"),
                    intervalo
                )

            # Guardar el mensaje de la IA en el message_log
            guardar_message_log(whatsapp_id, fecha_actual, respuesta_ia['respuesta'], "outbound", "SRR", step)

            # Enviar confirmación
            print("[INFO] Recordatorio guardado correctamente")

    except KeyError:
        print("[INFO] No se proporcionó un intervalo, no se guarda el recordatorio.")
        # Guardar el mensaje de la IA en el message_log
        guardar_message_log(whatsapp_id, fecha_actual, respuesta_ia['respuesta'], "outbound", "SRR", step)
    except ValueError as e:
        print(f"[ERROR] Error al procesar el intervalo: {e}")
        tipo = mensaje_usuario.lower().split("mi mascota es una")[1].split(".")[0].strip()
        datos_nuevos["mascota_tipo"] = tipo
        print(f"[INFO] Tipo de mascota detectado: {tipo}")

    # Update datos_nuevos with nombre_mascota and preferencia from respuesta_ia
    if nombre_mascota:
        datos_nuevos["mascota_nombre"] = nombre_mascota
    if preferencia:
        datos_nuevos["preferencias"] = preferencia

    if raza_mascota:
        datos_nuevos["mascota_tipo"] = raza_mascota
    
    
    # Guardar datos nuevos si se encontraron
    if datos_nuevos or nombre_mascota or preferencia:
        if cliente:
            # Actualizar datos existentes
            datos_actualizados = datos_cliente.copy()
            datos_actualizados.update(datos_nuevos)
            if nombre_mascota:
                datos_actualizados["mascota_nombre"] = nombre_mascota
            if preferencia:
                datos_actualizados["preferencias"] = preferencia
            guardar_info_cliente(whatsapp_id, datos_actualizados)
        else:
            # Crear nuevo cliente
            datos_nuevos = {"nombre": "Desconocido", "step": 0}
            if nombre_mascota:
                datos_nuevos["mascota_nombre"] = nombre_mascota
            if preferencia:
                datos_nuevos["preferencias"] = preferencia
            guardar_info_cliente(whatsapp_id, datos_nuevos)
            print("[INFO] Nuevo cliente creado con datos iniciales")

    # Update the step in the database
    if cliente:
        cursor.execute("UPDATE clientes SET step = %s WHERE whatsapp = %s", (step, whatsapp_id))
        conn.commit()
        print(f"[INFO] Step actualizado en la base de datos para el cliente {whatsapp_id} a {step}")

    # Guardar el mensaje de la IA en el message_log
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_message_log(whatsapp_id, fecha_actual, respuesta_ia['respuesta'], "outbound", "SRR", step)

    # Devolver la respuesta al usuario
    return respuesta_ia['respuesta']

# --- Pruebas ---
def truncate_tables():
    """Truncates all tables in the database"""
    try:
        if conn and cursor:
            cursor.execute("TRUNCATE TABLE message_log")
            cursor.execute("TRUNCATE TABLE clientes")
            cursor.execute("TRUNCATE TABLE recordatorios")
            conn.commit()
            print("[INFO] All tables truncated successfully")
        else:
            print("[ERROR] No hay conexión a la base de datos.")
    except Exception as e:
        print(f"[ERROR] Error al truncating tables: {e}")

if __name__ == "__main__":
    print("[INFO] Iniciando pruebas del chatbot")
    truncate_tables()

    def test_interactuar(mensaje, telefono):
        print(f"Usuario: {mensaje}")
        respuesta = interactuar(mensaje, telefono)
        print(f"Chatbot: {respuesta}")

    # Ejemplo 1: Saludo inicial
    print("\n[TEST] Ejemplo 1: Saludo inicial")
    test_interactuar("Hola", "5491112345678")

    # Ejemplo 2: Solicitud de recordatorio")
    print("\n[TEST] Ejemplo 2: Solicitud de recordatorio")
    test_interactuar("Sí, me gustaría un recordatorio", "5491112345678")

    # Ejemplo 3: Especificación de intervalo")
    print("\n[TEST] Ejemplo 3: Especificación de intervalo")
    test_interactuar("En dos meses", "5491112345678")

    # Ejemplo 4: Información sobre mascota")
    print("\n[TEST] Ejemplo 4: Información sobre mascota")
    test_interactuar("Mi perro se llama Firulais y le gusta la comida Royal Canin", "5491112345678")
