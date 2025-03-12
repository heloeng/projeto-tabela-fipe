from db_connection import create_connection

def insert_resgister(id_campaign, id_user, id_store, id_vehicle, year_man, price, reg_date):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO register_table (id_campaign, id_user, id_store, id_vehicle, year_man, price, reg_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (id_campaign, id_user, id_store, id_vehicle, year_man, price, reg_date))

    #(SELECT id_model FROM models_table WHERE name = %s)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Registro realizado com sucesso!")


if __name__ == "__main__":
    #  Atribuir o pesquisador "Paulo Souza" (id_user=1) à "Loja Centro" (id_store=1)
    insert_resgister(4, 4, 7, 1, 2021, 65250.00, "2024-03-12")

    #  Atribuir a pesquisadora "Heloiza Mendes" (id_user=3) à Loja 2
#    insert_research("2024-03-13", None, 1, 8)
