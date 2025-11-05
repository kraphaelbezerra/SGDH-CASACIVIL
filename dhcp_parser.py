import re

def parse_dhcp_conf(file_path):
    """
    Analisa o arquivo dhcpd.conf para extrair informações de hosts.
    Retorna uma lista de dicionários, onde cada dicionário representa um host
    com 'name', 'mac_address' e 'ip_address'.
    """
    hosts = []
    with open(file_path, 'r') as f:
        content = f.read()

    # Regex para encontrar blocos 'host' e extrair nome, MAC e IP
    host_blocks = re.findall(r'host\s+([\w\d_.-]+)\s*\{([^}]+)\}', content, re.DOTALL)

    for host_name, block_content in host_blocks:
        mac_match = re.search(r'hardware\s+ethernet\s+([0-9a-fA-F:]{17});', block_content)
        ip_match = re.search(r'fixed-address\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3});', block_content)

        if mac_match and ip_match:
            date_match = re.search(r'#\s*Data:\s*(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', block_content)
            hosts.append({
                'name': host_name,
                'mac_address': mac_match.group(1),
                'ip_address': ip_match.group(1),
                'registration_date': date_match.group(1) if date_match else 'N/A'
            })
    return hosts

def get_used_ips(file_path):
    """
    Extrai todos os IPs fixos usados no arquivo dhcpd.conf.
    Retorna um conjunto de strings de endereços IP.
    """
    used_ips = set()
    with open(file_path, 'r') as f:
        content = f.read()
    
    ip_matches = re.findall(r'fixed-address\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3});', content)
    for ip in ip_matches:
        used_ips.add(ip)
    return used_ips


def parse_ip_ranges(file_path):
    """
    Analisa o script ips_disponiveis.sh para extrair as regras de ranges de IP.
    Retorna uma lista de dicionários, onde cada dicionário representa uma regra
    com 'categoria', 'acesso', 'inicio' e 'fim'.
    """
    rules = []
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search(r'checa_regra\s+\"([^\"]+)\"\s+\"([^\"]+)\"\s+\"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\"\s+\"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\"', line)
            if match:
                rules.append({
                    'categoria': match.group(1),
                    'acesso': match.group(2),
                    'inicio': match.group(3),
                    'fim': match.group(4)
                })
    return rules


# Exemplo de uso (para teste)
if __name__ == '__main__':
    dhcp_conf_path = '/home/ubuntu/upload/dhcpd.conf'
    ips_script_path = '/home/ubuntu/upload/ips_disponiveis.sh'

    print('--- Hosts existentes ---')
    hosts_data = parse_dhcp_conf(dhcp_conf_path)
    for host in hosts_data[:5]: # Mostrar os primeiros 5 para exemplo
        print(host)
    print(f'Total de hosts encontrados: {len(hosts_data)}\n')

    print('--- IPs usados ---')
    used_ips_data = get_used_ips(dhcp_conf_path)
    print(f'Total de IPs usados: {len(used_ips_data)}\n')

    print('--- Regras de IP ---')
    ip_rules_data = parse_ip_ranges(ips_script_path)
    for rule in ip_rules_data:
        print(rule)
    print(f'Total de regras de IP encontradas: {len(ip_rules_data)}\n')

