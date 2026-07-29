# 💰 All Too Accountable — Backend

API REST desarrollada con **Flask** que da soporte a [All Too Accountable](https://github.com/Soofiaa/All-Too-Accountable), una plataforma web de gestión de finanzas personales. Expone los endpoints necesarios para autenticación, transacciones, categorías, metas de ahorro, gastos recurrentes, importación de movimientos bancarios y lectura OCR de boletas.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-database-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/status-proyecto%20personal-lightgrey)

---

## 📑 Tabla de contenidos

- [Descripción general](#-descripción-general)
- [Arquitectura](#-arquitectura)
- [Modelo de datos](#-modelo-de-datos)
- [Endpoints principales](#-endpoints-principales)
- [Seguridad](#-seguridad)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación y ejecución local](#-instalación-y-ejecución-local)
- [Configuración](#-configuración)
- [Mejoras futuras](#-mejoras-futuras)
- [Autora](#-autora)

---

## 📌 Descripción general

Este backend está construido con **Flask** y **SQLAlchemy**, usando **MySQL** como motor de base de datos (con `pymysql` como driver). Su rol es exponer una API REST que centraliza toda la lógica de negocio de la aplicación: registro/autenticación de usuarios, CRUD de transacciones financieras, categorías con límites de gasto, gastos recurrentes (mensuales y programados), metas de ahorro, cálculo de promedios y estadísticas por categoría, envío de correos para recuperación de contraseña, importación de cartolas bancarias y lectura OCR de boletas.

## 🏗️ Arquitectura

El proyecto sigue el patrón de **Blueprints** de Flask: cada recurso de negocio (usuarios, transacciones, categorías, etc.) vive en su propio módulo dentro de `app/routes/`, con su modelo correspondiente en `app/models/`. La aplicación se registra y arranca desde `run.py`, que:

1. Crea la instancia de Flask.
2. Configura CORS (restringido al origen del frontend en desarrollo, `http://localhost:5173`).
3. Configura la conexión a MySQL vía SQLAlchemy.
4. Configura Flask-Mail para el envío de correos (recuperación de contraseña).
5. Registra todos los blueprints con su prefijo de ruta (`/api/...`).
6. Sirve archivos estáticos (comprobantes/boletas subidas) desde `/uploads` e `/imagenes`.

## 🗄️ Modelo de datos

| Tabla | Modelo | Descripción |
|---|---|---|
| `usuarios` | `Usuario` | Credenciales y datos básicos del usuario (contraseña hasheada con bcrypt). |
| `categorias` | `Categoria` | Categorías de ingreso/gasto, con límite mensual opcional y flag `es_general`. |
| `transacciones` | `Transaccion` | Movimientos financieros: soporta doble método de pago, cuotas con interés, importación bancaria, soft-delete (`visible`) y vínculo opcional a un gasto mensual o programado. |
| `gastos_mensuales` | `GastoMensual` | Gastos recurrentes que se repiten cada mes en un día fijo. |
| `gastos_programados` | `GastoProgramado` | Pagos únicos a una fecha futura (incluye soporte para cheques a fecha, con `dias_cheque`). |
| `metas_ahorro` | `MetaAhorro` | Metas de ahorro con monto objetivo, fecha límite y estado activo. |
| `movimientos_ahorro` | `MovimientoAhorro` | Historial de aportes/retiros al ahorro acumulado. |
| `promedios_categorias` | `PromedioCategoria` | Promedios de gasto mensual por categoría, usados para las alertas del dashboard. |
| `tokens_recuperacion` | `TokenRecuperacion` | Tokens temporales para el flujo de recuperación de contraseña. |
| `detalles_usuario` | `DetallesUsuario` (sin ORM, SQL directo) | Historial de salario del usuario a lo largo del tiempo. |

> Las tablas se crean automáticamente al iniciar la aplicación mediante `db.create_all()`; no se utiliza un sistema de migraciones (ej. Alembic/Flask-Migrate) en este proyecto.

## 🔌 Endpoints principales

Todos los endpoints (salvo `/login`) se exponen bajo el prefijo `/api`.

#### Usuarios y autenticación
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/usuarios/registro` | Registra un nuevo usuario (hashea la contraseña con bcrypt). |
| `GET` | `/api/usuarios/<id_usuario>` | Obtiene los datos básicos de un usuario. |
| `POST` | `/login` | Inicia sesión (valida correo/contraseña). |
| `POST` | `/api/recuperar_contrasena` | Envía un correo con token de recuperación. |
| `POST` | `/api/restablecer_contrasena` | Restablece la contraseña usando el token recibido. |
| `GET` | `/api/detalles_usuario` | Obtiene el salario vigente del usuario. |
| `POST` | `/api/actualizar_salario` | Registra un nuevo salario (se conserva el historial). |
| `POST` | `/api/actualizar_nombre` | Actualiza el nombre del usuario. |
| `GET` | `/api/historial_salarios/<id_usuario>` | Historial completo de salarios. |
| `PUT` | `/editar_salario/<id_detalle>` | Edita un registro de salario puntual. |

#### Transacciones
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/transacciones/<id_usuario>` | Transacciones visibles del usuario (con filtros). |
| `GET` | `/api/transacciones/<id_usuario>/todas` | Incluye también las eliminadas. |
| `POST` | `/api/transacciones` | Crea una transacción (soporta cuotas y doble pago). |
| `PUT` | `/api/transacciones/<id>` | Edita una transacción. |
| `PUT` | `/api/transacciones/<id>/eliminar` | Soft-delete (mueve a "eliminadas"). |
| `PUT` | `/api/transacciones/<id>/recuperar` | Restaura una transacción eliminada. |
| `DELETE` | `/api/transacciones/<id>/borrar_definitivo` | Elimina permanentemente. |
| `GET` | `/api/transacciones/exportar_mes_actual` | Datos del mes actual para exportar. |
| `GET` | `/api/transacciones/categorias/<id_usuario>` | Categorías disponibles para transacciones. |
| `GET` | `/api/transacciones_completas` | Vista combinada de transacciones + recurrentes generadas. |
| `POST` | `/api/transacciones/generar_mes_actual` | Genera transacciones del mes desde gastos recurrentes activos. |
| `POST` | `/api/transacciones/limpiar_duplicados` | Limpieza de duplicados generados automáticamente. |

#### Categorías
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/categorias/<id_usuario>` | Lista categorías del usuario + categorías generales. |
| `POST` | `/api/categorias/` | Crea una categoría. |
| `PUT` | `/api/categorias/<id>` | Edita una categoría. |
| `DELETE` | `/api/categorias/<id>` | Elimina una categoría. |

#### Gastos recurrentes
| Método | Ruta | Descripción |
|---|---|---|
| `GET` `POST` `PUT` `DELETE` | `/api/gastos_mensuales` | CRUD de gastos mensuales. |
| `PUT` | `/api/gastos_mensuales/desactivar/<id>` · `/reactivar/<id>` | Activa/desactiva un gasto mensual. |
| `POST` | `/api/pagos_programados` | Crea un gasto programado (pago único). |
| `GET` `PUT` `DELETE` | `/api/pagos_programados/<id>` | Consulta, edita o elimina un gasto programado. |
| `PUT` | `/api/pagos_programados/actualizar_estado_automatico/<id_usuario>` | Actualiza automáticamente el estado según la fecha. |

#### Metas de ahorro y movimientos de ahorro
| Método | Ruta | Descripción |
|---|---|---|
| `GET` `POST` `PUT` `DELETE` | `/api/metas` | CRUD de metas de ahorro. |
| `GET` `POST` | `/api/movimientos_ahorro` | Consulta y registra aportes/retiros de ahorro. |

#### Estadísticas y promedios
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/estadisticas/comparar_categorias` | Compara gasto por categoría entre dos meses. |
| `POST` | `/api/promedios/registrar_promedios/<id_usuario>` | Recalcula promedios mensuales por categoría. |
| `GET` | `/api/promedios/promedio_categoria` | Consulta promedios recientes. |

#### Importación y OCR
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/importar_movimientos` | Importa movimientos desde un archivo `.csv`/`.xlsx` (procesado con `pandas`), evitando duplicados y clasificando automáticamente en la categoría "General". |
| `POST` | `/api/leer_boleta` | Recibe una imagen (`.jpg`/`.png`), la valida con Pillow y extrae el texto con **Tesseract OCR** (`pytesseract`, idioma español). |

## 🔒 Seguridad

- Las contraseñas de usuario se almacenan **hasheadas con bcrypt** (`app/utils/seguridad.py`), nunca en texto plano.
- CORS está restringido en `run.py` al origen del frontend en desarrollo.
- Validación de formato de correo y de campos obligatorios en el login.
- Validación de extensión y estructura real del archivo en los endpoints de importación (`.csv`/`.xlsx`) y OCR (`.jpg`/`.png`), no solo por el nombre del archivo.

> ⚠️ **Nota de configuración pendiente:** actualmente la cadena de conexión a MySQL y las credenciales del correo de recuperación de contraseña están definidas directamente en `run.py`/`database.py`, en lugar de cargarse desde variables de entorno. Antes de desplegar en un entorno real o de compartir el repositorio de forma pública, se recomienda migrar estos valores a un archivo `.env` (con `python-dotenv`) y añadir dicho archivo al `.gitignore`, junto con las carpetas de contenido subido por usuarios (`imagenes_transacciones/`) y los `__pycache__/`.

## 📂 Estructura del proyecto

```
BackEnd-All-Too-Accountable/
├── app/
│   ├── models/              # Modelos SQLAlchemy (uno por entidad de negocio)
│   ├── routes/               # Blueprints de Flask, uno por recurso
│   │   └── DESCARTADOS/      # Rutas exploradas y no integradas (ej. chat con IA)
│   ├── utils/
│   │   └── seguridad.py      # Hasheo y verificación de contraseñas (bcrypt)
│   ├── extensions.py          # Instancias compartidas (SQLAlchemy, Flask-Mail)
│   └── __init__.py            # Patrón factory (create_app) — no utilizado por run.py
├── database.py                 # Configuración de conexión y sesión de base de datos
├── imagenes_transacciones/      # Boletas/comprobantes subidos por los usuarios
├── requirements.txt
└── run.py                       # Punto de entrada real de la aplicación
```

> La carpeta `app/routes/DESCARTADOS/` contiene un blueprint de chat conversacional (`chat_ia.py`) que integraba la API de OpenAI para responder preguntas sobre las finanzas del usuario ("FinAI"). Se mantiene como referencia de una funcionalidad explorada, pero no está integrada al flujo actual del backend.

## 🚀 Instalación y ejecución local

### Requisitos previos
- Python 3.11+
- MySQL Server en ejecución localmente
- Tesseract OCR instalado en el sistema (para el endpoint de lectura de boletas)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/Soofiaa/BackEnd-All-Too-Accountable.git
cd BackEnd-All-Too-Accountable

# 2. Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear la base de datos en MySQL
#    CREATE DATABASE all_too_accountable;

# 5. Ejecutar el servidor
python run.py
```

La API quedará disponible en `http://localhost:5000`.

> ⚠️ **Sobre `requirements.txt`:** el archivo actual del repositorio solo incluye Flask, flask-cors y sus dependencias internas. El proyecto además necesita `flask-sqlalchemy`, `flask-mail`, `pymysql`, `bcrypt`, `pytesseract`, `Pillow`, `pandas`, `python-dateutil` y `python-dotenv` (si se migran las credenciales a variables de entorno). Se recomienda regenerar el archivo con `pip freeze > requirements.txt` desde el entorno virtual una vez instaladas todas las dependencias, para que la instalación funcione de punta a punta.

## ⚙️ Configuración

Configuración actual (definida en `run.py` / `database.py`):

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contraseña@localhost/all_too_accountable'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
```

**Configuración recomendada** (una vez migrado a variables de entorno), crear un archivo `.env`:

```env
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/all_too_accountable
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicación
MAIL_DEFAULT_SENDER=tu_correo@gmail.com
```

Y cargarlas en `run.py` con `python-dotenv` y `os.getenv(...)` en lugar de valores fijos.

## 👩‍💻 Autora

**Sofía Menzel** — Ingeniera en Ejecución Informática (PUCV)
📍 Viña del Mar, Chile
🔗 [Portafolio](https://portafolio-web-theta-coral.vercel.app)
