# Deployment Guide

## Backend (Google Cloud Run)

### First-Time Setup

```bash
# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

# Deploy with env vars
cd backend
gcloud run deploy playroom-diet-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=xxx,SUPABASE_SECRET_KEY=xxx,AIRFLOW_HOST=xxx,AIRFLOW_STATIC_TOKEN=xxx"
```

### Redeploy

```bash
cd backend
gcloud run deploy playroom-diet-api --source . --region us-central1
```

Existing environment variables are preserved automatically.

### Managing Environment Variables

```bash
# View current env vars
gcloud run services describe playroom-diet-api --region us-central1 --format='yaml(spec.template.spec.containers[0].env)'

# Update specific vars (no rebuild)
gcloud run services update playroom-diet-api --region us-central1 \
  --update-env-vars "DAILY_SCAN_LIMIT=50"

# Add new var
gcloud run services update playroom-diet-api --region us-central1 \
  --set-env-vars "NEW_VAR=value"
```

### Useful Commands

```bash
# View logs
gcloud run services logs read playroom-diet-api --region us-central1 --limit 50

# Stream logs (follow mode)
gcloud run services logs tail playroom-diet-api --region us-central1

# Check service status
gcloud run services describe playroom-diet-api --region us-central1

# Set scaling limits
gcloud run services update playroom-diet-api --region us-central1 \
  --min-instances 1 --max-instances 10
```

---

## Frontend (Firebase Hosting)

### First-Time Setup

```bash
cd frontend
firebase init hosting
# → Select project
# → Public directory: dist
# → Single-page app: Yes
# → Don't overwrite index.html
```

### Redeploy

```bash
cd frontend
GPD_API_URL=https://playroom-diet-api-xxx-uc.a.run.app npm run build
firebase deploy --only hosting
```

---

## Airflow

Deployed separately via [Astronomer](https://astronomer.io). Use `astro deploy` from the `airflow/` directory.
