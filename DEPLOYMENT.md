# Backend and frontend deployment guide

## Prerequisites
- `gcloud` CLI installed and authenticated (`brew install --cask gcloud-cli && gcloud auth login`)
- `firebase` CLI installed (`npm install -g firebase-tools && firebase login`)
- Supabase setup with table (see [/backend/README.md](/backend/README.md))
- Airflow deployed (e.g. via Astro CLI at Astro)

## Backend (via Cloud Run)

```bash
cd backend

# first time: enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com

# build and deploy
gcloud run deploy playroom-diet-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=xxx,SUPABASE_SECRET_KEY=xxx,AIRFLOW_HOST=xxx,AIRFLOW_STATIC_TOKEN=xxx"
```

After deploy, note the service URL: `https://playroom-diet-api-xxx-uc.a.run.app`

### Update env vars only (no rebuild)
```bash
gcloud run services update playroom-diet-api --region us-central1 \
  --update-env-vars "KEY=value"
```

### View logs
```bash
gcloud run services logs read playroom-diet-api --region us-central1 --limit 50
```

### Set max instances
```bash
gcloud run services update playroom-diet-api --region us-central1 --max-instances 10
```

## Frontend (via Firebase Hosting)

```bash
cd frontend

# first time only
firebase init hosting
# → select project, use 'dist' as public dir, configure as SPA: yes

# build and deploy
GPD_API_URL=https://playroom-diet-api-xxx-uc.a.run.app npm run build
firebase deploy --only hosting
```

## Avoiding cold starts

Keep one minimal instance warm (~$0.03/hour):
```bash
gcloud run services update playroom-diet-api --region us-central1 \
  --min-instances 1 --cpu 0.5 --memory 256Mi
```

Scale back to zero:
```bash
gcloud run services update playroom-diet-api --region us-central1 --min-instances 0
```
