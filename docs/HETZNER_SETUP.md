# HETZNER + DOMINIO SETUP
## Guía paso a paso para crear la infraestructura

**Versión:** 1.0  
**Para:** Allan (Backend/DevOps)  
**Tiempo estimado:** 30-45 minutos  
**Costo total:** $3.60 USD/mes (VPS) + $2 USD/mes (dominio) = $5.60 USD/mes base

---

## PASO 1: CREAR CUENTA HETZNER CLOUD (5 min)

### 1.1 Ir a https://www.hetzner.cloud
1. Click en "Sign Up"
2. Ingresar email (usa tu email personal o compartido del proyecto)
3. Crear contraseña segura (guarda en 1Password o similar)
4. Aceptar términos
5. Verificar email (te enviarán link)

### 1.2 Configurar billing
1. En dashboard → "Billing"
2. Agregar tarjeta de crédito/débito
   - ⚠️ Te cobrarán ~$5 de verifi cación (después devuelven)
3. Confirmar

---

## PASO 2: CREAR VPS HETZNER CX31 (10 min)

### 2.1 Crear servidor
1. Dashboard → "Servers" → "Create Server"
2. **Location:** Frankfurt, Alemania (más cercano a Chile que Miami)
3. **OS Image:** Ubuntu 22.04 LTS (recomendado)
4. **Server Type:** CX31
   - 2 vCPU
   - 4 GB RAM
   - 40 GB SSD
   - Costo: €3.29/mes (~$3.60 USD)
5. Click "Create & Buy Now"

### 2.2 SSH Key Setup (IMPORTANTE)
Tienes 2 opciones:

**OPCIÓN A: Generar key en Hetzner (más fácil)**
1. En "SSH Keys" → "Add SSH Key"
2. Click "Generate in browser"
3. Hetzner genera par público/privado
4. Descarga el archivo `.pem` → **guarda en lugar seguro**
5. Permiso: `chmod 600 nombre-key.pem`

**OPCIÓN B: Usar tu key existente (si tienes)**
1. Copiar tu `~/.ssh/id_rsa.pub`
2. En Hetzner → "SSH Keys" → "Add SSH Key"
3. Pegar contenido

### 2.3 Asignar SSH Key al servidor
1. Volver a "Create Server"
2. En "SSH Keys" → seleccionar la que acabas de crear
3. Click "Create Server"

**⏳ ESPERAR:** El servidor tarda ~2 minutos en estar listo. Hetzner mostrará una IP pública.

### 2.4 Guardar la IP pública
```
Ejemplo: 1.2.3.4

Esta IP es importante para:
- SSH access
- DNS del dominio
- Recordarla (escribe en contraseña)
```

---

## PASO 3: REGISTRAR DOMINIO .CL (15 min)

Tienes 2 opciones:

### OPCIÓN A: NIC Chile (Oficial, recomendado)
**Sitio:** https://nic.cl/

1. Click "Registrar un dominio"
2. Buscar `tuempresa.cl` (disponibilidad)
3. Seleccionar "Deseo registrar este dominio"
4. Carrito → proceder
5. **Datos del titular:**
   - Nombre: Tu nombre legal o empresa
   - RUT: 11.111.111-1 (o RUT empresa)
   - Email: tumail@ejemplo.com
   - Teléfono: +56912345678
6. **Servidores DNS (dejarás vacío por ahora)**
   - Lo configuraremos después con Cloudflare
7. Pagar ~$2-3 USD (tarjeta de crédito)

**⏳ ESPERAR:** Activación puede tomar 24-48 horas

### OPCIÓN B: Namecheap o similar (más rápido)
**Sitio:** https://www.namecheap.com
1. Buscar dominio `.cl`
2. Agregar al carrito
3. Completar datos de titular
4. Pagar

**Nota:** Para ambas, después configurarás DNS con Cloudflare (paso 5)

### 3.1 Guardar credenciales del dominio
```
Dominio: tuempresa.cl
Titular: Tu Nombre
RUT: 11.111.111-1
Email registrador: tumail@ejemplo.com
Contraseña registrador: [guarda seguro]
```

---

## PASO 4: CONFIGURAR CLOUDFLARE (SSL gratis + DNS) (10 min)

### 4.1 Crear cuenta Cloudflare
**Sitio:** https://www.cloudflare.com

1. Click "Sign Up"
2. Email + contraseña
3. Verificar email

### 4.2 Agregar dominio a Cloudflare
1. Dashboard → "Add a site"
2. Ingresar tu dominio: `tuempresa.cl`
3. Cloudflare detectará registros DNS existentes
4. Click "Continue"

### 4.3 Cambiar Nameservers en NIC Chile
Cloudflare te dará 2 nameservers:
```
Ejemplo:
- noah.ns.cloudflare.com
- opal.ns.cloudflare.com
```

**Volver a NIC Chile:**
1. Iniciar sesión en tu cuenta NIC
2. "Mis dominios" → tu dominio
3. "Editar DNS"
4. Eliminar servidores existentes
5. Agregar los 2 de Cloudflare
6. Guardar

**⏳ ESPERAR:** Propagación DNS puede tardar 24-48 horas (normalmente 15-30 min)

### 4.4 Configurar registros DNS en Cloudflare
1. En Cloudflare → Dashboard → tu dominio → "DNS"
2. Agregar estos registros:

```
Tipo    Nombre              Valor               TTL    Proxy
─────────────────────────────────────────────────────────────
A       tuempresa.cl        1.2.3.4             Auto   ☁️ Proxied
A       www                 1.2.3.4             Auto   ☁️ Proxied
CNAME   api                 tuempresa.cl        Auto   ☁️ Proxied
```

Donde `1.2.3.4` es la IP de tu VPS Hetzner.

### 4.5 Habilitar SSL/TLS (gratis)
1. En Cloudflare → "SSL/TLS" → "Overview"
2. "Your SSL/TLS encryption mode" → "Full"
3. "Edge Certificates" → "Always Use HTTPS" = ON

✅ **Listo:** Ahora tienes HTTPS gratis via Cloudflare

---

## PASO 5: VERIFICAR ACCESO VPS (5 min)

### 5.1 SSH al servidor
```bash
ssh -i /ruta/a/tu/key.pem root@1.2.3.4
```

Si la key está en `~/.ssh/`, puedes:
```bash
ssh -i ~/.ssh/hetzner-key.pem root@1.2.3.4
```

Deberías ver:
```
Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.10.0-21-generic x86_64)
```

### 5.2 Cambiar contraseña root
```bash
passwd
# ingresa nueva contraseña
```

### 5.3 Verificar conectividad
```bash
# Mostrar IP del servidor
ip addr show

# Verificar internet
ping 8.8.8.8

# Salir
exit
```

---

## PASO 6: LISTA DE DATOS PARA SIGUIENTE FASE (Guardar!)

```
═══════════════════════════════════════════════════════
CREDENCIALES PROYECTO COMERCIALES
═══════════════════════════════════════════════════════

VPS HETZNER
───────────
IP Pública:               1.2.3.4
Usuario:                  root
SSH Key:                  /path/to/key.pem
Region:                   Frankfurt
Specs:                    CX31 (2vCPU, 4GB RAM)

DOMINIO
───────
Dominio:                  tuempresa.cl
Registrador:              NIC Chile / Namecheap
Email Titular:            tumail@ejemplo.com
Nameservers:              Cloudflare

CLOUDFLARE
──────────
Email:                    tumail@ejemplo.com
Contraseña:               [guarda en 1Password]
SSL:                      Full (HTTPS)
DNS Proxy:                Enabled

PRESUPUESTO MENSUAL
───────────────────
VPS Hetzner CX31:         $3.60 USD
Dominio .cl:              $2.00 USD
Cloudflare:               $0.00 USD (free tier)
SII (Bsale):              $28.00 USD
─────────────────────────────────────
TOTAL:                    $33.60 USD/mes
```

---

## ⚠️ TROUBLESHOOTING

### "SSH connection refused"
- Verificar que IP es correcta: `ssh root@[IP]`
- Esperar 2-3 minutos después de crear servidor
- Verificar key permisos: `chmod 600 key.pem`

### "DNS no resuelve tuempresa.cl"
- Cloudflare tarda 24-48h en propagar
- Mientras tanto, accede por IP: `http://1.2.3.4`
- Verificar registros en Cloudflare DNS

### "SSL certificate error"
- Esperar a que Cloudflare genere el cert (~5 min)
- Forzar refresh: Ctrl+Shift+R en navegador
- Verificar SSL está "Full" en Cloudflare

---

## ✅ CHECKLIST COMPLETADO

- [ ] Cuenta Hetzner Cloud creada
- [ ] VPS CX31 creado (IP anotada)
- [ ] SSH key generada y guardada
- [ ] Dominio .cl registrado
- [ ] Nameservers apuntando a Cloudflare
- [ ] Registros DNS creados
- [ ] SSL/TLS activado en Cloudflare
- [ ] SSH access verificado
- [ ] IP, usuario, credenciales guardadas

**Próximo paso:** VPS_SETUP.md (Allan configura el servidor)

---

**Duración total:** ~45 min (incluye esperas de propagación DNS)  
**Costo:** $5.60 USD/mes base  
**Próximo:** Ver `docs/VPS_SETUP.md` para configurar servicios
