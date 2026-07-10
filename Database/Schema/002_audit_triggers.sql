-- ============================================
-- HomeOS - Audit Triggers
-- Just a simple trigger to update the UpdatedDate column on any table that has it.
-- ============================================

CREATE OR REPLACE FUNCTION UpdateUpdatedDate()
RETURNS TRIGGER AS
$$
BEGIN
    NEW.UpdatedDate = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TR_Products_UpdatedDate
BEFORE UPDATE ON Products
FOR EACH ROW
EXECUTE FUNCTION UpdateUpdatedDate();