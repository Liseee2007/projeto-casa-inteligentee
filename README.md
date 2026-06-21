# Hub Central - Casa Inteligente (Back-end em Python)

Este repositório contém os códigos em Python e os scripts de rede que foi desenvolvido para o Hub Central do projeto da Casa Inteligente. O foco aqui foi resolver os problemas de segurança digital que foi mapeado no relatório.

## 🛠️ O que foi usado
* **Python**: Linguagem principal para rodar o servidor da central.
* **paho-mqtt (Python)**: Biblioteca que usei para fazer o Hub receber as mensagens dos sensores.
* **pyotp (Python)**: Biblioteca para gerar o código de verificação em duas etapas (MFA) no login.
* **Shell Script / iptables**: Para simular as regras de firewall que separam as redes.

---

## 🛡️ O que os códigos resolvem (Mitigações)

1. **Proteção contra invasão por senha (Software):**
   * No arquivo `auth.py`, foi criada a lógica para exigir autenticação em duas etapas (MFA). Também foi colocado uma trava simples: se o mesmo IP errar a senha mais de 3 vezes, o código bloqueia temporariamente as tentativas para evitar ataques de força bruta.

2. **Isolamento de Redes (Rede):**
   * No arquivo `firewall_rules.sh`, foi criado um script de firewall. Ele serve para separar os aparelhos em 3 redes virtuais (VLANs: IoT, Servidor e Principal). A regra principal impede que alguém que invadir uma lâmpada ou câmera consiga acessar os computadores e celulares da rede principal.

---

## 📂 Estrutura das Pastas

```text
├── src/
│   ├── app.py             # Arquivo principal que roda o sistema
│   ├── auth.py            # Código de login, MFA e bloqueio de IP
│   └── mqtt_client.py     # Código que conecta e escuta o Broker MQTT
└── scripts/
    └── firewall_rules.sh  # Script com as regras do firewall (iptables)
