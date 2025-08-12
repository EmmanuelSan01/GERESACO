# GERESACO - Gestor de Reservas de Salas de Conferencias

Una API REST completa para la gestión de reservas de salas de conferencias, desarrollada con FastAPI y SQLModel.

## 🚀 Características

- **Autenticación JWT**: Sistema completo de autenticación y autorización
- **Gestión de Usuarios**: Registro, login y gestión de perfiles
- **Gestión de Salas**: CRUD completo para salas con diferentes sedes y recursos
- **Sistema de Reservas**: Creación, consulta, actualización y cancelación de reservas
- **Interfaz de Consola**: CLI interactiva para gestión del sistema
- **Base de Datos MySQL**: Soporte completo con creación automática de esquema
- **Roles de Usuario**: Sistema de permisos con roles user/admin
- **Documentación Automática**: Swagger UI integrada

## 📋 Requisitos Previos

- Python 3.8+
- MySQL Server 5.7+ o 8.0+
- pip (gestor de paquetes de Python)

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd geresaco
```

### 2. Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de Base de Datos
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/geresaco

# Configuración JWT
JWT_SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
JWT_EXPIRE_MINUTES=30

# Configuración de la API
API_BASE_URL=http://localhost:8000

# Configuración de desarrollo
ENABLE_CONSOLE_INTERFACE=true
```

### 5. Configurar Base de Datos

La aplicación creará automáticamente la base de datos y las tablas al iniciarse. Asegúrate de que:

- MySQL Server esté ejecutándose
- El usuario tenga permisos para crear bases de datos
- La configuración de conexión en `.env` sea correcta

## 🏃‍♂️ Ejecución

### Desarrollo

```bash
# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload

# O usar el script principal
python app/main.py
```

La aplicación estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Interfaz de Consola**: Se inicia automáticamente en la terminal

### Producción (Heroku)

El proyecto incluye un `Procfile` configurado para despliegue en Heroku:

```bash
# El proceso web se ejecutará automáticamente
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8443}
```

## 📊 Estructura de la Base de Datos

### Tablas Principales

- **user**: Usuarios del sistema (admin/user)
- **room**: Salas de conferencias con sedes y recursos
- **reservation**: Reservas con estados (pendiente/confirmada/cancelada)

### Datos de Ejemplo

El proyecto incluye scripts SQL para poblar la base de datos:
- `app/data/docsFlowEstructura.sql`: Estructura de tablas
- `app/data/docsFlowData.sql`: Datos de ejemplo

## 🔧 Estructura del Proyecto

```
geresaco/
├── app/                          # Aplicación principal
│   ├── auth/                     # Sistema de autenticación
│   │   ├── controller.py         # Controlador de autenticación
│   │   ├── model.py             # Modelos de autenticación
│   │   └── service.py           # Servicios JWT y hash
│   ├── data/                    # Scripts de base de datos
│   ├── utils/                   # Utilidades
│   │   └── console_interface.py # Interfaz de consola
│   └── main.py                  # Punto de entrada
├── backend/                     # Core del backend
│   ├── controllers/             # Controladores de negocio
│   │   ├── users/
│   │   ├── rooms/
│   │   └── reservations/
│   ├── models/                  # Modelos SQLModel
│   │   ├── users/
│   │   ├── rooms/
│   │   └── reservations/
│   ├── routes/                  # Rutas FastAPI
│   │   ├── auth/
│   │   ├── users/
│   │   ├── rooms/
│   │   └── reservations/
│   └── core/
│       └── db.py               # Configuración de base de datos
├── .env                        # Variables de entorno
├── requirements.txt            # Dependencias Python
├── Procfile                   # Configuración Heroku
└── README.md                  # Este archivo
```

## 🔐 Autenticación

### Registro de Usuario

```bash
POST /auth/register
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "contrasena": "password123",
  "rol": "user"  // opcional, default: "user"
}
```

### Inicio de Sesión

```bash
POST /auth/login
{
  "email": "juan@example.com",
  "contrasena": "password123"
}
```

### Uso del Token

```bash
Authorization: Bearer <tu-jwt-token>
```

## 📱 Interfaz de Consola

La aplicación incluye una interfaz de consola interactiva que permite:

- ✅ Registro e inicio de sesión
- 👤 Consulta de perfil de usuario
- 📅 Gestión de reservas personales
- 🏢 Consulta de salas disponibles
- 🕒 Creación de nuevas reservas

### Funcionalidades de la Consola

1. **Usuarios No Autenticados**:
   - Registrarse en el sistema
   - Iniciar sesión

2. **Usuarios Autenticados**:
   - Ver perfil personal
   - Consultar mis reservas
   - Listar salas disponibles
   - Crear nuevas reservas
   - Cerrar sesión

## 🌐 Endpoints de la API

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener perfil actual
- `POST /auth/verify-token` - Verificar token

### Usuarios (requiere autenticación)
- `GET /users/` - Listar usuarios
- `GET /users/me` - Mi perfil
- `GET /users/{user_id}` - Usuario por ID
- `POST /users/` - Crear usuario (admin)
- `PATCH /users/{user_id}` - Actualizar usuario (admin)
- `DELETE /users/{user_id}` - Eliminar usuario (admin)

### Salas (requiere autenticación)
- `GET /rooms/` - Listar salas
- `GET /rooms/{room_id}` - Sala por ID
- `POST /rooms/` - Crear sala (admin)
- `PATCH /rooms/{room_id}` - Actualizar sala (admin)
- `DELETE /rooms/{room_id}` - Eliminar sala (admin)

### Reservas (requiere autenticación)
- `GET /reservations/` - Listar todas las reservas
- `GET /reservations/me` - Mis reservas
- `GET /reservations/{reservation_id}` - Reserva por ID
- `POST /reservations/` - Crear reserva
- `PATCH /reservations/{reservation_id}` - Actualizar reserva
- `DELETE /reservations/{reservation_id}` - Cancelar reserva
- `GET /reservations/room/{room_id}` - Reservas por sala
- `GET /reservations/date/{date}` - Reservas por fecha

## 🏢 Sedes Disponibles

- `zona_franca` - Zona Franca
- `cajasan` - Cajasán
- `bogota` - Bogotá
- `cucuta` - Cúcuta
- `guatemala` - Guatemala

## 🛠️ Recursos de Salas

- `proyector` - Proyector
- `pizarra` - Pizarra
- `televisor` - Televisor
- `WiFi` - Conexión WiFi
- `computadores` - Computadores

## 📅 Estados de Reserva

- `pendiente` - Reserva creada, pendiente de confirmación
- `confirmada` - Reserva confirmada y activa
- `cancelada` - Reserva cancelada

## 🔒 Roles de Usuario

- **user**: Usuario estándar (crear/ver/editar sus propias reservas)
- **admin**: Administrador (gestión completa del sistema)

## 🧪 Testing

### Usando la Documentación Swagger

Visita http://localhost:8000/docs para acceder a la documentación interactiva y probar los endpoints.

### Usando cURL

```bash
# Registrar usuario
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"nombre":"Test User","email":"test@example.com","contrasena":"password123"}'

# Listar salas (requiere token)
curl -X GET "http://localhost:8000/rooms/" \
     -H "Authorization: Bearer <tu-token>"
```

## 📝 Notas de Desarrollo

### Agregar Nuevas Dependencias

```bash
# Instalar nueva dependencia
pip install nombre-paquete

# Actualizar requirements.txt
pip freeze > requirements.txt
```

### Logs y Debug

- Los logs se muestran en consola durante el desarrollo
- Nivel de log configurado en `app/main.py`
- Información detallada de autenticación en logs

### Base de Datos

- La aplicación crea automáticamente la base de datos si no existe
- Las tablas se crean automáticamente usando SQLModel
- Soporte para migraciones manuales mediante scripts SQL

## 🚨 Consideraciones de Seguridad

- ⚠️ **Cambiar JWT_SECRET_KEY en producción**
- 🔐 Las contraseñas se almacenan hasheadas con bcrypt
- 🛡️ Validación de tokens en todos los endpoints protegidos
- 📧 Validación de emails únicos
- ⏰ Tokens con expiración configurable

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades:
1. Crear un issue en el repositorio
2. Incluir logs relevantes
3. Describir los pasos para reproducir el problema

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

**¡GERESACO - Simplificando la gestión de salas de conferencias!** 🎯
