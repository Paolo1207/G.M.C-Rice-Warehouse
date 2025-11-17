-- Migration script to update unique constraint for batch_code support
-- Run this in pgAdmin connected to your Render PostgreSQL database

-- Step 1: Drop the old unique constraint if it exists (check common names)
DO $$
BEGIN
    -- Try to drop constraint if it exists with old name
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_branch_product' 
        AND conrelid = 'inventory_items'::regclass
    ) THEN
        ALTER TABLE inventory_items DROP CONSTRAINT uq_branch_product;
        RAISE NOTICE 'Dropped old constraint: uq_branch_product';
    END IF;
END $$;

-- Step 2: Drop the new constraint if it already exists (in case of re-run)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'uq_branch_product_batch' 
        AND conrelid = 'inventory_items'::regclass
    ) THEN
        ALTER TABLE inventory_items DROP CONSTRAINT uq_branch_product_batch;
        RAISE NOTICE 'Dropped existing constraint: uq_branch_product_batch';
    END IF;
END $$;

-- Step 3: Add the new unique constraint that includes batch_code
ALTER TABLE inventory_items 
ADD CONSTRAINT uq_branch_product_batch 
UNIQUE (branch_id, product_id, batch_code);

-- Verification: Check that the constraint was created
SELECT 
    conname as constraint_name,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'inventory_items'::regclass 
AND conname = 'uq_branch_product_batch';

