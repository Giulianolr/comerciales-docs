\set ON_ERROR_STOP on
BEGIN;
ALTER TABLE stores DISABLE TRIGGER ALL;
ALTER TABLE users DISABLE TRIGGER ALL;
INSERT INTO stores (id, name, owner_id, address, is_active) VALUES ('11111111-1111-1111-1111-111111111111', 'Sucursal Central', '22222222-2222-2222-2222-222222222222', 'Av Siempre Viva 123', true);
INSERT INTO users (id, store_id, name, email, pin, password_hash, role, is_active) VALUES ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Admin', 'admin@comerciales.cl', '0000', '$2b$12$kvl6ZXvT9cbZlVBiw87N9O7godJOBftP4r0V73f47SRv9vxWVoPjG', 'ADMIN', true);
INSERT INTO users (id, store_id, name, email, pin, password_hash, role, is_active) VALUES ('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'Cajero Uno', 'cajero@omsai.cl', '1234', '$2b$12$eS4Y5YC3h/xBXTSKDwnaaObgtbAnq/nWLvY9ny88t6I2.lKI8pGNy', 'CAJERO', true);
INSERT INTO users (id, store_id, name, email, pin, password_hash, role, is_active) VALUES ('44444444-4444-4444-4444-444444444444', '11111111-1111-1111-1111-111111111111', 'Cajero Prueba', 'caja@comerciales.cl', '0001', '$2y$12$Qbnl1K9BcSuYEBSACES81.lrwZWwLrH9smqLlwHGXqKQyceo71ZMW', 'CAJERO', true);
ALTER TABLE stores ENABLE TRIGGER ALL;
ALTER TABLE users ENABLE TRIGGER ALL;
COMMIT;
