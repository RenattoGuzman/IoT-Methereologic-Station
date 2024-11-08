import json
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from confluent_kafka import Consumer, KafkaError
from itertools import count
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener configuración de Kafka desde variables de entorno
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
topic = str(os.getenv('KAFKA_TOPIC'))

# Configuración del Consumer
kafka_config = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': 'telemetria_consumer'
}

# Crear el Consumer
consumer = Consumer(kafka_config)

# Suscribirse al topic
consumer.subscribe([topic])

# Listas para almacenar datos
temperaturas = []
humedades = []
tiempos = []
direccion_actual = "N/A"

# Configuración de la gráfica
plt.ion()
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

def graph_new_value(frame):
    global direccion_actual  # Accedemos a la dirección del viento actual

    # Actualizar título con la dirección del viento
    fig.suptitle(f"Dirección del viento actual: {direccion_actual}", fontsize=16)
    
    # Limpiar y graficar datos
    ax[0].clear()
    ax[1].clear()
    ax[0].plot(tiempos, temperaturas, label="Temperatura (°C)", color='r')
    ax[1].plot(tiempos, humedades, label="Humedad (%)", color='b')
    ax[0].set_title("Temperatura en tiempo real")
    ax[1].set_title("Humedad en tiempo real")
    ax[0].legend()
    ax[1].legend()

# Función para consumir datos y actualizar listas
def consume_data():
    global direccion_actual
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        return
    if msg.error():
        if msg.error().code() != KafkaError._PARTITION_EOF:
            print(f"Error en el Consumer: {msg.error()}")
        return

    # Procesar mensaje
    data = json.loads(msg.value().decode('utf-8'))
    temperatura = data["temperatura"]
    humedad = data["humedad"]
    direccion_actual = data["direccion_viento"]

    # Agregar datos a las listas
    temperaturas.append(temperatura)
    humedades.append(humedad)
    tiempos.append(len(tiempos))


# Configurar animación para que llame a `graph_new_value`
ani = FuncAnimation(fig, graph_new_value, frames=None, interval=2000, cache_frame_data=False)

try:
    while True:
        consume_data()  # Consumiendo datos y actualizando listas
        plt.pause(0.1)  # Mantener la gráfica interactiva

except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    consumer.close()
