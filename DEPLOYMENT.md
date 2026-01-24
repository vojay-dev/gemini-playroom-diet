# Deployment Guide

All components are implemented in a platform-independent manner. For example, the database can be any PostgreSQL instance, and Airflow can run on any hosting provider, as only open-source features are used. This approach maximizes flexibility, and platforms are chosen solely for cost optimization.

Overview:

- **Backend**: Google Cloud Run
- **Frontend**: Firebase Hosting
- **Airflow**: Astronomer Astro
- **Database**: Supabase
- **Storage**: Supabase

## Backend (Google Cloud Run)

### First-time setup

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

> [!IMPORTANT]
> Note down the service URL as we need it for frontend deployment. It can be found in the Google Cloud Console later.

### Managing environment variables

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

## Frontend (Firebase Hosting)

### First-time setup

```bash
cd frontend
firebase init hosting
# → Select project
# → Public directory: dist
# → Single-page app: Yes
# → Don't overwrite index.html
```

### Redeploy

> [!IMPORTANT]
> Set correct service URL from backend deployment.

```bash
cd frontend
GPD_API_URL=https://playroom-diet-api-xxx-uc.a.run.app npm run build
firebase deploy --only hosting
```

## Airflow

Local Airflow setup as well as deployment are handled via the [Astro CLI](https://github.com/astronomer/astro-cli) (open-source).

```bash
astro deploy
```
