# Lusha Enrich API

API para enriquecer perfiles de LinkedIn usando la API de Lusha.

## Características

- Enriquecimiento de un solo perfil de LinkedIn
- Procesamiento batch de múltiples URLs
- Enriquecimiento masivo desde Excel
- Configuración mediante variables de entorno

## Requisitos

- Python 3.8+
- API Key de Lusha

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/PyloomNG/FastApi-local-lusha.git
   ```
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   ```
3. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Iniciar el servidor

```bash
python run.py
```

O directamente con uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints

#### Enriquecer un solo perfil

```bash
POST /enrich
```

Body:
```json
{
  "linkedin_url": "https://www.linkedin.com/in/nombre-usuario",
  "reveal_emails": true,
  "reveal_phones": true,
  "partial_profile": true
}
```

#### Enriquecer múltiples URLs

```bash
POST /enrich/batch
```

Body:
```json
{
  "urls": [
    "https://www.linkedin.com/in/usuario1",
    "https://www.linkedin.com/in/usuario2"
  ]
}
```

#### Enriquecer desde Excel

```bash
POST /bulk/enrich
```

El archivo Excel debe estar en `data/input.xlsx` con una columna `profileUrl` conteniendo las URLs de LinkedIn.

El resultado se guardará en `data/enriched_output.xlsx` con las siguientes columnas adicionales:
- Email
- Phone
- First Name
- Last Name
- Company
- Job Title
- Location
- Country

## Estructura del Proyecto

```
FastApi-local-Lusha/
├── app/
│   ├── config.py          # Configuración
│   ├── models/
│   │   └── lusha_models.py
│   ├── routes/
│   │   ├── base.py
│   │   ├── enrich.py
│   │   └── bulk.py
│   └── services/
│       ├── lusha_service.py
│       └── bulk_service.py
├── data/
│   └── input.xlsx         # Archivo de entrada
├── main.py                # Aplicación FastAPI
├── run.py                 # Script de ejecución
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Licencia

MIT
