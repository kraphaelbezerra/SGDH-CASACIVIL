# Changelog - DHCP Manager v2

## Versão 2.1 - Funcionalidade de Edição de Hosts

### Data: 28 de Outubro de 2025

### 🎯 Objetivo
Implementar funcionalidade completa de edição de hosts cadastrados no sistema DHCP Manager.

### ✨ Novas Funcionalidades

#### 1. **Backend - Nova Rota de Edição**
- **Arquivo**: `src/routes/dhcp.py`
- **Rota**: `PUT /api/dhcp/hosts/<host_name>`
- **Funcionalidades**:
  - Edição de endereço MAC
  - Edição de endereço IP
  - Validação completa de formato MAC (regex)
  - Validação completa de formato IP (regex)
  - Verificação de duplicidade de MAC e IP
  - Verificação de regras e disponibilidade de IP
  - Atualização automática do arquivo `dhcpd.conf`
  - Backup automático antes de modificações
  - Tratamento de erros robusto

#### 2. **Frontend - Modal de Edição**
- **Arquivo**: `src/static/index.html`
- **Componentes Adicionados**:
  - Modal responsivo com design moderno
  - Formulário de edição com validações
  - Botão "Editar" em cada linha da tabela de hosts
  - Estilos CSS personalizados para o modal
  
- **Campos do Formulário**:
  - **Nome do Host**: Campo somente leitura (não editável)
  - **Endereço MAC**: Campo editável com formatação automática
  - **Endereço IP**: Campo editável com validação
  - **Seleção de Regra**: Dropdown opcional para trocar de regra
  - **IPs Disponíveis**: Lista dinâmica baseada na regra selecionada

#### 3. **JavaScript - Funções de Gerenciamento**
- **Funções Adicionadas**:
  - `openEditModal(hostName)`: Abre o modal e carrega dados do host
  - `closeEditModal()`: Fecha o modal e limpa o formulário
  - `updateHost()`: Envia requisição PUT para atualizar o host
  - `populateEditForm(host)`: Preenche o formulário com dados do host
  - Event listeners para gerenciar interações do usuário

### 🔧 Validações Implementadas

#### Backend
- ✅ Validação de formato MAC: `^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$`
- ✅ Validação de formato IP: `^(\d{1,3}\.){3}\d{1,3}$`
- ✅ Verificação de duplicidade de MAC (exceto o próprio host)
- ✅ Verificação de duplicidade de IP (exceto o próprio host)
- ✅ Validação de existência do host
- ✅ Validação de regras e IPs disponíveis

#### Frontend
- ✅ Formatação automática de MAC durante digitação
- ✅ Validação de campos obrigatórios
- ✅ Feedback visual de erros e sucessos
- ✅ Confirmação antes de salvar alterações

### 🎨 Melhorias de Interface

1. **Modal de Edição**:
   - Design consistente com o restante da aplicação
   - Animações suaves de abertura/fechamento
   - Overlay escuro para foco no modal
   - Botões com cores intuitivas (verde para salvar, vermelho para cancelar)
   - Ícone de lápis (✏️) no título do modal

2. **Tabela de Hosts**:
   - Botão "Editar" com cor azul para cada host
   - Botão "Apagar" mantido com cor vermelha
   - Layout responsivo e organizado

3. **Feedback ao Usuário**:
   - Mensagens de sucesso em verde
   - Mensagens de erro em vermelho
   - Atualização automática da lista após edição

### 📋 Fluxo de Edição

1. Usuário clica no botão "Editar" de um host
2. Modal abre com dados pré-preenchidos
3. Usuário modifica MAC e/ou IP
4. Opcionalmente seleciona nova regra
5. Clica em "Salvar Alterações"
6. Sistema valida os dados
7. Atualiza o arquivo `dhcpd.conf`
8. Fecha o modal e atualiza a tabela
9. Exibe mensagem de sucesso

### 🔒 Segurança

- ✅ Validação de entrada no backend e frontend
- ✅ Sanitização de dados antes de salvar
- ✅ Backup automático do arquivo de configuração
- ✅ Tratamento de erros para evitar corrupção de dados
- ✅ Verificação de permissões (usuário autenticado)

### 📦 Arquivos Modificados

1. **src/routes/dhcp.py**
   - Adicionada rota `PUT /api/dhcp/hosts/<host_name>`
   - Implementadas validações completas
   - Adicionada lógica de atualização do dhcpd.conf

2. **src/static/index.html**
   - Adicionado modal de edição (HTML)
   - Adicionados estilos CSS para o modal
   - Adicionadas funções JavaScript de gerenciamento
   - Adicionado botão "Editar" na tabela

### 🧪 Testes Realizados

- ✅ Login na aplicação
- ✅ Abertura do modal de edição
- ✅ Preenchimento automático dos campos
- ✅ Edição de endereço MAC
- ✅ Salvamento das alterações
- ✅ Atualização da tabela
- ✅ Botão Cancelar
- ✅ Validações de formato
- ✅ Tratamento de erros

### 📝 Notas Técnicas

- A edição do **nome do host** não é permitida para manter a integridade das referências
- O sistema cria backup automático antes de qualquer modificação
- As validações são executadas tanto no frontend quanto no backend
- A interface é totalmente responsiva e compatível com dispositivos móveis

### 🚀 Como Usar

1. Faça login no sistema
2. Acesse a aba "📋 Hosts Cadastrados"
3. Localize o host que deseja editar
4. Clique no botão "Editar" (azul)
5. Modifique os campos desejados
6. Clique em "Salvar Alterações"
7. Aguarde a confirmação de sucesso

### 👨‍💻 Desenvolvido por

Sistema modificado para incluir funcionalidade de edição de hosts conforme solicitação do usuário.

---

**Versão anterior**: v2.0 (apenas cadastro e exclusão)  
**Versão atual**: v2.1 (cadastro, edição e exclusão)
