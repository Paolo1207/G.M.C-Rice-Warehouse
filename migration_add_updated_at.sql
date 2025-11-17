-- Migration: Add updated_at column to inventory_items table
-- For PostgreSQL on Render

-- Add the updated_at column with default value
ALTER TABLE inventory_items 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing records to have a timestamp (optional - sets to current time for all existing records)
UPDATE inventory_items 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- Add a comment to the column
COMMENT ON COLUMN inventory_items.updated_at IS 'Timestamp of last update to inventory item';

