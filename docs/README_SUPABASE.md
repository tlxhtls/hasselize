# Supabase Setup Guide for Hasselize

## Overview

Hasselize uses Supabase for:
- User authentication (Google, Apple OAuth)
- Database (PostgreSQL) for profiles, transformations, feed
- Real-time subscriptions (future)

## Prerequisites

- Supabase account: https://supabase.com
- Google Cloud project (for Google OAuth)
- Apple Developer account (for Apple OAuth, optional)

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click "New Project"
3. Configure:
   - **Name**: `hasselize`
   - **Database Password**: Generate strong password (save it!)
   - **Region**: Choose closest to your users
   - **Pricing Plan**: Free tier to start

4. Wait for project provisioning (~2 minutes)

## Step 2: Run Database Migration

1. Go to your Supabase project → SQL Editor
2. Click "New Query"
3. Copy the contents of `supabase/migrations/001_initial_schema.sql`
4. Paste and click "Run" (or press Ctrl+Enter)

This creates the following tables:
- `profiles` - User profiles and subscription info
- `camera_styles` - Available camera style options
- `prompts` - AI prompts for camera styles
- `transformations` - Image transformation records
- `feed` - Public gallery feed
- `likes` - User likes on feed items

## Step 3: Configure Environment Variables

### Frontend (apps/web/.env.local)

```bash
# Copy from Supabase Dashboard → Project Settings → API
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### Backend (apps/ai-backend/.env)

```bash
# Copy from Supabase Dashboard → Project Settings → API
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Security Note**: Never commit `SUPABASE_SERVICE_ROLE_KEY` to git!

## Step 4: Enable OAuth Providers

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API:
   - APIs & Services → Library
   - Search "Google+ API" → Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs:
     ```
     https://your-project.supabase.co/auth/v1/callback
     http://localhost:3000/auth/callback
     ```
5. Copy Client ID and Client Secret

6. In Supabase Dashboard:
   - Authentication → Providers → Google
   - Enable Google provider
   - Paste Client ID and Secret
   - Save

### Apple OAuth (Optional)

1. Go to [Apple Developer](https://developer.apple.com)
2. Create an App ID with "Sign in with Apple" capability
3. Create a Services ID:
   - Bundle ID: your app identifier
   - Return URLs:
     ```
     https://your-project.supabase.co/auth/v1/callback
     http://localhost:3000/auth/callback
     ```
4. Configure Sign in with Apple

5. In Supabase Dashboard:
   - Authentication → Providers → Apple
   - Enable Apple provider
   - Paste Service ID, Team ID, Key ID, Private Key
   - Save

## Step 5: Create Auth Callback Handler

The auth callback handler (`app/auth/callback/route.ts`) is already created. Verify it exists:

```bash
cat apps/web/app/auth/callback/route.ts
```

## Step 6: Test Authentication

### Start Development Server

```bash
cd apps/web
npm run dev
```

### Test Login Flow

1. Visit http://localhost:3000/login
2. Click "Sign in with Google"
3. Complete Google OAuth flow
4. Verify redirect to home page
5. Check Supabase Dashboard → Authentication → Users
   - New user should be created

### Verify Profile Creation

```sql
-- In Supabase SQL Editor
SELECT * FROM profiles;
```

Profile should be auto-created on first login via database trigger.

## Step 7: Configure Row Level Security (RLS)

RLS policies are already defined in the migration file. Verify they're active:

```sql
-- Check RLS status
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

All tables should have `rowsecurity = true`.

## Step 8: Test Database Operations

### From Frontend

```typescript
// Test profile fetch
import { createClient } from '@/lib/supabase/server'

const supabase = await createClient()
const { data } = await supabase.from('profiles').select('*')
console.log(data)
```

### From Backend

```python
# Test Supabase connection
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

response = supabase.table('profiles').select('*').execute()
print(response.data)
```

## Troubleshooting

### "Invalid API Key" Error

**Cause**: Missing or incorrect environment variables

**Solution**:
1. Verify `.env.local` exists
2. Check values match Supabase Dashboard
3. Restart dev server after changing env vars

### OAuth Callback Fails

**Cause**: Redirect URI mismatch

**Solution**:
1. Check redirect URI in OAuth provider matches exactly
2. Include both production and localhost URLs
3. Wait 5-10 minutes for OAuth provider changes to propagate

### Profile Not Created on Login

**Cause**: Database trigger not fired

**Solution**:
```sql
-- Check trigger exists
SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';

-- Recreate if missing (see migration file)
```

### RLS Policy Blocks Access

**Cause**: User not authenticated

**Solution**:
```sql
-- Check current user
select auth.uid();

-- Test RLS policy
set request.jwt.claim.sub = 'your-user-id';
select * from profiles;
```

## Production Deployment

1. Update environment variables in production
2. Change redirect URIs to production domain
3. Enable additional OAuth providers if needed
4. Set up database backups
5. Configure email templates (Supabase Dashboard → Auth → Email Templates)

## References

- Supabase Docs: https://supabase.com/docs
- Supabase Auth: https://supabase.com/docs/guides/auth
- Next.js Auth Helpers: https://supabase.com/docs/guides/auth/server-side/nextjs
- Migration File: `supabase/migrations/001_initial_schema.sql`
