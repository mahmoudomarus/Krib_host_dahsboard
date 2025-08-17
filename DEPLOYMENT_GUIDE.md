# 🚀 Deployment Guide

This guide will help you deploy your RentalAI Dashboard to production using Vercel (frontend) and Render (backend).

## 📋 Prerequisites

Before deploying, ensure you have:
- [x] Database schema deployed to Supabase ✅
- [ ] GitHub repository set up
- [ ] Vercel account
- [ ] Render account
- [ ] Environment variables ready

## 🗂️ Project Structure

Your project is now properly organized:

```
rental-ai-dashboard/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend  
├── supabase/         # Database migrations
└── README.md         # Project documentation
```

## 🐙 GitHub Setup

1. **Initialize Git and push to your repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: RentalAI Dashboard"
   git remote add origin https://github.com/mahmoudomarus/Krib_host_dahsboard.git
   git push -u origin main
   ```

## 🎯 Frontend Deployment (Vercel)

### Step 1: Connect Repository
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository: `mahmoudomarus/Krib_host_dahsboard`

### Step 2: Configure Project
- **Framework**: Vite (auto-detected)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### Step 3: Environment Variables
Add these environment variables in Vercel:

```
VITE_API_URL=https://your-backend-url.onrender.com/api
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for build to complete
3. Your frontend will be available at: `https://your-app.vercel.app`

## ⚙️ Backend Deployment (Render)

### Step 1: Create Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository: `mahmoudomarus/Krib_host_dahsboard`

### Step 2: Configure Service
- **Name**: `rental-ai-backend`
- **Root Directory**: `backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Add these environment variables in Render (as secrets):

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# Supabase S3 Storage
AWS_ACCESS_KEY_ID=your_s3_access_key_id
AWS_SECRET_ACCESS_KEY=your_s3_secret_access_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_s3_bucket_name
S3_ENDPOINT_URL=https://your-project-id.supabase.co/storage/v1/s3

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for build and deployment
3. Your backend will be available at: `https://your-backend.onrender.com`

## 🔄 Update Frontend with Backend URL

After your backend is deployed:

1. Go back to Vercel project settings
2. Update the `VITE_API_URL` environment variable:
   ```
   VITE_API_URL=https://your-backend.onrender.com/api
   ```
3. Redeploy the frontend

## 🔍 Testing Your Deployment

### Test Backend
Visit: `https://your-backend.onrender.com/docs`
- Should show the FastAPI documentation
- Test the `/health` endpoint

### Test Frontend  
Visit: `https://your-app.vercel.app`
- Should load the RentalAI dashboard
- Try signing up/logging in
- Test creating a property

## 🛠️ Troubleshooting

### Common Issues

**Frontend Build Errors:**
- Check that all environment variables are set
- Ensure `frontend/` directory structure is correct
- Verify Node.js version compatibility

**Backend Deployment Errors:**
- Check Python version (3.11+ required)
- Verify all environment variables are set as secrets
- Check Render logs for specific error messages

**Database Connection Issues:**
- Verify Supabase URL and keys are correct
- Check if your IP is allowed in Supabase settings
- Test database connection from local environment first

**CORS Issues:**
- Ensure your frontend URL is added to CORS origins in backend
- Check that API calls use the correct backend URL

### Getting Help

1. Check the logs in Vercel/Render dashboards
2. Test locally first with the same environment variables
3. Create an issue in the GitHub repository with error details

## 🎉 Success!

Once deployed, your RentalAI Dashboard will be live with:
- ✅ Production-ready frontend on Vercel
- ✅ Scalable backend on Render  
- ✅ Real database with Supabase
- ✅ AI-powered features
- ✅ Secure authentication
- ✅ File storage with S3

Your users can now access the full-featured rental management platform!
