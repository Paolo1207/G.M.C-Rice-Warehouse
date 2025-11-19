# Database Entity List (Corrected)

1. Branches Entity (Schema: public.branches)

| Primary Key | Attributes | Purpose |
|-------------|------------|---------|
| id | name, location, status | Stores warehouse branch details, enabling region-based operations, sales tracking, and product distribution management. |

2. User Entity (Schema: public.user)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | email, password_hash, role, branch_id | branch_id → branches.id | Manages system users with assigned roles (e.g., Admin, Manager). Ensures authenticated access and associates each user with a specific warehouse branch. |

3. Products Entity (Schema: public.products)

| Primary Key | Attributes | Purpose |
|-------------|------------|---------|
| id | name, category, barcode, sku, description | Catalogs all products managed across branches, supporting product identification, classification, and tracking. |

4. Inventory Items Entity (Schema: public.inventory_items)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | branch_id, product_id, stock_kg, unit_price, batch_code, warn_level, auto_level, margin, grn_number, updated_at | branch_id → branches.id, product_id → products.id | Central table tracking stock quantity, pricing, and replenishment thresholds for each product per branch. Enables accurate stock management. |

5. Restock Logs Entity (Schema: public.restock_logs)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | inventory_item_id, qty_kg, supplier, note, created_at, created_by | inventory_item_id → inventory_items.id | Records restocking activities with supplier information and restock quantities, ensuring traceability of inventory additions. |

6. Sales Transactions Entity (Schema: public.sales_transactions)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | branch_id, product_id, quantity_sold, unit_price, total_amount, transaction_date, customer_name, customer_contact, batch_code | branch_id → branches.id, product_id → products.id | Tracks product sales per branch for financial analysis, demand monitoring, and performance evaluation. |

7. Forecast Data Entity (Schema: public.forecast_data)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | branch_id, product_id, forecast_date, forecast_period, predicted_demand, confidence_interval_lower, confidence_interval_upper, model_type, created_at, accuracy_score | branch_id → branches.id, product_id → products.id | Stores machine learning prediction results for product demand. Supports proactive stock planning and minimizes shortages or overstocking. |

8. Export Logs Entity (Schema: public.export_logs)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | user_id, report_type, filters_json, file_type, status, created_at | user_id → user.id (nullable, no FK constraint) | Tracks export actions performed by users, including report types and filters applied, ensuring auditability of generated reports. |

9. Notifications Entity (Schema: public.notifications)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | type, branch_id, date, message, sender, status, created_at | branch_id → branches.id | Sends automated or manual alerts (e.g., low stock, sales updates) to relevant branches and users for real-time operational awareness. |

10. Email Verifications Entity (Schema: public.email_verifications)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | user_id, new_email, verification_token, created_at, expires_at, is_verified | user_id → user.id | Manages email verification during account updates, ensuring secure communication and preventing unauthorized email changes. |

11. Password Resets Entity (Schema: public.password_resets)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | user_id, reset_token, created_at, expires_at, is_used | user_id → user.id | Supports password recovery through secure token-based reset links, maintaining user account security and system integrity. |

12. Activity Logs Entity (Schema: public.activity_logs)

| Primary Key | Attributes | Relationships | Purpose |
|-------------|------------|---------------|---------|
| id | user_id, user_email, action, description, details, branch_id, created_at | user_id → user.id, branch_id → branches.id | Tracks all user actions and system events (e.g., password resets, email changes, stock operations, product edits) for comprehensive audit trails and activity monitoring. |

---

## Summary of Corrections Made:

1. **Removed duplicate "Users Entity"** - Only one User entity exists in the system
2. **Added "Activity Logs Entity"** - This entity was missing from the original list but exists in the codebase
3. **Updated Export Logs relationship** - Noted that user_id is nullable without a formal foreign key constraint
4. **Verified all attributes** - All attributes match the actual database schema



