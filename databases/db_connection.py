import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "fipe")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def create_connection():
    """Cria e retorna uma conexão com o PostgreSQL"""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
