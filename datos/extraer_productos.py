#!/usr/bin/env python3
"""
Extrae productos del backup MySQL de Doña Esperanza
y genera INSERT SQL compatible con nuestra BD PostgreSQL.
"""
import re
import sys

BACKUP = "/Users/giuliano.larosa/Documents/Proyecto locales comerciales/datos/donaesperanza_20260305_1717.sql"
STORE_ID = "a0000000-0000-0000-0000-000000000001"
CATEGORY_ID = "c0000000-0000-0000-0000-000000000001"

def limpiar(s):
    return s.strip().strip("'").replace("''", "'").replace("\\", "")

def leer_inserts(sql_text, tabla):
    """Extrae todas las filas de INSERT para una tabla dada."""
    pattern = rf"insert\s+into\s+`{tabla}`[^;]+?values\s*([\s\S]+?)(?:;|\Z)"
    rows = []
    for match in re.finditer(pattern, sql_text, re.IGNORECASE):
        bloque = match.group(1)
        # Extraer tuplas individuales
        for tupla in re.finditer(r'\(([^)]+)\)', bloque):
            vals = [v.strip() for v in tupla.group(1).split(',')]
            rows.append(vals)
    return rows

print("Leyendo backup (228MB)...", file=sys.stderr)
with open(BACKUP, encoding='latin-1', errors='replace') as f:
    sql = f.read()
print("Cargado.", file=sys.stderr)

# ── Parsear codigosdebarra ────────────────────────────────────────────────────
# (COD_EMPRESA, COD_ART, COD_BARRA, ...)
print("Parseando codigosdebarra...", file=sys.stderr)
barcode_map = {}  # COD_ART -> COD_BARRA
for row in leer_inserts(sql, 'codigosdebarra'):
    if len(row) >= 3:
        cod_art = limpiar(row[1])
        cod_barra = limpiar(row[2]).strip()
        # Ignorar barcodes vacíos o solo espacios
        if cod_barra and len(cod_barra.strip()) >= 4:
            barcode_map[cod_art] = cod_barra.strip()

print(f"  {len(barcode_map)} barcodes encontrados", file=sys.stderr)

# ── Parsear precios (COD_LISTA=1 = lista pública) ─────────────────────────────
print("Parseando precios...", file=sys.stderr)
precios_map = {}  # COD_ART -> precio
for row in leer_inserts(sql, 'precios'):
    if len(row) >= 4:
        cod_lista = limpiar(row[1])
        cod_art = limpiar(row[2])
        precio = limpiar(row[3])
        if cod_lista == '1':  # Lista 1 = precio público
            try:
                precios_map[cod_art] = round(float(precio))
            except ValueError:
                pass

print(f"  {len(precios_map)} precios encontrados", file=sys.stderr)

# ── Parsear productos ─────────────────────────────────────────────────────────
# COD_ART=1, descripcion=8, SIMBOLO_STOCK=19, ESTADO=5, STOCK=12
print("Parseando productos...", file=sys.stderr)

# Buscar todos los inserts de productos
prod_pattern = r"insert\s+into\s+`productos`.*?values\s*([\s\S]+?)(?=\n\n|\Z)"
productos = []

# Extraer directamente con regex línea por línea
lines_pattern = re.compile(
    r"\((\d+),(\d+),(\d+),(\d+),(\d+),(\d+),[^,]*,[^,]*,'([^']*)'",
)

for m in re.finditer(r"insert\s+into\s+`productos`[^;]+;", sql, re.IGNORECASE | re.DOTALL):
    bloque = m.group(0)
    for fila in re.finditer(r"\((\d+),(\d+),\d+,\d+,\d+,(\d+),[^,]+,[^,]+,'([^']{1,60})'", bloque):
        cod_empresa = fila.group(1)
        cod_art     = fila.group(2)
        estado      = fila.group(3)
        descripcion = fila.group(4).strip()
        if estado == '1' and cod_art in barcode_map:
            productos.append((cod_art, descripcion))

print(f"  {len(productos)} productos activos con barcode", file=sys.stderr)

# ── Detectar unidad (kg vs unit) ─────────────────────────────────────────────
KG_KEYWORDS = ['kilo', ' kg', 'granel', '/kg', 'x kg', 'tomate', 'cebolla', 'papa',
               'zapallo', 'zanahoria', 'manzana', 'platano', 'palta', 'limón', 'limon',
               'naranja', 'lechuga', 'apio', 'beterraga', 'betarraga', 'pepino',
               'choclo', 'arveja', 'poroto', 'lenteja', 'garbanzo']

def inferir_unidad(nombre):
    nom = nombre.lower()
    return 'kg' if any(k in nom for k in KG_KEYWORDS) else 'unit'

# ── Generar SQL ───────────────────────────────────────────────────────────────
print("\n-- Generado desde donaesperanza_20260305_1717.sql", file=sys.stdout)
print("-- Productos reales del local Doña Esperanza", file=sys.stdout)
print("ALTER TABLE products DISABLE ROW LEVEL SECURITY;", file=sys.stdout)
print("BEGIN;", file=sys.stdout)

count = 0
vistos_barcode = set()

for cod_art, descripcion in productos:
    barcode = barcode_map.get(cod_art, '').strip()
    precio  = precios_map.get(cod_art, 0)

    if not barcode or barcode in vistos_barcode:
        continue
    if precio <= 0 or precio > 999999:
        continue
    if len(descripcion) < 2:
        continue

    vistos_barcode.add(barcode)
    unidad = inferir_unidad(descripcion)
    desc_clean = descripcion.replace("'", "''")
    precio_int = int(precio)

    print(
        f"INSERT INTO products (id, store_id, barcode, name, description, category_id, unit, price, stock_quantity, min_stock) "
        f"VALUES (gen_random_uuid(), '{STORE_ID}', '{barcode}', '{desc_clean}', '', '{CATEGORY_ID}', '{unidad}', {precio_int}, 100, 10) "
        f"ON CONFLICT DO NOTHING;",
        file=sys.stdout
    )
    count += 1

print("COMMIT;", file=sys.stdout)
print("ALTER TABLE products ENABLE ROW LEVEL SECURITY;", file=sys.stdout)
print(f"\n-- Total: {count} productos", file=sys.stdout)
print(f"Total a insertar: {count} productos", file=sys.stderr)
