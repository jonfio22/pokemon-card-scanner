# Deploy Pokemon Card Scanner to Vercel

## Prerequisites
- Vercel account (free at vercel.com)
- Git repository with your code
- Google API key

## Deployment Steps

### 1. Install Vercel CLI (optional but recommended)
```bash
npm i -g vercel
```

### 2. Deploy from Command Line
```bash
cd Pokemon-Card-Scanner
vercel
```

### 3. Or Deploy from GitHub
1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "Import Project"
4. Select your GitHub repository
5. Configure environment variables (see below)

### 4. Set Environment Variables
In Vercel dashboard, go to Settings > Environment Variables and add:
- `GOOGLE_API_KEY` = your-google-api-key-here

### 5. Deploy
Click "Deploy" and wait for the build to complete!

## What Gets Deployed

- `/` - Main web interface
- `/api/scan` - Card scanning API endpoint
- `/api/health` - Health check endpoint

## Notes

- The deployment uses `opencv-python-headless` which works in serverless environments
- Maximum function duration is set to 30 seconds for AI processing
- Memory is set to 3GB for image processing
- Static files (card images) are not deployed to keep size small

## Testing Your Deployment

Visit: `https://your-project.vercel.app`

The app should work exactly like the local version!