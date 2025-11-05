# Gerenciamento de Usuários (Administrativo)

Como a opção de registro de usuário foi removida da interface web principal para manter um controle mais centralizado, novos usuários devem ser criados administrativamente. Existem duas maneiras principais de fazer isso:

## 1. Criação de Usuário via Console Flask (Recomendado para Desenvolvimento/Testes)

Esta é a forma mais simples de adicionar usuários diretamente ao banco de dados da aplicação usando o shell interativo do Flask. É ideal para ambientes de desenvolvimento ou para adicionar um número limitado de usuários.

**Passos:**

1.  **Navegue até o diretório raiz da sua aplicação `dhcp_manager`** no terminal.
    ```bash
    cd /home/ubuntu/dhcp_manager
    ```

2.  **Ative o ambiente virtual**:
    ```bash
    source venv/bin/activate
    ```

3.  **Abra o shell interativo do Flask**:
    ```bash
    flask shell
    ```

4.  Dentro do shell, **importe os módulos necessários e crie um novo usuário**:
    ```python
    from src.models.user import db, User
    from src.main import app

    with app.app_context():
        # Exemplo: Criar um usuário 'admin' com email 'admin@example.com' e senha 'sua_senha_segura'
        username = input("Digite o nome de usuário: ")
        email = input("Digite o email do usuário: ")
        password = input("Digite a senha do usuário: ")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            print(f"Usuário com nome '{username}' ou email '{email}' já existe.")
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuário '{username}' criado com sucesso!")

        # Para listar todos os usuários (opcional)
        print("\nUsuários existentes:")
        for user in User.query.all():
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    ```

5.  **Saia do shell Flask** digitando `exit()` e pressionando Enter.

## 2. Criação de Usuário via Script Python (Para Automação)

Para cenários onde você precisa adicionar vários usuários ou automatizar o processo, você pode criar um script Python separado.

**Passos:**

1.  **Crie um novo arquivo** (por exemplo, `create_user.py`) no diretório raiz da sua aplicação `dhcp_manager`:
    ```bash
    touch /home/ubuntu/dhcp_manager/create_user.py
    ```

2.  **Adicione o seguinte código ao `create_user.py`**:
    ```python
    import os
    from src.models.user import db, User
    from src.main import app

    def create_admin_user(username, email, password):
        with app.app_context():
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                print(f"Usuário com nome '{username}' ou email '{email}' já existe.")
                return False

            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuário '{username}' criado com sucesso!")
            return True

    if __name__ == '__main__':
        # Exemplo de uso: crie um usuário admin por padrão se não existir
        print("Criando usuário administrativo...")
        create_admin_user("admin", "admin@casacivil.ce.gov.br", "sua_senha_segura")
        # Você pode adicionar mais chamadas para criar outros usuários aqui
        # create_admin_user("outro_usuario", "outro@casacivil.ce.gov.br", "outra_senha")
    ```

3.  **Execute o script**:
    ```bash
    cd /home/ubuntu/dhcp_manager
    source venv/bin/activate
    python create_user.py
    ```

Lembre-se de substituir `"sua_senha_segura"` por uma senha forte e segura em um ambiente de produção. Para maior segurança, considere usar variáveis de ambiente para senhas em scripts de automação. Após a criação, o usuário poderá fazer login na aplicação web normalmente.
