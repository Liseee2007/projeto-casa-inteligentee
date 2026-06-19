import time
import pyotp  # Biblioteca para gerar/validar códigos de MFA (Autenticação em Duas Etapas)

# Banco de dados simulado em memória
USUARIOS_BD = {
    "admin": {
        "senha": "SenhaUltraSegura#2026",  # Exigência de senha forte
        "mfa_secret": "JBSWY3DPEHPK3PXP"    # Chave secreta para gerar o Token MFA
    }
}

# Dicionário para controlar as tentativas de login por endereço IP
tentativas_login = {}
# Dicionário para guardar o timestamp de quando o IP foi bloqueado
ips_bloqueados = {}

LIMIT_TENTATIVAS = 3
TEMPO_BLOQUEIO = 60  # Tempo de bloqueio em segundos (1 minuto)

def verificar_rate_limit(ip):
    """Verifica se o IP está bloqueado por excesso de tentativas"""
    if ip in ips_bloqueados:
        tempo_decorrido = time.time() - ips_bloqueados[ip]
        if tempo_decorrido < TEMPO_BLOQUEIO:
            tempo_restante = int(TEMPO_BLOQUEIO - tempo_decorrido)
            print(f"[ALERTA DE SEGURANÇA] IP {ip} está bloqueado por mais {tempo_restante} segundos.")
            return False
        else:
            # O tempo de bloqueio já passou, liberta o IP
            del ips_bloqueados[ip]
            tentativas_login[ip] = 0
    return True

def realizar_login(ip, usuario, senha, token_mfa):
    """Função principal que valida as credenciais e o MFA com Rate Limiting"""
    
    # 1. Verifica se o IP não está na lista de bloqueados
    if not verificar_rate_limit(ip):
        return "Acesso negado: IP temporariamente bloqueado."

    # Inicializa o contador de tentativas para o IP, se for a primeira vez dele
    if ip not in tentativas_login:
        tentativas_login[ip] = 0

    # 2. Valida o Usuário e a Senha
    if usuario not in USUARIOS_BD or USUARIOS_BD[usuario]["senha"] != senha:
        tentativas_login[ip] += 1
        print(f"[Falha] Tentativa incorreta para o usuário '{usuario}' vinda do IP {ip}. Erros: {tentativas_login[ip]}/{LIMIT_TENTATIVAS}")
        
        # Se atingir o limite, bloqueia o IP
        if tentativas_login[ip] >= LIMIT_TENTATIVAS:
            ips_bloqueados[ip] = time.time()
            print(f"[🚨 BLOCK] IP {ip} foi bloqueado por tentar força bruta!")
            
        return "Usuário ou senha incorretos."

    # 3. Se a senha estiver certa, valida o Token MFA (Duas Etapas)
    secret = USUARIOS_BD[usuario]["mfa_secret"]
    totp = pyotp.TOTP(secret)
    
    if not totp.verify(token_mfa):
        tentativas_login[ip] += 1
        print(f"[Falha] Senha correta, mas Token MFA inválido para o usuário '{usuario}' vinda do IP {ip}.")
        return "Token MFA inválido."

    # Se chegou aqui, deu tudo certo! Reseta o contador do IP
    tentativas_login[ip] = 0
    print(f"[Sucesso] Login efetuado com sucesso no Hub pelo usuário '{usuario}' (IP: {ip}).")
    return "Login efetuado com sucesso!"

# --- ÁREA DE TESTE ---
if __name__ == "__main__":
    ip_teste = "192.168.10.45"
    
    print("--- Cenário 1: Tentando invadir com senha errada (Força Bruta) ---")
    print(realizar_login(ip_teste, "admin", "12345", "000000"))
    print(realizar_login(ip_teste, "admin", "admin", "000000"))
    print(realizar_login(ip_teste, "admin", "senha_errada", "000000"))
    
    print("\n--- Cenário 2: Próxima tentativa após o bloqueio ---")
    print(realizar_login(ip_teste, "admin", "SenhaUltraSegura#2026", "000000"))
