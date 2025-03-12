from create_users_table import create_users_table
from create_stores_table import create_stores_table
from create_research_table import create_research_table


def main():
    print("Verificando e criando tabelas no banco de dados...")

    
    create_users_table()
    create_stores_table()
    create_research_table()

    print("Todas as tabelas foram verificadas e criadas se necessário!")

if __name__ == "__main__":
    main()