from create_users_table import create_users_table
from create_research_table import create_research_table
from create_brands_table import create_brands_table
from create_models_table import create_models_table
from create_vehicles_table import create_vehicles_table
from create_register_table import create_register_table
from create_stores_table import create_stores_table

def main():
    print("Verificando e criando tabelas no banco de dados...")

    
    create_users_table()
    create_stores_table()
    create_research_table()
    create_brands_table()
    create_models_table()
    create_vehicles_table()
    create_register_table()

    print("Todas as tabelas foram verificadas e criadas se necessário!")

if __name__ == "__main__":
    main()