"""
Rebuild Long-Term Memory Milvus Collection
Used to fix schema mismatch issues
"""
import sys
import os
import importlib

# Add project root directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pymilvus import MilvusClient

# Use importlib to import config module (module name starts with number)
config_module = importlib.import_module('05_config.settings')
Config = config_module.Config

def recreate_collection():
    """Rebuild long-term memory collection"""
    client = MilvusClient(Config.MILVUS_URI)
    
    collection_name = "long_term_memory_default"
    
    # Check if collection exists
    if client.has_collection(collection_name):
        print(f"🗑️  Deleting old collection: {collection_name}")
        client.drop_collection(collection_name)
        print(f"✅ Collection deleted")
    else:
        print(f"ℹ️  Collection {collection_name} does not exist")
    
    print("\n💡 New collection will be automatically created next time you run the program")
    print("   The new collection's content_preview field length is 600 bytes")

if __name__ == "__main__":
    recreate_collection()
