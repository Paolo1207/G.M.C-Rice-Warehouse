# 📧 GMC Email Verification Setup

## 🎯 **Goal:**
Enable real email verification so users receive actual emails in their Gmail inbox when changing their email address.

## 🚀 **Quick Setup (5 minutes):**

### **Step 1: Configure Gmail App Password**
1. **Go to Google Account Security:**
   - Visit: https://myaccount.google.com/security
   - Sign in with your Gmail account

2. **Enable 2-Factor Authentication:**
   - Click "2-Step Verification"
   - Follow the setup process

3. **Generate App Password:**
   - Go to "App passwords" section
   - Select "Mail" as the app
   - Copy the 16-character password (no spaces)

### **Step 2: Run Email Setup Script**
```bash
cd backend
python setup_email.py
```

**Enter your details:**
- Gmail address: `yourname@gmail.com`
- App Password: `your-16-character-password`

### **Step 3: Test Email Verification**
1. **Go to Admin Settings**
2. **Change email** from `admin@gmc.com` to `your-new-email@gmail.com`
3. **Check Gmail inbox** for verification email
4. **Click verification link** in the email
5. **See "Email Successfully Verified!"** page

## ✅ **What Happens After Setup:**

### **Before Setup (Demo Mode):**
- User changes email → Shows demo modal with manual link
- User clicks demo link → Email gets updated

### **After Setup (Real Email):**
- User changes email → **Real email sent to Gmail**
- User checks Gmail inbox → **Finds verification email**
- User clicks link in email → **"Email Successfully Verified!" page**
- Email gets updated in database

## 🔧 **Manual Configuration (Alternative):**

Create `.env` file in `backend/` folder:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=yourname@gmail.com
SENDER_PASSWORD=your-16-character-app-password
BASE_URL=http://localhost:5000
```

## 🧪 **Test Email Configuration:**
```bash
cd backend
python setup_email.py test
```

## 📧 **Email Templates:**
- **Verification Email:** Sent to new email address
- **Change Notification:** Sent to old email address
- **Professional GMC branding** with HTML formatting

## 🎉 **Result:**
Users will receive beautiful, professional emails in their Gmail inbox with verification links that work exactly like real email verification systems!
