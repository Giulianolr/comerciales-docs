\set ON_ERROR_STOP on
BEGIN;
INSERT INTO categories (id, store_id, name, description) VALUES ('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'Lácteos', 'Quesos y leches');
INSERT INTO categories (id, store_id, name, description) VALUES ('55555555-5555-5555-5555-555555555555', '11111111-1111-1111-1111-111111111111', 'Fiambres', 'Embutidos y salames');

INSERT INTO products (id, store_id, category_id, barcode, name, description, unit, price, stock_quantity, min_stock, is_active) VALUES 
('66666666-6666-6666-6666-666666666661', '11111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', '1001', 'Queso Mantecoso 1Kg', 'Queso mantecoso primera calidad', 'kg', 8500, 50, 10, true),
('66666666-6666-6666-6666-666666666662', '11111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444444', '1002', 'Queso Gouda 1Kg', 'Queso de importación', 'kg', 12500, 20, 5, true),
('66666666-6666-6666-6666-666666666663', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', '2001', 'Salame Milán 1Kg', 'Salame tipo milán', 'kg', 14000, 30, 5, true),
('66666666-6666-6666-6666-666666666664', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', '2002', 'Jamón Pierna 1Kg', 'Jamón cocido de pierna', 'kg', 9900, 40, 10, true),
('66666666-6666-6666-6666-666666666665', '11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', '2003', 'Mortadela 1Kg', 'Mortadela con pistacho', 'kg', 6500, 25, 5, true);
COMMIT;
