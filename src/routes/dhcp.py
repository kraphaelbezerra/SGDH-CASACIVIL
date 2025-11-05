import os
import re
import sys
from flask import Blueprint, request, jsonify

from flask_login import login_required, current_user

# Adicionar o diretório raiz ao path para importar o dhcp_parser
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from dhcp_parser import parse_dhcp_conf, get_used_ips, parse_ip_ranges
from src.utils.audit import log_host_create, log_host_update, log_host_delete, log_action
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dhcp_service_manager import get_dhcp_status, restart_dhcp_service

dhcp_bp = Blueprint('dhcp', __name__)

# Caminhos dos arquivos de configuração
DHCP_CONF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dhcpd.conf')
IPS_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ips_disponiveis.sh')

def ip_to_int(ip_address):
    """Converte um endereço IP para inteiro."""
    parts = list(map(int, ip_address.split('.')))
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]

def int_to_ip(ip_int):
    """Converte um inteiro para endereço IP."""
    return f"{(ip_int >> 24) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"

def get_ips_in_range(start_ip, end_ip, used_ips, limit=50):
    """Retorna uma lista de IPs disponíveis em um range."""
    available = []
    start_int = ip_to_int(start_ip)
    end_int = ip_to_int(end_ip)
    
    for ip_int in range(start_int, end_int + 1):
        if len(available) >= limit:
            break
        current_ip = int_to_ip(ip_int)
        if current_ip not in used_ips:
            available.append(current_ip)
    
    return available

def validate_mac(mac_address):
    """Valida o formato do endereço MAC."""
    return re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac_address)



def find_rule_for_ip(ip_address, rules):
    """Encontra a regra de IP para um determinado endereço IP."""
    for rule in rules:
        start_int = ip_to_int(rule['inicio'])
        end_int = ip_to_int(rule['fim'])
        ip_int = ip_to_int(ip_address)
        if start_int <= ip_int <= end_int:
            return f"{rule['categoria']} - {rule['acesso']}"
    return "N/A"

def validate_ip(ip_address):
    """Valida o formato do endereço IP."""
    if not re.match(r"^(\d{1,3}\.){3}\d{1,3}$", ip_address):
        return False
    return all(0 <= int(x) <= 255 for x in ip_address.split('.'))

@dhcp_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Retorna estatísticas do sistema DHCP."""
    try:
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        ip_rules = parse_ip_ranges(IPS_SCRIPT_PATH)
        
        return jsonify({
            'total_hosts': len(hosts_data),
            'total_rules': len(ip_rules),
            'success': True
        })
    except Exception as e:
        return jsonify({
            'message': f'Erro ao obter estatísticas: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/rules', methods=['GET'])
@login_required
def get_rules():
    """Retorna todas as regras de IP disponíveis."""
    try:
        ip_rules = parse_ip_ranges(IPS_SCRIPT_PATH)
        return jsonify(ip_rules)
    except Exception as e:
        return jsonify({
            'message': f'Erro ao carregar regras: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/available-ips', methods=['GET'])
@login_required
def get_available_ips():
    """Retorna IPs disponíveis em um range específico."""
    try:
        start_ip = request.args.get('start')
        end_ip = request.args.get('end')
        
        if not start_ip or not end_ip:
            return jsonify({
                'message': 'Parâmetros start e end são obrigatórios',
                'success': False
            }), 400
        
        if not validate_ip(start_ip) or not validate_ip(end_ip):
            return jsonify({
                'message': 'Endereços IP inválidos',
                'success': False
            }), 400
        
        used_ips = get_used_ips(DHCP_CONF_PATH)
        available_ips = get_ips_in_range(start_ip, end_ip, used_ips)
        
        return jsonify(available_ips)
    except Exception as e:
        return jsonify({
            'message': f'Erro ao obter IPs disponíveis: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/hosts_status', methods=['GET'])
@login_required
def get_hosts_status():
    """Retorna todos os hosts cadastrados com o status de conectividade e a regra de IP."""
    try:
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        ip_rules = parse_ip_ranges(IPS_SCRIPT_PATH)
        hosts_with_status = []
        for host in hosts_data:
            host['connectivity_status'] = "Cadastrado no DHCP"
            host['rule'] = find_rule_for_ip(host['ip_address'], ip_rules)
            hosts_with_status.append(host)
        
        return jsonify(hosts_with_status)
    except Exception as e:
        return jsonify({
            'message': f'Erro ao carregar hosts com status: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/status', methods=['GET'])
@login_required
def get_service_status():
    """Retorna o status do serviço DHCP."""
    try:
        status_info = get_dhcp_status()
        log_action(f"Verificação de status do serviço DHCP: {status_info['status']}")
        return jsonify(status_info)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao verificar status do serviço: {str(e)}',
            'full_output': ''
        }), 500

@dhcp_bp.route('/restart', methods=['POST'])
@login_required
def restart_service():
    """Reinicia o serviço DHCP."""
    try:
        restart_info = restart_dhcp_service()
        if restart_info['success']:
            log_action("Serviço DHCP reiniciado com sucesso.")
        else:
            log_action(f"Falha ao reiniciar o serviço DHCP: {restart_info['message']}")
        return jsonify(restart_info)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao tentar reiniciar o serviço: {str(e)}',
            'full_output': ''
        }), 500

@dhcp_bp.route('/hosts', methods=['GET'])
@login_required
def get_hosts():
    """Retorna todos os hosts cadastrados."""
    try:
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        return jsonify(hosts_data)
    except Exception as e:
        return jsonify({
            'message': f'Erro ao carregar hosts: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/register', methods=['POST'])
@login_required
def register_ip():
    """Registra um novo IP no sistema DHCP."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'Dados JSON são obrigatórios',
                'success': False
            }), 400
        
        host_name = data.get('host_name', '').strip()
        mac_address = data.get('mac_address', '').strip().upper()
        ip_address = data.get('ip_address', '').strip()
        
        # Validações
        if not all([host_name, mac_address, ip_address]):
            return jsonify({
                'message': 'Todos os campos são obrigatórios',
                'success': False
            }), 400
        
        if not validate_mac(mac_address):
            return jsonify({
                'message': 'Endereço MAC inválido. Use o formato XX:XX:XX:XX:XX:XX',
                'success': False
            }), 400
        
        if not validate_ip(ip_address):
            return jsonify({
                'message': 'Endereço IP inválido',
                'success': False
            }), 400
        
        # Verificar se o IP já está em uso
        used_ips = get_used_ips(DHCP_CONF_PATH)
        if ip_address in used_ips:
            return jsonify({
                'message': f'O IP {ip_address} já está em uso',
                'success': False
            }), 400
        
        # Verificar se o IP está dentro de alguma regra
        ip_rules = parse_ip_ranges(IPS_SCRIPT_PATH)
        is_ip_in_rule = False
        for rule in ip_rules:
            start_int = ip_to_int(rule["inicio"])
            end_int = ip_to_int(rule["fim"])
            ip_int = ip_to_int(ip_address)
            if start_int <= ip_int <= end_int:
                is_ip_in_rule = True
                break
        
        if not is_ip_in_rule:
            return jsonify({
                'message': f'O IP {ip_address} não pertence a nenhum range de regras definido',
                'success': False
            }), 400
        
        # Verificar se o nome do host já existe
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        existing_names = [host['name'] for host in hosts_data]
        if host_name.replace(' ', '_') in existing_names:
            return jsonify({
                'message': f'O nome do host {host_name} já existe',
                'success': False
            }), 400
        
        # Verificar se o MAC já existe
        existing_macs = [host['mac_address'] for host in hosts_data]
        if mac_address in existing_macs:
            return jsonify({
                'message': f'O endereço MAC {mac_address} já está cadastrado',
                'success': False
            }), 400
        
        # Criar entrada para o dhcpd.conf
        from datetime import datetime
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        host_name_clean = host_name.replace(' ', '_').replace('-', '_')
        new_host_entry = f'''
          host {host_name_clean} {{
                  hardware ethernet {mac_address};
		          fixed-address {ip_address};
		          }}
		          # Data: {registration_date}'''
        
        # --- INÍCIO DA CORREÇÃO ---
        # A correção consiste em ler o arquivo, remover a última chave '}' e
        # inserir a nova entrada de host antes de reescrever a chave '}'.
        
        with open(DHCP_CONF_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Encontra a posição da última chave de fechamento '}' no arquivo
        # Isso assume que a última '}' é a que fecha o bloco 'subnet'.
        last_brace_index = content.rfind('}')
        
        if last_brace_index != -1:
            # Divide o conteúdo em duas partes: antes e depois da última '}'
            content_before_brace = content[:last_brace_index]
            content_after_brace = content[last_brace_index:]
            
            # Remove a última chave '}' do conteúdo anterior
            # O bloco de host deve ser inserido antes da chave de fechamento do subnet
            new_content = content_before_brace.rstrip() + new_host_entry + '\n' + content_after_brace.lstrip()
            
            # Reescreve o arquivo com o novo conteúdo
            with open(DHCP_CONF_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            # Se não encontrou a chave, volta para a lógica de 'append' e registra o erro
            with open(DHCP_CONF_PATH, 'a', encoding='utf-8') as f:
                f.write(new_host_entry)
            print(f"ERRO: Não foi encontrada a chave de fechamento '}}' no arquivo {DHCP_CONF_PATH}. Novo host adicionado ao final.")
        
        # --- FIM DA CORREÇÃO ---
        
        # Registrar log de auditoria
        rule_name = find_rule_for_ip(ip_address, ip_rules)
        log_host_create(host_name_clean, mac_address, ip_address, rule_name)
        
        # Reiniciar serviço DHCP automaticamente
        restart_info = restart_dhcp_service()
        if not restart_info['success']:
            log_action(f"Aviso: Falha ao reiniciar o serviço DHCP após criação: {restart_info['message']}")
        
        return jsonify({
            'message': f'Host {host_name} registrado com sucesso!',
            'success': True,
            'data': {
                'host_name': host_name,
                'mac_address': mac_address,
                'ip_address': ip_address
            }
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/hosts/<string:host_name>', methods=['DELETE'])
@login_required
def delete_host(host_name):
    """Exclui um host do arquivo dhcpd.conf."""
    try:
        # Obter dados do host antes de excluir para o log
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        host_to_delete = None
        for host in hosts_data:
            if host['name'] == host_name:
                host_to_delete = host
                break
        
        with open(DHCP_CONF_PATH, 'r') as f:
            lines = f.readlines()

        new_lines = []
        in_host_block = False
        host_found = False
        # Itera pelas linhas e recria o arquivo sem o bloco do host a ser excluído
        for i, line in enumerate(lines):
            # Encontra o início do bloco 'host'
            if re.search(r'^\s*host\s+' + re.escape(host_name) + r'\s*\{', line):
                in_host_block = True
                host_found = True
                continue

            # Se estiver dentro do bloco 'host', verifica o fechamento
            if in_host_block:
                if re.search(r'^\s*\}', line) or re.search(r'^\s*\}\s*#\s*Data:', line):
                    in_host_block = False
                    continue
                # Ignora as linhas dentro do bloco
                continue

            # Adiciona as linhas que não fazem parte do bloco a ser excluído
            new_lines.append(line)

        if host_found:
            # Reescreve o arquivo com as linhas restantes
            with open(DHCP_CONF_PATH, 'w') as f:
                f.writelines(new_lines)

            # Registrar log de auditoria
            if host_to_delete:
                rule_name = find_rule_for_ip(host_to_delete['ip_address'], parse_ip_ranges(IPS_SCRIPT_PATH))
                log_host_delete(host_to_delete['name'], host_to_delete['mac_address'], host_to_delete['ip_address'])
            
            # Reiniciar serviço DHCP automaticamente
            restart_info = restart_dhcp_service()
            if not restart_info['success']:
                log_action(f"Aviso: Falha ao reiniciar o serviço DHCP após exclusão: {restart_info['message']}")

            return jsonify({
                'message': f'Host {host_name} excluído com sucesso!',
                'success': True
            })
        else:
            return jsonify({
                'message': f'Host {host_name} não encontrado.',
                'success': False
            }), 404
        
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500
        
@dhcp_bp.route('/hosts/<string:host_name>', methods=['PUT'])
@login_required
def update_host(host_name):
    """Atualiza um host existente no dhcpd.conf."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'Dados JSON são obrigatórios',
                'success': False
            }), 400
        
        new_mac_address = data.get('mac_address', '').strip().upper()
        new_ip_address = data.get('ip_address', '').strip()
        
        # Validações
        if not all([new_mac_address, new_ip_address]):
            return jsonify({
                'message': 'MAC e IP são obrigatórios',
                'success': False
            }), 400
        
        if not validate_mac(new_mac_address):
            return jsonify({
                'message': 'Endereço MAC inválido. Use o formato XX:XX:XX:XX:XX:XX',
                'success': False
            }), 400
        
        if not validate_ip(new_ip_address):
            return jsonify({
                'message': 'Endereço IP inválido',
                'success': False
            }), 400
        
        # Obter dados atuais do host
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        host_to_update = None
        for host in hosts_data:
            if host['name'] == host_name:
                host_to_update = host
                break
        
        if not host_to_update:
            return jsonify({
                'message': f'Host {host_name} não encontrado.',
                'success': False
            }), 404
            
        # Verificar se o novo IP já está em uso por outro host
        used_ips = get_used_ips(DHCP_CONF_PATH)
        if new_ip_address in used_ips and new_ip_address != host_to_update['ip_address']:
            return jsonify({
                'message': f'O IP {new_ip_address} já está em uso por outro host',
                'success': False
            }), 400
            
        # Verificar se o novo MAC já está em uso por outro host
        existing_macs = [host['mac_address'] for host in hosts_data if host['name'] != host_name]
        if new_mac_address in existing_macs:
            return jsonify({
                'message': f'O endereço MAC {new_mac_address} já está cadastrado em outro host',
                'success': False
            }), 400
            
        # Verificar se o IP está dentro de alguma regra
        ip_rules = parse_ip_ranges(IPS_SCRIPT_PATH)
        is_ip_in_rule = False
        for rule in ip_rules:
            start_int = ip_to_int(rule["inicio"])
            end_int = ip_to_int(rule["fim"])
            ip_int = ip_to_int(new_ip_address)
            if start_int <= ip_int <= end_int:
                is_ip_in_rule = True
                break
        
        if not is_ip_in_rule:
            return jsonify({
                'message': f'O IP {new_ip_address} não pertence a nenhum range de regras definido',
                'success': False
            }), 400
            
        # Realizar a atualização no arquivo
        with open(DHCP_CONF_PATH, 'r') as f:
            lines = f.readlines()

        new_lines = []
        in_host_block = False
        
        for line in lines:
            # Encontra o início do bloco 'host'
            if re.search(r'^\s*host\s+' + re.escape(host_name) + r'\s*\{', line):
                in_host_block = True
                new_lines.append(line)
                continue

            # Se estiver dentro do bloco 'host', substitui MAC e IP
            if in_host_block:
                if re.search(r'hardware ethernet', line):
                    new_lines.append(f'\t\t\t\thardware ethernet {new_mac_address};\n')
                    continue
                elif re.search(r'fixed-address', line):
                    new_lines.append(f'\t\t\t\tfixed-address {new_ip_address};\n')
                    continue
                elif re.search(r'^\s*\}', line) or re.search(r'^\s*\}\s*#\s*Data:', line):
                    in_host_block = False
                    new_lines.append(line)
                    continue

            # Adiciona as linhas que não fazem parte do bloco a ser atualizado
            new_lines.append(line)

        # Reescreve o arquivo com as linhas atualizadas
        with open(DHCP_CONF_PATH, 'w') as f:
            f.writelines(new_lines)
            
        # Registrar log de auditoria
        rule_name = find_rule_for_ip(new_ip_address, ip_rules)
        log_host_update(host_name, 
            {'mac_address': host_to_update['mac_address'], 'ip_address': host_to_update['ip_address'], 'rule_name': find_rule_for_ip(host_to_update['ip_address'], ip_rules)}, 
            {'mac_address': new_mac_address, 'ip_address': new_ip_address, 'rule_name': rule_name})
        
        # Reiniciar serviço DHCP automaticamente
        restart_info = restart_dhcp_service()
        if not restart_info['success']:
            log_action(f"Aviso: Falha ao reiniciar o serviço DHCP após atualização: {restart_info['message']}")

        return jsonify({
            'message': f'Host {host_name} atualizado com sucesso!',
            'success': True,
            'data': {
                'host_name': host_name,
                'mac_address': new_mac_address,
                'ip_address': new_ip_address
            }
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500

@dhcp_bp.route('/hosts/<string:host_name>', methods=['PATCH'])
@login_required
def update_host_name(host_name):
    """Atualiza o nome de um host existente no dhcpd.conf."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'message': 'Dados JSON são obrigatórios',
                'success': False
            }), 400
        
        new_host_name = data.get('new_host_name', '').strip()
        
        # Validações
        if not new_host_name:
            return jsonify({
                'message': 'Novo nome do host é obrigatório',
                'success': False
            }), 400
        
        new_host_name_clean = new_host_name.replace(' ', '_').replace('-', '_')
        
        # Verificar se o novo nome do host já existe
        hosts_data = parse_dhcp_conf(DHCP_CONF_PATH)
        existing_names = [host['name'] for host in hosts_data if host['name'] != host_name]
        if new_host_name_clean in existing_names:
            return jsonify({
                'message': f'O novo nome do host {new_host_name} já está em uso',
                'success': False
            }), 400
            
        # Realizar a atualização no arquivo
        with open(DHCP_CONF_PATH, 'r') as f:
            content = f.read()

        # Regex para encontrar e substituir o nome do host
        # Procura por 'host NOME_ANTIGO {' e substitui por 'host NOVO_NOME {'
        pattern = r'(\s*host\s+)' + re.escape(host_name) + r'(\s*\{)'
        new_content = re.sub(pattern, r'\1' + new_host_name_clean + r'\2', content)

        # Se a substituição ocorreu (ou seja, o host foi encontrado)
        if new_content != content:
            with open(DHCP_CONF_PATH, 'w') as f:
                f.write(new_content)
                
            # Obter dados do host antes de atualizar para o log
            host_to_update = None
            for host in hosts_data:
                if host['name'] == host_name:
                    host_to_update = host
                    break
                    
            # Registrar log de auditoria
            if host_to_update:
                rule_name = find_rule_for_ip(host_to_update['ip_address'], parse_ip_ranges(IPS_SCRIPT_PATH))
                log_action(f"Renomeou host de '{host_name}' para '{new_host_name_clean}' (MAC: {host_to_update['mac_address']}, IP: {host_to_update['ip_address']}, Regra: {rule_name})")
            
            # Reiniciar serviço DHCP automaticamente
            restart_info = restart_dhcp_service()
            if not restart_info['success']:
                log_action(f"Aviso: Falha ao reiniciar o serviço DHCP após renomear: {restart_info['message']}")

            return jsonify({
                'message': f'Nome do host atualizado para {new_host_name} com sucesso!',
                'success': True,
                'data': {
                    'old_host_name': host_name,
                    'new_host_name': new_host_name
                }
            })
        else:
            return jsonify({
                'message': f'Host {host_name} não encontrado para renomear.',
                'success': False
            }), 404
        
    except Exception as e:
        return jsonify({
            'message': f'Erro interno do servidor: {str(e)}',
            'success': False
        }), 500
