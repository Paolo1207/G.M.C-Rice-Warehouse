# How to Export Your Render PostgreSQL Database

There are several ways to export your database. Choose the method that works best for you.

## Method 1: Using Render Dashboard (Easiest)

1. Go to your Render dashboard: https://dashboard.render.com
2. Navigate to your PostgreSQL database
3. Click on the database
4. Go to the "Info" tab
5. Copy the **Internal Database URL** or **External Connection String**
6. Use it in one of the export scripts below

## Method 2: Using pg_dump (Recommended)

### Prerequisites:
- Install PostgreSQL client tools:
  - **Windows**: Download from https://www.postgresql.org/download/windows/
  - Or use: `pip install psycopg2-binary`

### Steps:

1. Get your database URL from Render dashboard (Internal Database URL)

2. Run this command in PowerShell:
```powershell
cd "C:\Users\Admin\Desktop\GMC SYSTEM\backend"
# Set your DATABASE_URL
$env:DATABASE_URL="postgresql://user:password@host:port/database"
# Export database
pg_dump $env:DATABASE_URL --no-owner --no-acl > database_export.sql
```

Or if DATABASE_URL is in your .env file:
```powershell
python export_database.py
```

## Method 3: Using Python Script (No pg_dump Required)

1. Make sure you have the dependencies:
```powershell
pip install sqlalchemy psycopg2-binary python-dotenv
```

2. Add your DATABASE_URL to `.env` file:
```
DATABASE_URL=postgresql://user:password@host:port/database
```

3. Run the Python export script:
```powershell
cd "C:\Users\Admin\Desktop\GMC SYSTEM\backend"
python export_database_python.py
```

This will create `database_export.sql` file.

## Method 4: Using psql (Command Line)

```powershell
# Connect and export
psql "postgresql://user:password@host:port/database" -c "\copy (SELECT * FROM table_name) TO 'export.csv' CSV HEADER"
```

## After Export

Once you have the `database_export.sql` file:

1. **To share with me**: You can upload it to a file sharing service (Google Drive, Dropbox) and share the link, OR paste the contents here (if it's small enough).

2. **File size considerations**:
   - If the file is > 50MB, consider compressing it (.zip)
   - You can also export just the schema (no data) if you only need structure

## Export Schema Only (No Data)

If you only need the table structure:

```powershell
pg_dump $env:DATABASE_URL --schema-only --no-owner --no-acl > schema_only.sql
```

## Export Data Only (No Schema)

```powershell
pg_dump $env:DATABASE_URL --data-only --no-owner --no-acl > data_only.sql
```

## Troubleshooting

### "pg_dump: command not found"
- Install PostgreSQL client tools (see Method 2 prerequisites)

### "Connection refused" or "Could not connect"
- Make sure you're using the **External Connection String** from Render
- Check if your IP is whitelisted in Render's database settings
- Render PostgreSQL uses port 5432 by default

### "Permission denied"
- Make sure you're using the correct database user credentials
- Check if the database user has read permissions

## Getting Your Database URL from Render

1. Log in to https://dashboard.render.com
2. Click on your PostgreSQL database service
3. Go to "Info" tab
4. Copy the connection string:
   - **Internal Database URL** (for use within Render)
   - **External Connection String** (for use from your local machine)

The format will be:
```
postgresql://username:password@hostname:port/databasename
```

