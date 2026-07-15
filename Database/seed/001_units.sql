-- ============================================
-- HomeOS - Initial units
-- Safe to run more than once.
-- ============================================

INSERT INTO units (unitname, abbreviation)
VALUES
    ('Each', 'ea'),
    ('Gram', 'g'),
    ('Kilogram', 'kg'),
    ('Millilitre', 'ml'),
    ('Litre', 'L')
ON CONFLICT (unitname)
DO UPDATE SET
    abbreviation = EXCLUDED.abbreviation,
    isactive = TRUE;
