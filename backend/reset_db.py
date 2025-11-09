"""
Reset/Clean the vector database if corrupted
"""
import shutil
from pathlib import Path

# Path to vector database
db_path = Path(__file__).parent.parent / "data" / "vector_db"

print("=" * 60)
print("Vector Database Reset Tool")
print("=" * 60)
print(f"\nDatabase location: {db_path}")

if db_path.exists():
    print(f"\nFound existing database with {len(list(db_path.glob('*')))} files")
    
    response = input("\nDo you want to DELETE the entire vector database? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\nDeleting vector database...")
        shutil.rmtree(db_path)
        print("✓ Database deleted!")
        print("\nThe database will be recreated on next server start.")
        print("You'll need to re-upload all your documents.")
    else:
        print("\nCancelled. Database not deleted.")
else:
    print("\nNo existing database found. Nothing to delete.")

print("\n" + "=" * 60)
