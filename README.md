# Proyecto de Automatización de Pruebas - Strapi CMS

Este proyecto contiene scripts de automatización de pruebas (E2E) para el panel administrativo de **Strapi CMS**.
Está desarrollado en **Python** utilizando **Selenium WebDriver** bajo el patrón de diseño **Page Object Model (POM)** para garantizar escalabilidad y mantenimiento.

## Características
* **Lenguaje:** Python 3.x
* **Framework:** Selenium WebDriver + Unittest
* **Patrón de Diseño:** Page Object Model (POM)
* **Configuración:** Variables de entorno (`.env`)
* **Reportes:** Capturas de pantalla automáticas en cada paso crítico.
* **Validaciones:** Asserts, esperas explícitas y manejo de errores.

## Prerrequisitos

Asegúrate de tener instalado lo siguiente antes de comenzar:
1.  **Python 3.10+**: [Descargar aquí](https://www.python.org/downloads/)
2.  **Google Chrome**: Navegador actualizado.
3.  **Strapi**: Debe estar ejecutándose en local (`npm run develop`) en `http://localhost:1337`.

---

## Instalación y Configuración del Entorno

Sigue estos pasos para aislar las dependencias del proyecto utilizando un entorno virtual.

### 1. Clonar o descargar el proyecto
Sitúate en la carpeta del proyecto desde tu terminal:
```bash
cd ruta/a/tu/proyecto
```

### 2. Crear entorno virtual

```bash
# En Windows / Mac / Linux
python -m venv venv
```

### 3. Activar entonro virtual

```bash
# En Windows
.\venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
# En Windows / Mac / Linux
pip install -r requirements.txt
```
## Configuración de Variables

Crea un archivo llamado `.env` en la raíz del proyecto y agrega tus credenciales. Puedes guiarte del siguiente ejemplo:

```ini
# .env
BASE_URL=http://localhost:1337/admin
ADMIN_EMAIL=tu_usuario@strapi.com
ADMIN_PASSWORD=tu_password_segura
# El UID de la colección en Strapi (ej: api::article.article o api::category.category)
COLLECTION_TYPE=api::category.category
```

## Ejecucion de pruebas

```bash
# En Windows / Mac / Linux
python main.py
```

## Estructura del Proyecto

El proyecto sigue el patrón de diseño **Page Object Model (POM)** para separar la lógica de prueba de la interfaz de usuario:

```text
proyecto/
├── reports/
│   └── screenshots/       # Almacén de evidencias (capturas automáticas)
├── pages/                 # Paquete Page Object Model
│   ├── __init__.py
│   ├── base_page.py       # Clase Padre: Métodos comunes (esperas, clicks, inputs)
│   ├── login_page.py      # Lógica de la página de Login
│   └── content_page.py    # Lógica de creación y edición de contenido
├── .env                   # Archivo de configuración (NO compartir)
├── main.py                # Script principal (Test Case, Asserts y Ejecución)
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación
```
## Evidencias de Ejecución

El script está diseñado para capturar automáticamente el estado de la aplicación en momentos críticos. Esto sirve como prueba documental del funcionamiento del software.

### Ubicación de Archivos

Todas las capturas de pantalla se generan dinámicamente en la carpeta:
`./reports/screenshots/`

### Catálogo de Capturas Generadas
A continuación se describe qué valida cada imagen generada por el script durante la ejecución:

| Nombre del Archivo | Descripción de la Validación | Tipo de Prueba |
| :--- | :--- | :--- |
| **1_formulario_login_lleno.png** | Estado del formulario justo antes de enviar credenciales incorrectas. | Visual |
| **2_error_login.png** | Evidencia visual del mensaje de alerta "Invalid credentials". | Funcional (Negativa) |
| **3_validacion_error_campos.png** | Muestra las alertas de validación (bordes rojos/mensajes) al intentar guardar vacío. | Funcional (Validación) |
| **4_formulario_contenido_lleno.png** | Muestra los datos ingresados correctamente en el Content Manager antes de guardar. | Visual |
| **5_item_creado_exito.png** | Confirma que el registro fue guardado exitosamente (cambio de URL/Alerta). | Funcional (Positiva) |

### Logs de Consola

Además de las imágenes, la terminal mostrará el progreso de los `Asserts` en tiempo real. Un resultado exitoso se verá así:

```text
--- Iniciando Test de Login Fallido ---
Mensaje obtenido: Invalid credentials
--- Iniciando Login Correcto ---
Login Exitoso.
--- Navegando a Crear Contenido ---
--- Probando Validación de Campos Requeridos ---
--- Llenando Formulario Correctamente ---
Item creado y guardado correctamente.
.
----------------------------------------------------------------------
Ran 1 test in 12.456s

OK