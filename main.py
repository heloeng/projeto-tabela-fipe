from create_users_table import create_users_table
from create_stores_table import create_stores_table

def main():
    print("Verificando e criando tabelas no banco de dados...")

    create_stores_table()
    create_users_table()
   

    print("Todas as tabelas foram verificadas e criadas se necessário!")

if __name__ == "__main__":
    main()