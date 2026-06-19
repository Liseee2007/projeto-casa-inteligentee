#!/bin/bash

# ==============================================================================
# SCRIPT DE CONFIGURAÇÃO DO FIREWALL (iptables) - ISOLAMENTO DE VLANs
# Disciplina: Introdução à Computação
# Autora: Anelise (Back-end & Redes)
# ==============================================================================

echo "[INFO] Inicializando a configuração das regras de Firewall..."

# 1. Definição das Interfaces de Rede (VLANs)
VLAN_IOT="eth0.10"        # Rede dos sensores e câmeras (Ana)
VLAN_DMZ="eth0.20"        # Rede do Hub Central em Python e Servidor de Mídias
VLAN_PRINCIPAL="eth0.30"  # Rede dos computadores e telemóveis da família

# 2. Limpar regras anteriores para evitar conflitos (Reset)
iptables -F
iptables -X
echo "[INFO] Regras anteriores limpas com sucesso."

# 3. Política Padrão: Bloquear tudo o que não for explicitamente permitido
iptables -P FORWARD DROP
iptables -P INPUT DROP

# ==============================================================================
# 4. REGRAS DE MITIGAÇÃO DA FALHA DE REDE (Isolamento de Dispositivos IoT)
# ==============================================================================

# REGRA A: Permitir que a rede Principal aceda a qualquer outra rede
# (Os donos da casa podem controlar o Hub e ver as câmeras)
iptables -A FORWARD -i $VLAN_PRINCIPAL -j ACCEPT

# REGRA B: Permitir tráfego de conexões já estabelecidas
# (Se o Hub falar com o sensor, o sensor pode responder de volta)
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# REGRA C: Permitir que a rede IoT envie dados APENAS para a DMZ (Hub Central)
iptables -A FORWARD -i $VLAN_IOT -o $VLAN_DMZ -j ACCEPT

# REGRA D: Bloquear categoricamente qualquer tentativa da IoT de falar com a Principal
# (Mitigação contra movimentação lateral: se a câmera for invadida, o hacker fica preso)
iptables -A FORWARD -i $VLAN_IOT -o $VLAN_PRINCIPAL -j DROP

# ==============================================================================
# 5. Permissões Locais do Hub (Para o funcionamento do app.py e mqtt_client.py)
# ==============================================================================

# Permitir acesso local (Loopback)
iptables -A INPUT -i lo -j ACCEPT

# Abrir a porta do Broker MQTT (1883) apenas para a rede IoT e DMZ
iptables -A INPUT -p tcp --dport 1883 -i $VLAN_IOT -j ACCEPT
iptables -A INPUT -p tcp --dport 1883 -i $VLAN_DMZ -j ACCEPT

echo "[🚨 SEGURANÇA AKTIV] As regras de firewall foram aplicadas!"
echo "[INFO] VLAN IoT está agora isolada da VLAN Principal."
