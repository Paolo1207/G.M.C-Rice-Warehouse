# 🗄️ PostgreSQL Database Setup in pgAdmin 4

## 📋 Step-by-Step Guide

### 1. **Connect to Render Database in pgAdmin 4**

1. **Open pgAdmin 4**
2. **Right-click on "Servers"** in the left panel
3. **Select "Register" → "Server..."**
4. **Fill in the connection details:**

   **General Tab:**
   - **Name**: `GMC Render Database`

   **Connection Tab:**
   - **Host name/address**: `dpg-d3cd1j2li9vc73df7i10-a.oregon-postgres.render.com`
   - **Port**: `5432`
   - **Maintenance database**: `gmcdb`
   - **Username**: `gmcdb_user`
   - **Password**: `Ch9zA0bxdMgqWwsuUsbfoVRts0qxbhGz`

5. **Click "Save"**

### 2. **Create Database Schema**

1. **Expand your server** → **Databases** → **gmcdb**
2. **Right-click on "gmcdb"** → **Query Tool**
3. **Copy and paste the contents** of `backend/schema_postgresql.sql`
4. **Click the "Execute" button** (⚡ icon)

### 3. **Verify Tables Created**

After running the schema, you should see these tables:
- ✅ `branches`
- ✅ `products` 
- ✅ `users`
- ✅ `inventory_items`
- ✅ `restock_logs`
- ✅ `sales_transactions`
- ✅ `forecast_data`

### 4. **Test Connection from App**

Once the schema is created, your Render app should be able to connect and use the database!

## 🔧 **Connection Details Summary:**

- **Host**: `dpg-d3cd1j2li9vc73df7i10-a.oregon-postgres.render.com`
- **Port**: `5432`
- **Database**: `gmcdb`
- **Username**: `gmcdb_user`
- **Password**: `Ch9zA0bxdMgqWwsuUsbfoVRts0qxbhGz`

## 🚨 **Important Notes:**

1. **Use the External Database URL** for pgAdmin connection
2. **The schema includes all necessary tables** for your GMC system
3. **Default users are created** with proper password hashes
4. **Sample data is included** for branches and products

## ✅ **After Setup:**

Your Render app should now be able to:
- Connect to the database
- Login with `admin@gmc.com` / `adminpass`
- Login with `manager_marawoy@gmc.com` / `managerpass`
- Access all inventory, sales, and forecast data
