# Cloudflare R2 Setup Guide for Hasselize

## Overview

Hasselize uses Cloudflare R2 for:
- Storing original uploaded images
- Storing transformed AI images
- Storing thumbnail images
- Serving images via public URL

## Prerequisites

- Cloudflare account: https://dash.cloudflare.com
- R2 enabled (free tier: 10GB storage, 10M read operations/month)

## Step 1: Create R2 Bucket

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **R2** → **Create Bucket**
3. Configure:
   - **Bucket name**: `hasselize-images` (or your choice)
   - **Location**: Select region closest to users
4. Click "Create bucket"

## Step 2: Configure Bucket CORS

1. Go to your bucket → **Settings** → **CORS Policy**
2. Add the following CORS policy:

```json
[
  {
    "AllowedOrigins": [
      "http://localhost:3000",
      "https://your-production-domain.com"
    ],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600,
    "ExposeHeaders": ["ETag"]
  }
]
```

3. Save

## Step 3: Create API Token

1. Go to **R2** → **Manage R2 API Tokens**
2. Click "Create API Token"
3. Configure:
   - **Permissions**: Admin Read & Write
   - **TTL**: Unlimited (or set expiration)
4. Click "Create Token"
5. **IMPORTANT**: Save the credentials:
   - Access Key ID
   - Secret Access Key
   - Account ID (from URL)

## Step 4: Configure Environment Variables

Add to `apps/ai-backend/.env`:

```bash
# R2 Configuration
R2_ENDPOINT_URL=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=hasselize-images
R2_PUBLIC_DOMAIN=https://your-custom-domain.com  # Optional, see Step 6
```

**Security Note**: Never commit `R2_SECRET_ACCESS_KEY` to git!

## Step 5: Test Storage Service

### Start Backend

```bash
cd apps/ai-backend
uvicorn api.main:app --reload
```

### Test Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Response should include R2 connection status.

### Test Presigned URL Generation

```bash
curl -X POST http://localhost:8000/api/v1/storage/presign \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.jpg",
    "content_type": "image/jpeg"
  }'
```

Response:
```json
{
  "upload_url": "https://...",
  "key": "uploads/test.jpg"
}
```

### Test Upload Using Presigned URL

```bash
# Get presigned URL first
PRESIGNED_URL=$(curl -s -X POST http://localhost:8000/api/v1/storage/presign \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.jpg"}' | jq -r '.upload_url')

# Upload file
curl -X PUT "$PRESIGNED_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @test.jpg
```

### Test Public Access

```bash
# Access uploaded file (if public domain is configured)
curl https://your-custom-domain.com/uploads/test.jpg
```

## Step 6: Set Up Custom Domain (Optional but Recommended)

### Why Custom Domain?

- Clean URLs without R2 endpoint
- HTTPS support with custom SSL
- Better caching with Cloudflare CDN

### Steps

1. **Buy or use existing domain** (e.g., `images.hasselize.com`)

2. **Add CNAME record** in DNS:
   - Type: CNAME
   - Name: `images`
   - Target: `your-bucket.r2.cloudflarestorage.com`

3. **Configure custom domain in Cloudflare**:
   - Go to R2 → Your Bucket → Settings
   - Click "Add Custom Domain"
   - Enter: `images.hasselize.com`
   - Click "Add Domain"

4. **Update environment variable**:
   ```bash
   R2_PUBLIC_DOMAIN=https://images.hasselize.com
   ```

5. **Test public access**:
   ```bash
   curl https://images.hasselize.com/uploads/test.jpg
   ```

## Step 7: Verify Backend Integration

The storage service (`apps/ai-backend/services/storage_service.py`) should automatically work with these environment variables.

### Test Full Upload Flow

```python
# In Python
import os
from services.storage_service import storage_service

# Test upload
with open("test.jpg", "rb") as f:
    url = storage_service.upload_file(
        f.read(),
        "uploads/test.jpg",
        content_type="image/jpeg"
    )
    print(f"Uploaded to: {url}")

# Test presigned URL
upload_url, key = storage_service.get_presigned_url("test.jpg", "image/jpeg")
print(f"Presigned URL: {upload_url}")
```

## Step 8: Configure Frontend

Update `apps/web/.env.local`:

```bash
# R2 Public Domain (for displaying images)
NEXT_PUBLIC_R2_PUBLIC_DOMAIN=https://images.hasselize.com
```

Now frontend can display images:

```typescript
import { getPublicUrl } from '@/lib/storage/r2'

const imageUrl = getPublicUrl('uploads/transformation-123.jpg')
// → https://images.hasselize.com/uploads/transformation-123.jpg
```

## Step 9: Set Up Lifecycle Policies (Optional)

To automatically delete old files:

1. Go to R2 → Your Bucket → **Settings** → **Lifecycle Rules**
2. Add rule:
   - **Name**: "Delete thumbnails after 30 days"
   - **Apply to**: Prefix `thumbnails/`
   - **Expire after**: 30 days
3. Add rule:
   - **Name**: "Delete originals after 90 days"
   - **Apply to**: Prefix `originals/`
   - **Expire after**: 90 days

## Troubleshooting

### "Access Denied" Error

**Cause**: Incorrect credentials or permissions

**Solution**:
1. Verify API token has Admin Read & Write
2. Check credentials in `.env` match exactly
3. Regenerate API token if needed

### "CORS Error" in Browser

**Cause**: CORS policy not configured or incorrect

**Solution**:
1. Check bucket CORS settings
2. Include your domain in AllowedOrigins
3. Allow PUT and POST methods

### "NoSuchBucket" Error

**Cause**: Bucket name or region mismatch

**Solution**:
1. Verify bucket exists in Cloudflare Dashboard
2. Check `R2_BUCKET_NAME` in `.env`
3. Check `R2_ENDPOINT_URL` includes correct account ID

### Presigned URL Expired Immediately

**Cause**: System time mismatch

**Solution**:
1. Verify server system time is accurate
2. Use NTP to sync time: `sudo ntpdate pool.ntp.org`

## Monitoring

### Track Storage Usage

1. Go to Cloudflare Dashboard → R2
2. Check:
   - Total objects count
   - Storage used
   - Read/Write operations

### Set Up Alerts

1. Cloudflare Dashboard → R2 → Metrics
2. Configure alerts for:
   - Storage > 9GB (90% of free tier)
   - Read operations > 9M/month
   - Error rate > 1%

## Production Checklist

- [ ] Bucket created
- [ ] CORS policy configured
- [ ] API token created with Admin Read & Write
- [ ] Environment variables set (backend + frontend)
- [ ] Custom domain configured (optional but recommended)
- [ ] Public access tested
- [ ] Lifecycle policies configured (optional)
- [ ] Monitoring alerts set up
- [ ] Backup strategy planned

## Cost Estimation

Free tier (monthly):
- Storage: 10GB
- Class A operations (write): 1M
- Class B operations (read): 10M

Beyond free tier:
- Storage: $0.015/GB/month
- Class A: $4.50/M operations
- Class B: $0.36/M operations

**Example**: 1000 users, 10 transformations/day
- Storage: ~5GB/month (within free tier)
- Operations: ~300k Class A, ~600k Class B (within free tier)

## References

- Cloudflare R2 Docs: https://developers.cloudflare.com/r2/
- R2 API: https://developers.cloudflare.com/r2/api/
- Boto3 (S3-compatible): https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html
