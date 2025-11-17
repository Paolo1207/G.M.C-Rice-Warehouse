# 🚀 Quick Email Setup (2 minutes)

## **To Enable Real Email Verification:**

### **Step 1: Get Gmail App Password**
1. Go to: https://myaccount.google.com/security
2. Enable **2-Factor Authentication** (if not already enabled)
3. Go to **"App passwords"** section
4. Generate password for **"Mail"**
5. Copy the **16-character password** (no spaces)

### **Step 2: Configure Email**
1. Open `backend/email_config.py`
2. Replace these lines:
   ```python
   SENDER_EMAIL = "yourname@gmail.com"  # Your Gmail
   SENDER_PASSWORD = "your-app-password"  # Your 16-char password
   ```
3. Save the file

### **Step 3: Test**
1. Change email in Admin Settings
2. Check your Gmail inbox
3. Click verification link in email
4. See "Email Successfully Verified!" page

## **Example Configuration:**
```python
SENDER_EMAIL = "john.doe@gmail.com"
SENDER_PASSWORD = "abcd efgh ijkl mnop"  # Your app password
```

## **That's it!** 
Now users will receive real emails in their Gmail inbox! 📧✨
