# Plataforma de Gestión de Facturas

Sistema de procesamiento inteligente de facturas con extracción automática de datos usando IA.

## Tecnologías

- **Backend**: FastAPI + Python
- **Frontend**: Vue.js 3 + TypeScript
- **Base de datos**: Google Firestore
- **Almacenamiento**: Google Cloud Storage
- **IA**: OpenAI GPT-4 + Google Document AI
- **Infraestructura**: Google Cloud Run + Firebase Hosting

## Instalación de Dependencias

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Variables de Entorno

### Backend (Cloud Run)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | ID del proyecto GCP | `mi-proyecto-123` |
| `GCP_REGION` | Región de GCP | `us-central1` |
| `STORAGE_BUCKET_NAME` | Bucket para PDFs | `mi-proyecto-invoices` |
| `OPENAI_API_KEY` | Clave API de OpenAI | `sk-...` |
| `OPENAI_MODEL` | Modelo de OpenAI | `gpt-4o-mini` |
| `LLM_EXTRACTION_ENABLED` | Habilitar extracción con IA | `true` |
| `OCR_MODE` | Modo de extracción | `llm` o `auto` |
| `DOCUMENT_AI_PROJECT_ID` | Proyecto Document AI (opcional) | `mi-proyecto-123` |
| `DOCUMENT_AI_PROCESSOR_ID` | ID del procesador (opcional) | `abc123...` |
| `DOCUMENT_AI_ENABLED` | Habilitar Document AI | `false` |

**Secreto requerido:**
- `FIREBASE_SERVICE_ACCOUNT_SECRET`: Credenciales de Firebase Admin SDK

### Frontend (Firebase Hosting)

Crear archivo `frontend/.env.production`:

```bash
VITE_API_URL=https://tu-backend-url.run.app
VITE_FIREBASE_API_KEY=tu-api-key
VITE_FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=tu-proyecto-id
VITE_FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123456789:web:abc123
```

## Despliegue en GCP

### Paso 1: Configuración Inicial

```bash
# Configurar proyecto GCP
gcloud config set project TU_PROJECT_ID

# Habilitar APIs necesarias
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com
```

### Paso 2: Crear Recursos

```bash
# Crear bucket de almacenamiento
gsutil mb -l us-central1 gs://TU_PROJECT_ID-invoices

# Crear base de datos Firestore
gcloud firestore databases create --region=us-central1

# Crear secreto con credenciales de Firebase
gcloud secrets create firebase-service-account \
    --data-file=ruta/a/serviceAccountKey.json
```

### Paso 3: Desplegar Backend

```bash
cd backend

# Construir imagen Docker
gcloud builds submit --tag gcr.io/TU_PROJECT_ID/invoice-platform-backend

# Desplegar a Cloud Run
gcloud run deploy invoice-platform-backend \
  --image gcr.io/TU_PROJECT_ID/invoice-platform-backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="FIREBASE_SERVICE_ACCOUNT_SECRET=firebase-service-account:latest" \
  --set-env-vars "\
GCP_PROJECT_ID=TU_PROJECT_ID,\
GCP_REGION=us-central1,\
STORAGE_BUCKET_NAME=TU_PROJECT_ID-invoices,\
OPENAI_API_KEY=sk-tu-clave-openai,\
OPENAI_MODEL=gpt-4o-mini,\
LLM_EXTRACTION_ENABLED=true,\
OCR_MODE=llm,\
DOCUMENT_AI_ENABLED=false"
```

### Paso 4: Desplegar Frontend

```bash
cd frontend

# Crear archivo .env.production con las variables de entorno

# Construir aplicación
npm run build

# Desplegar a Firebase Hosting
firebase deploy --only hosting
```

### Paso 5: Configurar CORS

```bash
# Obtener URL del frontend
FRONTEND_URL=$(firebase hosting:channel:list | grep "live" | awk '{print $2}')

# Actualizar CORS en backend
gcloud run services update invoice-platform-backend \
  --region us-central1 \
  --update-env-vars "CORS_ORIGINS=$FRONTEND_URL,http://localhost:5173"
```

## Verificación

### Backend

```bash
# Obtener URL del backend
gcloud run services describe invoice-platform-backend \
  --region us-central1 \
  --format='value(status.url)'

# Probar endpoint de salud
curl https://tu-backend-url/health
```

### Frontend

Abrir en navegador: `https://tu-proyecto.web.app`

## Costos Estimados

- **Cloud Run**: ~$5-10/mes (uso básico)
- **Firestore**: Gratis hasta 50K lecturas/día
- **Cloud Storage**: ~$0.02/GB/mes
- **OpenAI (gpt-4o-mini)**: ~$0.0005 por factura
- **Firebase Hosting**: Gratis hasta 10GB/mes

**Total estimado**: $10-20/mes para uso moderado

## Soporte

Para más detalles técnicos, consultar:
- `SIMPLIFIED_DEPLOYMENT.md` - Guía de despliegue completa
- `LLM_QUICK_START.md` - Configuración de extracción con IA
- `backend/API_DOCUMENTATION.md` - Documentación de API

## Licencia

Propietario
