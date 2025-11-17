# 🚨 Render Deployment Fix - Database Connection Issue

## ❌ **Current Problem:**
The Render deployment is failing because the PostgreSQL database isn't properly linked to the web service. The error shows:
```
connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

## ✅ **Solution Steps:**

### **Step 1: Create PostgreSQL Database in Render Dashboard**

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"PostgreSQL"**
3. **Configure Database:**
   - **Name**: `gmc-database`
   - **Database Name**: `gmc_warehouse`
   - **User**: `gmc_user`
   - **Plan**: `Free`
4. **Click "Create Database"**

### **Step 2: Link Database to Web Service**

1. **Go to your Web Service** (gmc-rice-warehouse)
2. **Click "Environment"** tab
3. **Add Environment Variable:**
   - **Key**: `DATABASE_URL`
   - **Value**: Copy the **"External Database URL"** from your PostgreSQL service
4. **Click "Save Changes"**

### **Step 3: Redeploy the Application**

1. **Go to your Web Service**
2. **Click "Manual Deploy"** → **"Deploy latest commit"**
3. **Wait for deployment to complete**

### **Step 4: Seed the Database (Optional)**

If you want to populate the database with sample data:

1. **Go to your PostgreSQL service**
2. **Click "Connect"** → **"External Connection"**
3. **Use the connection details to run the seed script**

## 🔧 **Alternative: Use Environment Variables**

If the database linking doesn't work, you can manually set the DATABASE_URL:

1. **Get your database connection string** from the PostgreSQL service
2. **Add it as an environment variable** in your web service
3. **Redeploy**

## 📋 **Expected Database URL Format:**
```
postgresql://gmc_user:password@hostname:5432/gmc_warehouse
```

## 🎯 **Verification:**
After fixing, your application should:
- ✅ Connect to the PostgreSQL database
- ✅ Show "Using production database" in logs
- ✅ Load successfully without connection errors

## 🆘 **If Still Having Issues:**
1. Check that the database service is running
2. Verify the connection string is correct
3. Ensure the web service has the DATABASE_URL environment variable
4. Check Render's status page for any service outages
