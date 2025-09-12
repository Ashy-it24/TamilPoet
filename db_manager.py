"""
Database manager for custom Tamil dictionary entries
"""
import os
import psycopg2
import streamlit as st
from typing import Dict, List, Tuple, Optional

def get_db_connection():
    """Get database connection from environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PGHOST'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            port=os.getenv('PGPORT', '5432')
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def create_dictionary_table():
    """Create the custom_dictionary table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_dictionary (
                id SERIAL PRIMARY KEY,
                old_word VARCHAR(255) NOT NULL UNIQUE,
                modern_word VARCHAR(255) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error creating dictionary table: {str(e)}")
        if conn:
            conn.close()
        return False

def load_custom_dictionary() -> Dict[str, str]:
    """Load custom dictionary entries from database"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT old_word, modern_word FROM custom_dictionary")
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {old: modern for old, modern in entries}
    except Exception as e:
        st.error(f"Error loading custom dictionary: {str(e)}")
        if conn:
            conn.close()
        return {}

def add_dictionary_entry(old_word: str, modern_word: str, description: str = "") -> bool:
    """Add or update a dictionary entry"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO custom_dictionary (old_word, modern_word, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (old_word)
            DO UPDATE SET 
                modern_word = EXCLUDED.modern_word,
                description = EXCLUDED.description,
                updated_at = CURRENT_TIMESTAMP
        """, (old_word.strip(), modern_word.strip(), description.strip()))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding dictionary entry: {str(e)}")
        if conn:
            conn.close()
        return False

def delete_dictionary_entry(old_word: str) -> bool:
    """Delete a dictionary entry"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM custom_dictionary WHERE old_word = %s", (old_word,))
        deleted = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return deleted
    except Exception as e:
        st.error(f"Error deleting dictionary entry: {str(e)}")
        if conn:
            conn.close()
        return False

def get_all_dictionary_entries() -> List[Tuple[str, str, str]]:
    """Get all dictionary entries with descriptions"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT old_word, modern_word, COALESCE(description, '') 
            FROM custom_dictionary 
            ORDER BY old_word
        """)
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        return entries
    except Exception as e:
        st.error(f"Error fetching dictionary entries: {str(e)}")
        if conn:
            conn.close()
        return []

def search_dictionary_entries(search_term: str) -> List[Tuple[str, str, str]]:
    """Search dictionary entries by old word or modern word"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT old_word, modern_word, COALESCE(description, '')
            FROM custom_dictionary 
            WHERE old_word ILIKE %s OR modern_word ILIKE %s
            ORDER BY old_word
        """, (f'%{search_term}%', f'%{search_term}%'))
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        return entries
    except Exception as e:
        st.error(f"Error searching dictionary entries: {str(e)}")
        if conn:
            conn.close()
        return []

# Initialize database on import
if __name__ != "__main__":
    create_dictionary_table()