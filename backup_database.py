#!/usr/bin/env python3
"""
Database Backup Script
Backs up PostgreSQL schema and data to SQL file
"""

import psycopg2
import os
from datetime import datetime

# Database connection details
DB_HOST = "dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com"
DB_PORT = 5432
DB_NAME = "ai_receptionist_3gp5"
DB_USER = "ranga"
DB_PASSWORD = "lQHuZjjAtYduMoYuAL6FSHTsBd75u3Qd"

def backup_database():
    """Create a complete database backup"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.sql")
    
    print("\n" + "="*80)
    print("DATABASE BACKUP UTILITY")
    print("="*80)
    print(f"\nBackup file: {backup_file}")
    print(f"Database: {DB_NAME}")
    print(f"Host: {DB_HOST}")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASSWORD, sslmode="require"
        )
        cursor = conn.cursor()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"-- Database Backup\n")
            f.write(f"-- Database: {DB_NAME}\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- PostgreSQL Version: ")
            
            cursor.execute("SELECT version()")
            f.write(cursor.fetchone()[0].split(',')[0] + "\n")
            f.write("\n" + "="*80 + "\n\n")
            
            # Backup ENUM types
            print("\n[1] Backing up ENUM types...")
            cursor.execute("""
                SELECT typname, enumlabel
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                ORDER BY typname, enumsortorder
            """)
            
            enums = {}
            for typename, label in cursor.fetchall():
                if typename not in enums:
                    enums[typename] = []
                enums[typename].append(label)
            
            f.write("-- ENUM Types\n")
            for typename, labels in enums.items():
                f.write(f"DROP TYPE IF EXISTS {typename} CASCADE;\n")
                f.write(f"CREATE TYPE {typename} AS ENUM (")
                f.write(", ".join(f"'{label}'" for label in labels))
                f.write(");\n\n")
            
            print(f"  ✓ Backed up {len(enums)} enum types")
            
            # Backup tables (schema only first)
            print("\n[2] Backing up table schemas...")
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            f.write("\n-- Tables\n")
            for table in tables:
                # Get CREATE TABLE statement (simplified)
                cursor.execute(f"""
                    SELECT column_name, data_type, character_maximum_length, 
                           is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                
                f.write(f"\nDROP TABLE IF EXISTS {table} CASCADE;\n")
                f.write(f"CREATE TABLE {table} (\n")
                
                columns = []
                for col_name, data_type, max_len, nullable, default in cursor.fetchall():
                    col_def = f"    {col_name} {data_type.upper()}"
                    if max_len:
                        col_def += f"({max_len})"
                    if nullable == 'NO':
                        col_def += " NOT NULL"
                    if default:
                        col_def += f" DEFAULT {default}"
                    columns.append(col_def)
                
                f.write(",\n".join(columns))
                f.write("\n);\n")
            
            print(f"  ✓ Backed up {len(tables)} table schemas")
            
            # Backup data
            print("\n[3] Backing up table data...")
            f.write("\n-- Data\n")
            
            total_rows = 0
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                if row_count > 0:
                    f.write(f"\n-- Data for {table} ({row_count} rows)\n")
                    
                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    # Get data
                    cursor.execute(f"SELECT * FROM {table}")
                    for row in cursor.fetchall():
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped = val.replace("'", "''")
                                values.append(f"'{escaped}'")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                values.append(f"'{str(val)}'")
                        
                        f.write(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                    
                    total_rows += row_count
                    print(f"  ✓ {table}: {row_count} rows")
            
            # Backup views
            print("\n[4] Backing up views...")
            cursor.execute("""
                SELECT table_name, view_definition 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            views = cursor.fetchall()
            
            f.write("\n-- Views\n")
            for view_name, definition in views:
                f.write(f"\nCREATE OR REPLACE VIEW {view_name} AS\n{definition};\n")
            
            print(f"  ✓ Backed up {len(views)} views")
            
            # Backup functions
            print("\n[5] Backing up functions...")
            cursor.execute("""
                SELECT proname, pg_get_functiondef(oid)
                FROM pg_proc
                WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
                AND prokind = 'f'
            """)
            functions = cursor.fetchall()
            
            f.write("\n-- Functions\n")
            for func_name, func_def in functions:
                f.write(f"\n{func_def};\n")
            
            print(f"  ✓ Backed up {len(functions)} functions")
        
        cursor.close()
        conn.close()
        
        # Get file size
        file_size = os.path.getsize(backup_file)
        size_kb = file_size / 1024
        
        print("\n" + "="*80)
        print("✓ BACKUP COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"\nBackup Summary:")
        print(f"  • File: {backup_file}")
        print(f"  • Size: {size_kb:.2f} KB")
        print(f"  • Tables: {len(tables)}")
        print(f"  • Total rows: {total_rows}")
        print(f"  • Views: {len(views)}")
        print(f"  • Functions: {len(functions)}")
        print(f"  • Enums: {len(enums)}")
        print("\n" + "="*80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(backup_database())
