#!/usr/bin/env python3
"""
Simple script to create database tables.
Run this via Railway CLI or locally with DATABASE_URL set.

Usage:
  # Via Railway:
  railway run python scripts/create_tables.py

  # Locally:
  export DATABASE_URL="postgresql://..."
  python scripts/create_tables.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.db import Base, engine

def create_tables():
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully!")
        return 0
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(create_tables())
