#!/bin/bash
# Script para verificar IPs disponíveis a partir do dhcpd.conf
# Autor: ChatGPT + Karlos

CONF="/etc/dhcp/dhcpd.conf"   # ajuste o caminho do dhcpd.conf

# Extrai todos os IPs já usados no dhcpd.conf
USADOS=$(grep -oP 'fixed-address\s+\K[\d.]+' "$CONF" | sort -u)

# Função para gerar todos os IPs de um range
gera_range() {
    ip_start=$1
    ip_end=$2

    IFS=. read -r s1 s2 s3 s4 <<< "$ip_start"
    IFS=. read -r e1 e2 e3 e4 <<< "$ip_end"

    for i in $(seq $s4 $e4); do
        echo "$s1.$s2.$s3.$i"
    done
}

# Função para checar regra
checa_regra() {
    categoria="$1"
    acesso="$2"
    inicio="$3"
    fim="$4"

    echo "--------------------------------------------------"
    echo "$categoria - $acesso ($inicio - $fim)"

    TOTAL=0
    LIVRES=()
    for ip in $(gera_range $inicio $fim); do
        TOTAL=$((TOTAL+1))
        if ! echo "$USADOS" | grep -q "^$ip$"; then
            LIVRES+=("$ip")
        fi
    done

    OCUPADOS=$((TOTAL - ${#LIVRES[@]}))
    echo "Total: $TOTAL | Ocupados: $OCUPADOS | Livres: ${#LIVRES[@]}"

    if [ ${#LIVRES[@]} -gt 0 ]; then
        echo "IPs Livres (até 10): ${LIVRES[@]:0:10}"
    fi
}

# --------- Regras ----------
checa_regra "Access Point" "Apenas rede local"  "10.8.28.0" "10.8.28.99"
checa_regra "Access Point" "Internet NAT"       "10.8.28.100" "10.8.28.125"
checa_regra "Ativos de Rede" "Apenas rede local" "10.8.31.0" "10.8.31.254"
checa_regra "Celular" "Internet NAT"            "10.8.21.0" "10.8.21.255"
checa_regra "Celular" "Internet com proxy"      "10.8.19.0" "10.8.19.99"
checa_regra "Celular" "Internet sem Proxy"      "10.8.22.0" "10.8.22.255"
checa_regra "Desktop" "Internet NAT"            "10.8.6.12" "10.8.7.185"
checa_regra "Desktop" "Internet sem proxy"      "10.8.4.24" "10.8.5.225"
checa_regra "Desktop" "Internet com proxy"      "10.8.2.36" "10.8.3.152"
checa_regra "Desktop" "Apenas rede local"       "10.8.2.0" "10.8.2.35"
checa_regra "Equipamento" "Internet NAT"        "10.8.7.186" "10.8.7.255"
checa_regra "Equipamento" "Internet com proxy"  "10.8.3.153" "10.8.4.23"
checa_regra "Equipamento" "Apenas rede local"   "10.8.0.50" "10.8.0.200"
checa_regra "Notebook" "Internet NAT"           "10.8.13.12" "10.8.14.255"
checa_regra "Notebook" "Internet sem proxy"     "10.8.11.24" "10.8.13.11"
checa_regra "Notebook" "Internet com proxy"     "10.8.9.36" "10.8.11.23"
checa_regra "Notebook" "Apenas rede local"      "10.8.9.0" "10.8.9.35"
checa_regra "Outros" "Internet NAT"             "10.8.29.156" "10.8.29.255"
checa_regra "Outros" "Internet com proxy"       "10.8.28.212" "10.8.29.55"
checa_regra "Outros" "Apenas rede local"        "10.8.28.175" "10.8.28.211"
checa_regra "Servidores" "Internet sem proxy"   "10.8.30.0" "10.8.30.255"
checa_regra "Tablet" "Internet NAT"             "10.8.17.44" "10.8.17.255"
checa_regra "Tablet" "Internet sem proxy"       "10.8.16.100" "10.8.17.43"
checa_regra "Tablet" "Internet com proxy"       "10.8.16.0" "10.8.16.99"
checa_regra "Temporário" "Internet NAT"         "10.8.25.192" "10.8.25.255"
checa_regra "Temporário" "Internet sem proxy"   "10.8.24.64" "10.8.25.191"
checa_regra "Temporário" "Internet com proxy"   "10.8.23.0" "10.8.24.63"
