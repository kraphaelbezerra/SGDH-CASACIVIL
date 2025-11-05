# Pesquisa sobre Autenticação em Flask

## Bibliotecas Principais

### 1. Flask-Login
- **Uso**: Autenticação baseada em sessões para aplicações web tradicionais
- **Vantagens**:
  - Simples de implementar
  - Gerenciamento automático de sessões
  - Decorador `@login_required` para proteger rotas
  - Objeto `current_user` para acessar dados do usuário logado
  - Ideal para aplicações web com formulários HTML
- **Desvantagens**:
  - Não é adequado para APIs REST stateless
  - Dependente de cookies/sessões
- **Quando usar**: Aplicações web tradicionais com interface HTML

### 2. Flask-JWT-Extended
- **Uso**: Autenticação baseada em tokens JWT para APIs REST
- **Vantagens**:
  - Stateless (sem necessidade de sessões)
  - Ideal para APIs REST
  - Suporte a refresh tokens
  - Tokens podem ser usados em diferentes domínios
  - Melhor para aplicações SPA (Single Page Applications)
- **Desvantagens**:
  - Mais complexo de implementar
  - Requer gerenciamento manual de tokens
- **Quando usar**: APIs REST, SPAs, aplicações móveis

### 3. Flask-Security
- **Uso**: Solução completa de segurança
- **Vantagens**:
  - Inclui autenticação, autorização, confirmação de email, etc.
  - Muito completo e robusto
- **Desvantagens**:
  - Pode ser excessivo para aplicações simples
  - Curva de aprendizado maior

## Decisão para o Projeto DHCP Manager

Para nossa aplicação de gerenciamento DHCP, **Flask-Login** é a escolha mais adequada porque:

1. **Interface Web**: Nossa aplicação tem uma interface web HTML/CSS/JS
2. **Simplicidade**: Flask-Login é mais simples de implementar
3. **Funcionalidade**: Atende perfeitamente às necessidades de autenticação básica
4. **Compatibilidade**: Funciona bem com o template Flask existente

## Implementação Planejada

1. **Modelo de Usuário**: Usar SQLAlchemy com UserMixin
2. **Rotas de Autenticação**: Login, logout, registro
3. **Proteção de Rotas**: Usar `@login_required` nas rotas da API DHCP
4. **Interface**: Adicionar formulários de login/registro ao frontend
5. **Segurança**: Hash de senhas com werkzeug.security
