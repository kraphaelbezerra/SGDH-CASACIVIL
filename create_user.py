import os
import sys
import getpass
from src.models.user import db, User
from src.main import app

class UserManager:
    def __init__(self):
        self.app = app
    
    def create_user(self, username=None, email=None, password=None):
        """Cria um novo usuário"""
        with self.app.app_context():
            # Coletar dados interativamente se não fornecidos
            if not username:
                username = input("Nome de usuário: ").strip()
            if not email:
                email = input("Email: ").strip()
            if not password:
                password = getpass.getpass("Senha: ")
                confirm_password = getpass.getpass("Confirmar senha: ")
                if password != confirm_password:
                    print("❌ Erro: As senhas não coincidem!")
                    return False
            
            # Validar dados
            if not username or not email or not password:
                print("❌ Erro: Todos os campos são obrigatórios!")
                return False
            
            # Verificar se usuário já existe
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                print(f"❌ Usuário com nome '{username}' ou email '{email}' já existe.")
                return False
            
            # Criar novo usuário
            try:
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                print(f"✅ Usuário '{username}' criado com sucesso!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao criar usuário: {str(e)}")
                return False
    
    def change_password(self, username=None, new_password=None):
        """Altera a senha de um usuário"""
        with self.app.app_context():
            if not username:
                username = input("Nome de usuário para alterar senha: ").strip()
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ Usuário '{username}' não encontrado!")
                return False
            
            if not new_password:
                new_password = getpass.getpass("Nova senha: ")
                confirm_password = getpass.getpass("Confirmar nova senha: ")
                if new_password != confirm_password:
                    print("❌ Erro: As senhas não coincidem!")
                    return False
            
            try:
                user.set_password(new_password)
                db.session.commit()
                print(f"✅ Senha do usuário '{username}' alterada com sucesso!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao alterar senha: {str(e)}")
                return False
    
    def delete_user(self, username=None):
        """Exclui um usuário"""
        with self.app.app_context():
            if not username:
                username = input("Nome de usuário para excluir: ").strip()
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ Usuário '{username}' não encontrado!")
                return False
            
            # Confirmação de segurança
            confirm = input(f"⚠️  Tem certeza que deseja excluir o usuário '{username}'? (s/N): ")
            if confirm.lower() != 's':
                print("Operação cancelada.")
                return False
            
            try:
                db.session.delete(user)
                db.session.commit()
                print(f"✅ Usuário '{username}' excluído com sucesso!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao excluir usuário: {str(e)}")
                return False
    
    def list_users(self):
        """Lista todos os usuários"""
        with self.app.app_context():
            users = User.query.all()
            
            if not users:
                print("📭 Nenhum usuário encontrado.")
                return
            
            print("\n📋 Lista de Usuários:")
            print("-" * 60)
            print(f"{'ID':<5} {'Username':<20} {'Email':<30}")
            print("-" * 60)
            
            for user in users:
                print(f"{user.id:<5} {user.username:<20} {user.email:<30}")
            
            print(f"\nTotal: {len(users)} usuário(s)")
    
    def show_user_info(self, username=None):
        """Mostra informações de um usuário específico"""
        with self.app.app_context():
            if not username:
                username = input("Nome de usuário para visualizar: ").strip()
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"❌ Usuário '{username}' não encontrado!")
                return False
            
            print(f"\n👤 Informações do Usuário:")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Data de Criação: {user.created_at}")
            return True

def display_menu():
    """Exibe o menu de opções"""
    print("\n" + "="*50)
    print("          🛠️  GERENCIADOR DE USUÁRIOS")
    print("="*50)
    print("1. 📝 Criar usuário")
    print("2. 🔐 Alterar senha")
    print("3. 🗑️  Excluir usuário")
    print("4. 📋 Listar usuários")
    print("5. 👤 Ver informações do usuário")
    print("6. 🚪 Sair")
    print("="*50)

def main():
    """Função principal com menu interativo"""
    manager = UserManager()
    
    while True:
        display_menu()
        
        try:
            choice = input("\nEscolha uma opção (1-6): ").strip()
            
            if choice == '1':
                print("\n📝 CRIAR NOVO USUÁRIO")
                manager.create_user()
            
            elif choice == '2':
                print("\n🔐 ALTERAR SENHA")
                manager.change_password()
            
            elif choice == '3':
                print("\n🗑️  EXCLUIR USUÁRIO")
                manager.delete_user()
            
            elif choice == '4':
                print("\n📋 LISTAR USUÁRIOS")
                manager.list_users()
            
            elif choice == '5':
                print("\n👤 INFORMAÇÕES DO USUÁRIO")
                manager.show_user_info()
            
            elif choice == '6':
                print("\n👋 Saindo... Até logo!")
                break
            
            else:
                print("❌ Opção inválida! Escolha entre 1 e 6.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Operação cancelada pelo usuário. Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")

# Funções de uso direto (para chamadas programáticas)
def create_admin_user(username="admin", email="admin@casacivil.ce.gov.br", password=None):
    """Cria usuário administrativo (compatibilidade com versão anterior)"""
    manager = UserManager()
    
    if not password:
        password = getpass.getpass(f"Senha para {username}: ")
        confirm = getpass.getpass("Confirmar senha: ")
        if password != confirm:
            print("❌ Erro: As senhas não coincidem!")
            return False
    
    return manager.create_user(username, email, password)

def quick_create_user(username, email, password):
    """Cria usuário rapidamente via linha de comando"""
    manager = UserManager()
    return manager.create_user(username, email, password)

if __name__ == '__main__':
    # Verificar se há argumentos de linha de comando
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "create" and len(sys.argv) >= 5:
            # Uso: python script.py create username email password
            username = sys.argv[2]
            email = sys.argv[3]
            password = sys.argv[4]
            quick_create_user(username, email, password)
        
        elif command == "create-admin":
            # Uso: python script.py create-admin
            print("Criando usuário administrativo...")
            create_admin_user()
        
        elif command == "list":
            # Uso: python script.py list
            manager = UserManager()
            manager.list_users()
        
        elif command == "change-password" and len(sys.argv) >= 3:
            # Uso: python script.py change-password username
            username = sys.argv[2]
            manager = UserManager()
            manager.change_password(username)
        
        elif command == "delete" and len(sys.argv) >= 3:
            # Uso: python script.py delete username
            username = sys.argv[2]
            manager = UserManager()
            manager.delete_user(username)
        
        else:
            print("Comandos disponíveis:")
            print("  create <username> <email> <password>")
            print("  create-admin")
            print("  list")
            print("  change-password <username>")
            print("  delete <username>")
            print("\nOu execute sem argumentos para modo interativo")
    
    else:
        # Modo interativo
        main()
