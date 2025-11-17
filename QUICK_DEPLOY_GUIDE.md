# 🚀 Quick Deployment Guide - G.M.C Rice Warehouse

## Deploy to Render.com (Recommended)

### Step 1: Push Your Code to GitHub

Make sure all your changes are committed and pushed to your repository:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up for a free account (or sign in)
3. Connect your GitHub account

### Step 3: Deploy Using render.yaml (Automated)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repository**: `Paolo1207/G.M.C-Rice-Warehouse`
4. **Render will automatically detect** `render.yaml` and configure everything
5. **Click "Apply"** to deploy

The `render.yaml` file will:
- ✅ Create a PostgreSQL database
- ✅ Create a web service
- ✅ Set up environment variables
- ✅ Link the database to the web service

### Alternative: Manual Deployment

If you prefer manual setup:

#### A. Create PostgreSQL Database

1. **Click "New +"** → **"PostgreSQL"**
2. **Configure:**
   - **Name**: `gmc-database`
   - **Database Name**: `gmc_warehouse`
   - **User**: `gmc_user`
   - **Plan**: `Free`
3. **Click "Create Database"**
4. **Copy the "Internal Database URL"** (you'll need this)

#### B. Create Web Service

1. **Click "New +"** → **"Web Service"**
2. **Connect your GitHub repository**: `Paolo1207/G.M.C-Rice-Warehouse`
3. **Configure:**
   - **Name**: `gmc-rice-warehouse`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free`
4. **Add Environment Variables:**
   - `FLASK_ENV` = `production`
   - `FLASK_DEBUG` = `false`
   - `SECRET_KEY` = (generate a strong random key)
   - `DATABASE_URL` = (paste the Internal Database URL from step A)
5. **Click "Create Web Service"**

### Step 4: Initialize Database

After deployment, you need to create the database tables:

1. **Go to your Web Service** in Render Dashboard
2. **Click "Shell"** tab (or use "Manual Deploy" → "Run Shell")
3. **Run these commands:**

```bash
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created!')"
```

### Step 5: Seed Initial Data (Optional)

If you want to populate the database with initial data:

1. **In the Render Shell**, run:
```bash
cd backend
python seed_production_data.py
```

Or manually create users:

```python
# In Render Shell
cd backend
python
>>> from app import app, db
>>> from models import User, Branch
>>> app.app_context().push()

# Create branches
>>> branches = ["Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"]
>>> for name in branches:
...     if not Branch.query.filter_by(name=name).first():
...         db.session.add(Branch(name=name, status="operational"))
>>> db.session.commit()

# Create admin user (you'll need to hash the password properly)
>>> from werkzeug.security import generate_password_hash
>>> admin = User(
...     email="admin@gmc.com",
...     password_hash=generate_password_hash("admin123"),
...     role="admin",
...     branch_id=None
... )
>>> db.session.add(admin)
>>> db.session.commit()
```

### Step 6: Access Your Application

Once deployed, your app will be available at:
- **URL**: `https://gmc-rice-warehouse.onrender.com` (or your custom name)
- **Admin Login**: `/admin-login`
- **Manager Login**: `/manager-login`

### Step 7: Verify Deployment

1. **Check the logs** in Render Dashboard for any errors
2. **Visit your app URL** and test the login pages
3. **Test the database connection** by logging in

## 🔧 Troubleshooting

### Common Issues:

1. **"Module not found" errors:**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version (should be 3.x)

2. **Database connection errors:**
   - Verify `DATABASE_URL` environment variable is set
   - Check that PostgreSQL service is running
   - Ensure the database URL format is correct

3. **Static files not loading:**
   - Check file paths in templates
   - Verify static files are in correct directories

4. **Port binding errors:**
   - The `$PORT` environment variable is automatically set by Render
   - Make sure your start command uses `$PORT`

### Debug Commands:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test database connection
python -c "from app import app, db; app.app_context().push(); print('DB:', db.engine.url)"
```

## 📊 Monitoring

Render provides:
- **Logs**: Real-time application logs in Dashboard
- **Metrics**: CPU, memory, response times
- **Health Checks**: Automatic uptime monitoring

## 🔒 Security Checklist

Before going live:
- [ ] Change default admin password
- [ ] Generate a strong `SECRET_KEY`
- [ ] Review user authentication
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up proper session management
- [ ] Add rate limiting for API endpoints

## 🎯 Next Steps

1. **Set up custom domain** (optional)
2. **Configure automatic deployments** (already done via GitHub)
3. **Set up monitoring and alerts**
4. **Implement backup strategies**
5. **Add production logging**
6. **Set up error tracking** (Sentry, etc.)

## 📝 Notes

- **Free tier limitations**: Render free tier spins down after 15 minutes of inactivity
- **First load**: First request after spin-down may take 30-60 seconds
- **Database**: PostgreSQL is persistent, but free tier has limited resources
- **Upgrade**: Consider paid plans ($7+/month) for production use

---

**Your G.M.C Rice Warehouse is now deployed!** 🎉

For more details, see `DEPLOYMENT.md` and `RENDER_DEPLOYMENT_FIX.md`

