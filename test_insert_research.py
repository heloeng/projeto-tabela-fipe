from db_connection import create_connection

def insert_research(assigned_date, completion_date, user_id, store_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO research_table (assigned_date, completion_date, user_id, store_id)
        VALUES (%s, %s, %s, %s);
    """, (assigned_date, completion_date, user_id, store_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Pesquisa atribuída ao usuário ID {user_id} para a loja ID {store_id}!")

if __name__ == "__main__":
    #  Atribuir o pesquisador "Paulo Souza" (id_user=1) à "Loja Centro" (id_store=1)
    insert_research("2024-03-12", None, 4, 7)

    #  Atribuir a pesquisadora "Heloiza Mendes" (id_user=3) à Loja 2
    insert_research("2024-03-13", None, 1, 8)