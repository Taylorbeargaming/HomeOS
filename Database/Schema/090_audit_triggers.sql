-- ============================================
-- HomeOS - Timestamp and completion triggers
-- Run after all tables have been created.
-- ============================================

CREATE OR REPLACE FUNCTION set_updateddate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    NEW.updateddate = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_units_updateddate
BEFORE UPDATE ON units
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_products_updateddate
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_shoppinglist_updateddate
BEFORE UPDATE ON shoppinglist
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_shoppinglistitem_updateddate
BEFORE UPDATE ON shoppinglistitem
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_inventory_updateddate
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE TRIGGER tr_recipe_updateddate
BEFORE UPDATE ON recipe
FOR EACH ROW
EXECUTE FUNCTION set_updateddate();

CREATE OR REPLACE FUNCTION set_shoppinglist_completeddate()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.completed THEN
        IF TG_OP = 'INSERT' THEN
            NEW.completeddate = COALESCE(NEW.completeddate, CURRENT_TIMESTAMP);
        ELSE
            NEW.completeddate = COALESCE(NEW.completeddate, OLD.completeddate, CURRENT_TIMESTAMP);
        END IF;
    ELSE
        NEW.completeddate = NULL;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER tr_shoppinglist_completeddate
BEFORE INSERT OR UPDATE OF completed, completeddate ON shoppinglist
FOR EACH ROW
EXECUTE FUNCTION set_shoppinglist_completeddate();
