# GMC Rice Warehouse - Render Deployment Guide

## 🚀 Deploy to Render

### Prerequisites
1. GitHub repository with your code
2. Render account (free tier available)
3. PostgreSQL database (Render provides this)

### Step 1: Prepare Your Repository

Make sure your repository has these files:
- `requirements.txt` ✅
- `render.yaml` ✅
- `Procfile` ✅
- `backend/app.py` (updated for production) ✅

### Step 2: Create Render Web Service

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - **Name**: `gmc-rice-warehouse`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Root Directory**: `backend`

### Step 3: Create PostgreSQL Database

1. **In Render Dashboard**: Click "New +" → "PostgreSQL"
2. **Configure database**:
   - **Name**: `gmc-database`
   - **Database Name**: `gmc_warehouse`
   - **User**: `gmc_user`
3. **Copy the connection string** (you'll need this)

### Step 4: Configure Environment Variables

In your Render web service settings, add these environment variables:

```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://gmc_user:password@hostname:5432/gmc_warehouse
```

**Note**: Render will automatically provide `DATABASE_URL` if you link the database to your web service.

### Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for deployment** (5-10 minutes)
3. **Check logs** for any errors
4. **Visit your deployed URL**

### Step 6: Initialize Database

After deployment, you need to create the database tables:

1. **SSH into your Render service** (if available)
2. **Or use Render's shell**:
   ```bash
   python -c "from app import app; from extensions import db; app.app_context().push(); db.create_all()"
   ```

### Step 7: Seed Initial Data

Run this script to create initial data:

```python
# Create this as seed_data.py
from app import app
from extensions import db
from models import Branch, Product, User

with app.app_context():
    # Create branches
    branches = ["Marawoy", "Lipa", "Malvar", "Bulacnin", "Boac", "Sta. Cruz"]
    for name in branches:
        if not Branch.query.filter_by(name=name).first():
            db.session.add(Branch(name=name, status="operational"))
    
    # Create admin user
    if not User.query.filter_by(email="admin@gmc.com").first():
        admin = User(
            email="admin@gmc.com",
            password_hash="admin123",  # Change this in production!
            role="admin",
            branch_id=None
        )
        db.session.add(admin)
    
    # Create manager users
    for i, branch_name in enumerate(branches, 1):
        email = f"{branch_name.lower().replace(' ', '').replace('.', '')}.manager@gmc.com"
        if not User.query.filter_by(email=email).first():
            manager = User(
                email=email,
                password_hash="manager123",  # Change this in production!
                role="manager",
                branch_id=i
            )
            db.session.add(manager)
    
    db.session.commit()
    print("Database seeded successfully!")
```

### Step 8: Access Your Application

1. **Admin Login**: `https://your-app-name.onrender.com/admin-login`
   - Email: `admin@gmc.com`
   - Password: `admin123`

2. **Manager Login**: `https://your-app-name.onrender.com/manager-login`
   - Email: `marawoy.manager@gmc.com`
   - Password: `manager123`

### 🔧 Troubleshooting

#### Common Issues:

1. **Database Connection Error**:
   - Check `DATABASE_URL` environment variable
   - Ensure PostgreSQL service is running

2. **Import Errors**:
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

3. **Static Files Not Loading**:
   - Check file paths in templates
   - Ensure static files are in correct directories

4. **Session Issues**:
   - Verify `SECRET_KEY` is set
   - Check session configuration

#### Debug Commands:

```bash
# Check if app starts locally
python app.py

# Test database connection
python -c "from app import app; from extensions import db; app.app_context().push(); print('DB connected:', db.engine.url)"

# Check all routes
python -c "from app import app; print([rule.rule for rule in app.url_map.iter_rules()])"
```

### 📊 Monitoring

Render provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, response times
- **Health Checks**: Automatic uptime monitoring

### 🔒 Security Considerations

1. **Change default passwords** in production
2. **Use strong SECRET_KEY**
3. **Enable HTTPS** (Render provides this automatically)
4. **Set up proper user authentication** (replace simple password check)
5. **Add rate limiting** for API endpoints
6. **Implement proper session management**

### 💰 Cost Estimation

**Render Free Tier**:
- 750 hours/month (enough for small applications)
- 512MB RAM
- Shared CPU
- PostgreSQL database included

**Render Paid Plans**:
- Starting at $7/month for dedicated resources
- Better performance and reliability
- Custom domains
- SSL certificates

### 🎯 Next Steps

1. **Set up custom domain** (optional)
2. **Configure CI/CD** for automatic deployments
3. **Set up monitoring and alerts**
4. **Implement backup strategies**
5. **Add production logging**
6. **Set up error tracking** (Sentry, etc.)

---

**Your GMC Rice Warehouse Management System is now deployed on Render!** 🎉
