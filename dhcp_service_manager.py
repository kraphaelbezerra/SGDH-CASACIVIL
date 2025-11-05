import subprocess
import os
import sys

# Definir o nome do serviço DHCP
DHCP_SERVICE = "isc-dhcp-server"

def get_dhcp_status():
    """
    Verifica o status do serviço DHCP usando systemctl.
    No ambiente de sandbox, simula a saída de um serviço ativo.
    Em um ambiente real, executa o comando systemctl.
    """
    if os.environ.get("SANDBOX_ENV") == "true":
        # Simulação para ambiente de sandbox
        return {
            "status": "active",
            "message": f"Serviço {DHCP_SERVICE} está ativo e rodando (Simulado).",
            "full_output": "Active: active (running) since Mon 2025-10-27 10:00:00 -03; 2 days ago"
        }
    
    try:
        # Comando para verificar o status
        command = ["sudo", "systemctl", "status", DHCP_SERVICE]
        
        # Executar o comando
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        # Analisar a saída
        status = "unknown"
        message = "Não foi possível determinar o status."
        
        if result.returncode == 0:
            status = "active"
            message = f"Serviço {DHCP_SERVICE} está ativo e rodando."
        elif result.returncode == 3:
            status = "inactive"
            message = f"Serviço {DHCP_SERVICE} está inativo/parado."
        elif result.returncode == 4:
            status = "not-found"
            message = f"Serviço {DHCP_SERVICE} não encontrado."
        else:
            # Tenta encontrar a linha de status na saída
            for line in result.stdout.splitlines():
                if "Active:" in line:
                    if "active (running)" in line:
                        status = "active"
                        message = f"Serviço {DHCP_SERVICE} está ativo e rodando."
                        break
                    elif "inactive" in line:
                        status = "inactive"
                        message = f"Serviço {DHCP_SERVICE} está inativo/parado."
                        break
                    elif "failed" in line:
                        status = "failed"
                        message = f"Serviço {DHCP_SERVICE} falhou."
                        break
            
        return {
            "status": status,
            "message": message,
            "full_output": result.stdout + result.stderr
        }
        
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Comando systemctl não encontrado. O sistema operacional não é compatível com systemd ou o PATH está incorreto.",
            "full_output": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao executar o comando de status: {str(e)}",
            "full_output": ""
        }

def restart_dhcp_service():
    """
    Reinicia o serviço DHCP usando systemctl.
    No ambiente de sandbox, simula a execução.
    Em um ambiente real, executa o comando systemctl.
    """
    if os.environ.get("SANDBOX_ENV") == "true":
        # Simulação para ambiente de sandbox
        return {
            "success": True,
            "message": f"Serviço {DHCP_SERVICE} reiniciado com sucesso (Simulado)."
        }
    
    try:
        # Comando para reiniciar o serviço
        command = ["sudo", "systemctl", "restart", DHCP_SERVICE]
        
        # Executar o comando
        # Usamos 'check=True' para levantar um CalledProcessError se o comando falhar
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "message": f"Serviço {DHCP_SERVICE} reiniciado com sucesso."
        }
        
    except subprocess.CalledProcessError as e:
        # O comando falhou
        return {
            "success": False,
            "message": f"Falha ao reiniciar o serviço {DHCP_SERVICE}. Verifique as permissões de sudo e se o serviço existe.",
            "full_output": e.stdout + e.stderr
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "Comando systemctl não encontrado. O sistema operacional não é compatível com systemd ou o PATH está incorreto.",
            "full_output": ""
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao executar o comando de reinício: {str(e)}",
            "full_output": ""
        }

if __name__ == '__main__':
    # Exemplo de uso (apenas para teste direto)
    print("--- Status do DHCP ---")
    status = get_dhcp_status()
    print(status)
    
    # print("\n--- Reiniciando DHCP ---")
    # restart = restart_dhcp_service()
    # print(restart)
