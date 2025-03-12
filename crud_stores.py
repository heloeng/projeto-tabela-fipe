from db_connection import create_connection

#  CREATE: Inserir uma nova loja no banco de dados
def create_store(name, city, state, street, neighborhood, number, zip_code):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO stores_table (name, city, state, street, neighborhood, number, zip_code) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_store;
    """, (name, city, state, street, neighborhood, number, zip_code))

    store_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Loja '{name}' criada com sucesso! ID: {store_id}")

# READ (Todos): Buscar todas as lojas cadastradas
def get_all_stores():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stores_table;")
    stores = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    print(" Lista de Lojas:")
    for store in stores:
        print(store)
    
    return stores

# READ (Por ID): Buscar uma loja específica pelo ID
def get_store_by_id(store_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stores_table WHERE id_store = %s;", (store_id,))
    store = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if store:
        print(f" Loja encontrada: {store}")
    else:
        print(f" Nenhuma loja encontrada com ID {store_id}")
    
    return store

# UPDATE: Atualizar informações de uma loja pelo ID
def update_store(store_id, name=None, city=None, state=None, street=None, neighborhood=None, number=None, zip_code=None):
    conn = create_connection()
    cursor = conn.cursor()

    updates = []
    values = []
    
    if name:
        updates.append("name = %s")
        values.append(name)
    if city:
        updates.append("city = %s")
        values.append(city)
    if state:
        updates.append("state = %s")
        values.append(state)
    if street:
        updates.append("street = %s")
        values.append(street)
    if neighborhood:
        updates.append("neighborhood = %s")
        values.append(neighborhood)
    if number:
        updates.append("number = %s")
        values.append(number)
    if zip_code:
        updates.append("zip_code = %s")
        values.append(zip_code)
    
    values.append(store_id)

    sql_query = f"UPDATE stores_table SET {', '.join(updates)} WHERE id_store = %s"
    cursor.execute(sql_query, values)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Loja ID {store_id} atualizada com sucesso!")

# DELETE: Remover uma loja pelo ID
def delete_store(store_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM stores_table WHERE id_store = %s", (store_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    print(f" Loja ID {store_id} removida com sucesso!")

# Testando as funções
if __name__ == "__main__":
    # Criar uma nova loja
    create_store("Loja Norte", "Rio de Janeiro", "RJ", "Av. Brasil", "Centro", "456", "21000-000")

    # Buscar todas as lojas
    get_all_stores()

    # Buscar uma loja específica pelo ID
    get_store_by_id(1)  # Substitua pelo ID desejado

    # Atualizar uma loja
    update_store(1, name="Loja Centro Atualizada", city="São Paulo")

    # Deletar uma loja
    delete_store(2)
