
import sys
import argparse
from sqlmodel import Session, select
from src.core.database import engine
from src.core.models import Client

def add_client(name: str, key: str):
    with Session(engine) as session:
        # Check if exists
        statement = select(Client).where(Client.client_key == key)
        existing = session.exec(statement).first()
        
        if existing:
            print(f"❌ Error: Client with key '{key}' already exists (Name: {existing.name}).")
            return

        new_client = Client(name=name, client_key=key, is_active=True)
        session.add(new_client)
        session.commit()
        session.refresh(new_client)
        print(f"✅ Success: Client '{name}' added with key '{key}'. (ID: {new_client.id})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new client to JotaDB")
    parser.add_argument("name", help="Name of the client")
    parser.add_argument("key", help="Unique API Key for the client")
    
    args = parser.parse_args()
    
    try:
        add_client(args.name, args.key)
    except Exception as e:
        print(f"❌ unexpected Error: {e}")
