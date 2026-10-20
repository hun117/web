# Kakao social login design

## Goal and approved defaults

Add Kakao sign-up and login to the existing Vue and FastAPI application. A successful login uses the application's existing `EN_AT` HttpOnly cookie and displays the user's email in the existing account header.

Approved design defaults:

- Kakao is the only provider in the first release.
- Kakao REST Authorization Code flow is completed by FastAPI. The browser never receives the Kakao client secret or provider access token.
- Request only Kakao email consent. A new account requires an email that Kakao reports as valid and verified. If it is unavailable, do not create an account; send the user back to login with an email-consent message.
- Never auto-link a Kakao identity to an existing password account based only on email. Show an existing-account message and leave that account unchanged.
- Preserve the current email/password sign-up and login flows. Show the Kakao CTA on both login and registration screens.

## User and request flow

1. The user selects “카카오로 계속하기” from `/login` or `/register`. The browser navigates to `GET /user/oauth/kakao/start` through the existing same-origin API proxy.
2. FastAPI creates a cryptographically random `state`, places a signed, short-lived state token in an HttpOnly, SameSite=Lax cookie, then redirects to Kakao's authorization endpoint requesting `account_email` consent.
3. Kakao redirects to the registered callback URI with either an authorization code or an error. FastAPI validates and consumes the state cookie before exchanging the code.
4. FastAPI exchanges the code at Kakao's token endpoint and calls Kakao's user-info endpoint. It uses the Kakao service user ID as the stable identity and reads only the user ID, email validity/verification flags, email, and optional profile nickname.
5. If the `(provider, provider_user_id)` identity already exists, log in its linked local user even if Kakao no longer returns an email. Otherwise, require a valid verified email. Compare email addresses case-insensitively when checking for an existing user; if a local user already has that email, do not link or modify either account. If not, store the normalized lowercase email and create a local user and the Kakao identity in one database transaction. Use the Kakao nickname when available; otherwise use the email's local part as the required local display name. Generate an undisclosed high-entropy password value to satisfy the existing non-null password column.
6. FastAPI issues the normal application cookie and redirects to `/posts`. The Vue app calls `GET /user/me` on page load to restore the header email after a full OAuth redirect or browser refresh. The callback never puts email or tokens in a URL.

The Kakao REST flow uses `https://kauth.kakao.com/oauth/authorize`, `https://kauth.kakao.com/oauth/token`, and `https://kapi.kakao.com/v2/user/me`. Kakao documents `state` as the CSRF check and requires the callback URI to match the URI registered for the REST API key. [Kakao REST API](https://developers.kakao.com/docs/en/kakaologin/rest-api), [Kakao security guide](https://developers.kakao.com/docs/en/getting-started/security-guideline)

## API, persistence, and configuration

Add these backend routes:

- `GET /user/oauth/kakao/start`: redirect to Kakao; return a clear service-unavailable response if required provider configuration is missing.
- `GET /user/oauth/kakao/callback`: validate state, handle provider denial, exchange the code, create or look up the identity, set the app cookie, and redirect to the configured frontend route.
- `GET /user/me`: validate `EN_AT` and return the existing `ApiResponse` envelope with the current user's email; return 401 and clear the cookie when missing, expired, malformed, or linked to a deleted user.

Keep `POST /user/signup` and `POST /user/login` paths and payloads unchanged. Their app tokens must use the real local user ID as the JWT `sub`; update the existing token creation call so `/user/me` can resolve the user safely.

Add a `SocialAccount` table with a user foreign key, provider name, and provider user ID. Enforce uniqueness on `(provider, provider_user_id)`. Do not alter existing user columns. The app uses SQLAlchemy `create_all` and has no migration framework, so import the model before `Base.metadata.create_all`; this additive table is created without rebuilding the existing SQLite user table. If two callbacks race to create the same identity, roll back the losing transaction, re-read the identity, and log in the already-created user.

Add environment settings for `KAKAO_REST_API_KEY`, `KAKAO_CLIENT_SECRET`, `KAKAO_REDIRECT_URI`, `FRONTEND_URL` (origin only), and `COOKIE_SECURE`. Require the REST API key, client secret, and redirect URI before starting OAuth; require a non-default `SECRET_KEY` for production. For local development, the registered callback is the frontend origin's proxied path, for example `http://127.0.0.1:5173/user/oauth/kakao/callback`; production must route frontend and `/user/*` through the same browser origin so the existing same-origin cookie behavior works. Register this exact callback in Kakao Developers and enable Kakao Login plus the email consent item. Kakao's user-info response includes email validity and verification fields, so account creation checks both rather than trusting email presence alone. [Kakao REST API user information](https://developers.kakao.com/docs/en/kakaologin/rest-api)

The application JWT remains valid for 30 minutes. Set `EN_AT` HttpOnly, SameSite=Lax, and Secure in production, with cookie lifetime matching token expiry. Existing tokens with the current constant `sub` cannot hydrate `/user/me`; deployers should expect users with an old cookie to sign in again once after rollout.

## Failure handling and privacy

- Handle Kakao cancellation, missing code, state mismatch/expiry, token exchange failure, user-info timeout/failure, missing or unverified email, existing local email, and missing server configuration with these allowlisted redirect codes: `cancelled`, `invalid_state`, `email_required`, `email_unverified`, `account_exists`, `provider_unavailable`, and `provider_error`. The frontend maps them to localized messages and ignores unknown values.
- Apply a short timeout to Kakao HTTP requests. Do not log authorization codes, access/refresh tokens, client secrets, email addresses, or raw provider response bodies.
- Do not store Kakao access or refresh tokens. Store only the provider identity mapping and the local user data already needed by the app.
- If `/user/me` returns 401, clear the frontend email state and show the normal logged-out header without surfacing an auth error on public pages.
- Do not add account-linking, Kakao unlink, logout, Google/Naver, or OpenID Connect flows in this release.

## Verification and acceptance

Backend pytest coverage uses a temporary SQLite database and mocked Kakao HTTP responses; tests never require live Kakao credentials. Cover state success/mismatch/expiry, cancellation, token and user-info failures, missing/unverified email, email collision without linking, first-time account creation, repeated login by provider ID, concurrent duplicate identity handling, `/user/me` valid/invalid/expired cookies, and unchanged password login/sign-up behavior.

Frontend Jest coverage verifies Kakao CTA presence on login and registration, navigation to the backend start route, callback error messages, successful `/user/me` header hydration, and logged-out fallback on 401. The full backend pytest suite, frontend Jest suite, and frontend production build must pass.

Acceptance requires that a mocked first Kakao login creates exactly one local user and one identity; a repeated login reuses that user; the existing email account is never silently linked; a successful callback ends at `/posts` with the email in the header; and the Kakao credentials and tokens never reach frontend code or callback URLs.
