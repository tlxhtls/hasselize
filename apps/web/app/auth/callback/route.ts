/**
 * Supabase Auth Callback Handler.
 *
 * This route handles OAuth callbacks from providers like Google and Apple.
 * After user completes OAuth flow on provider's site, they are redirected here
 * with an authorization code that we exchange for a session.
 */

import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'
import { redirect } from 'next/navigation'

/**
 * GET /auth/callback
 *
 * Handle OAuth callback from Supabase.
 *
 * Query parameters:
 * - code: Authorization code from OAuth provider
 * - next: Optional redirect path after login (default: /)
 *
 * Flow:
 * 1. User clicks "Sign in with Google"
 * 2. Supabase redirects to Google OAuth page
 * 3. User approves app
 * 4. Google redirects back here with code
 * 5. We exchange code for session
 * 6. Redirect user to home page or requested page
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  // If we have an auth code, exchange it for a session
  if (code) {
    const supabase = await createClient()

    try {
      await supabase.auth.exchangeCodeForSession(code)
    } catch (error) {
      console.error('Error exchanging code for session:', error)
      // Redirect to login page with error
      return NextResponse.redirect(
        new URL(`/login?error=auth_callback_failed`, request.url)
      )
    }
  }

  // Redirect to the page they came from, or home page
  return NextResponse.redirect(new URL(next, request.url))
}

/**
 * Optional: Add error handling route
 *
 * GET /auth/callback/error
 *
 * Display friendly error message for auth failures.
 */
export async function POST(request: Request) {
  // For POST requests (if needed for future use)
  return NextResponse.json({ message: 'Method not allowed' }, { status: 405 })
}
