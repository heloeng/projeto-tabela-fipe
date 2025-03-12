from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crud_stores import create_store, get_all_stores, get_store_by_id, update_store, delete_store

app = FastAPI()

#  Definição do modelo para entrada de dados (JSON)
class StoreCreate(BaseModel):
    name: str
    city: str
    state: str
    street: str
    neighborhood: str
    number: str
    zip_code: str

# Rota de Boas-Vindas
@app.get("/")
def home():
    return {"message": "API de Lojas está rodando!"}

# Criar uma nova loja (agora aceita JSON corretamente)
@app.post("/stores/")
def api_create_store(store: StoreCreate):
    try:
        create_store(
            store.name, store.city, store.state, 
            store.street, store.neighborhood, store.number, store.zip_code
        )
        return {"message": f"Loja '{store.name}' criada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  Listar todas as lojas
@app.get("/stores/")
def api_get_all_stores():
    stores = get_all_stores()
    return {"stores": stores}

# Buscar uma loja pelo ID
@app.get("/stores/{store_id}")
def api_get_store_by_id(store_id: int):
    store = get_store_by_id(store_id)
    if store:
        return {"store": store}
    raise HTTPException(status_code=404, detail="Loja não encontrada")

# Atualizar uma loja pelo ID (deve receber JSON no Body)
@app.put("/stores/{store_id}")
def api_update_store(store_id: int, store: StoreCreate):
    try:
        update_store(
            store_id, store.name, store.city, store.state, 
            store.street, store.neighborhood, store.number, store.zip_code
        )
        return {"message": f"Loja ID {store_id} atualizada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deletar uma loja pelo ID
@app.delete("/stores/{store_id}")
def api_delete_store(store_id: int):
    try:
        delete_store(store_id)
        return {"message": f"Loja ID {store_id} removida com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
