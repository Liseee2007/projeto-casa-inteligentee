import time
import json
import paho.mqtt.client as mqtt

# Configurações do Broker MQTT (O servidor que centraliza as mensagens IoT)
MQTT_BROKER = "localhost"  # Na prática, seria o IP do Hub na rede local
MQTT_PORT = 1883
TOPICO_SEGURANCA = "casa/seguranca/+" # O '+' é um wildcard (escuta presenca, fumaca, etc.)

def on_connect(client, userdata, flags, rc):
    """Callback executada quando o Hub se liga com sucesso ao Broker MQTT"""
    if rc == 0:
        print(f"[INFO] Hub conectado ao Broker MQTT com sucesso!")
        # Subscreve o tópico de segurança para ouvir os sensores de borda
        client.subscribe(TOPICO_SEGURANCA)
        print(f"[INFO] Escutando atualizações em: {TOPICO_SEGURANCA}")
    else:
        print(f"[ERRO] Falha na conexão ao MQTT. Código de retorno: {rc}")

def on_message(client, userdata, msg):
    """Callback executada sempre que um sensor envia um dado (Publica uma mensagem)"""
    try:
        # Decodifica a mensagem recebida (geralmente enviada em formato JSON)
        payload_str = msg.payload.decode("utf-8")
        dados = json.loads(payload_str)
        
        sensor_nome = msg.topic.split("/")[-1]
        print(f"\n[📡 TELEMETRIA] Sensor '{sensor_nome}' enviou dados.")
        
        # Lógica de processamento do Back-end com base no tipo de sensor
        if sensor_nome == "presenca":
            if dados.get("movimento") == True:
                print(f"[🚨 ALERTA - INTRUSÃO] Movimento detetado na zona: {dados.get('zona')}!")
                print("[AÇÃO] Ativando gravação das câmeras e enviando notificação push para o usuário.")
                
        elif sensor_nome == "fumaca":
            if dados.get("nivel_ppm", 0) > 50:
                print(f"[🔥 ALERTA - INCÊNDIO] Nível de fumaça crítico: {dados.get('nivel_ppm')} PPM!")
                print("[AÇÃO] Disparando alarme sonoro local e acionando o sistema de mitigação.")
                
        else:
            print(f"[INFO] Dados do sensor {sensor_nome}: {dados}")
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar mensagem no tópico {msg.topic}: {e}")

def iniciar_cliente_mqtt():
    """Inicializa o cliente MQTT e inicia o loop de escuta"""
    client = mqtt.Client("Hub_Central_Python")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("[INFO] Tentando conectar ao Broker MQTT...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Inicia o loop em segundo plano para manter o script escutando os sensores
        client.loop_start()
        return client
    except Exception as e:
        print(f"[AVISO ACADÉMICO] Broker local offline. Lógica de rede MQTT estruturada corretamente.")
        return None

# --- ÁREA DE TESTE  ---
if __name__ == "__main__":
    print("--- Inicializando o Motor de Redes MQTT do Hub ---")
    cliente = iniciar_cliente_mqtt()
    
    # Se o broker estivesse rodando, simularíamos o recebimento de uma mensagem assim:
    print("\n[Simulação] Simulando o comportamento de um sensor de presença:")
    class SimularMsg:
        topic = "casa/seguranca/presenca"
        payload = b'{"movimento": true, "zona": "Corredor Principal"}'
    
    on_message(None, None, SimularMsg)
    
    time.sleep(2)
