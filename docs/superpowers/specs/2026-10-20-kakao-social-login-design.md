# Kakao social login design

## Goal and approved behavior

Add Kakao sign-up and login to the existing Vue and FastAPI application. Vue starts Kakao Login with the Kakao JavaScript SDK. After login, the account header shows the Kakao nickname for a Kakao account and continues to show the email for an email/password account.

Approved behavior:

- Kakao is the only social provider in this release.
- Do not request Kakao email consent. Kakao email is currently unavailable in this application, so it cannot be used to identify or link accounts.
- Identify a social account by Kakao's stable service user ID. If it already has a local identity mapping, log in the linked local user. Otherwise, create a local user and mapping.
- If Kakao does provide an email in a future/configuration change, reject the Kakao login when that email already belongs to a local account. Never auto-link accounts by matching email.
- A new Kakao account has no email or password. Its displayed name comes from the consented Kakao nickname. Nickname consent or a non-empty nickname is required; if absent, fail with a profile-consent message.
- Keep the existing email/password sign-up and login paths and behavior.
- Show the Kakao login action on both login and registration pages.

The email collision rule cannot be evaluated when Kakao does not return an email. Under the current no-email-consent flow, authentication therefore relies on Kakao user ID; the collision rejection is applied only when a provider email is present. Kakao documents email as a consent-controlled, optional user field and nickname as requiring profile/nickname consent. [Kakao JavaScript Login](https://developers.kakao.com/docs/ko/kakaologin/js), [Kakao REST API](https://developers.kakao.com/docs/ko/kakaologin/rest-api)

## Flow and components

1. Vue loads the Kakao JavaScript SDK using the public JavaScript key from frontend configuration. On the login and registration pages, the Kakao button obtains a one-time state value from `GET /user/oauth/kakao/state`, then calls `Kakao.Auth.authorize()` with that state and the registered frontend callback URI. Request only the Kakao profile/nickname scope; do not request email.
2. Kakao redirects to `/login/kakao/callback` with an authorization code, state, or cancellation/error. The Vue callback handler verifies that the returned state matches the value saved for this login attempt, then immediately removes code and state from the visible URL and posts them to the backend. The backend also compares state with a short-lived, HttpOnly, SameSite=Lax state cookie set by the state endpoint, so browser-side checking is not the only CSRF defense.
3. `POST /user/oauth/kakao/callback` validates and consumes state, exchanges the authorization code using the Kakao REST API key (and client secret when configured), then retrieves user information from Kakao. Kakao tokens remain on the backend and are discarded after profile retrieval.
4. The backend looks up `(provider='kakao', provider_user_id)`. For an existing mapping, it refreshes the local display name from the latest non-empty nickname and logs in the mapped local user. For a new mapping, it checks any returned email against existing local users case-insensitively; a collision rejects the login without changing either account. Otherwise it creates a local user with null email/password, the nickname as name, and the new mapping in one transaction.
5. The backend issues the normal `EN_AT` HttpOnly application cookie. Vue navigates to `/posts`, calls `GET /user/me` on startup, and uses the returned display name and kind to render email or Kakao nickname. No provider token is returned to Vue or placed in an application URL.

Kakao's JavaScript SDK uses the authorization-code process for web login; the server exchanges the code for tokens and retrieves profile data. The SDK requires a JavaScript key and registered JavaScript domain/redirect URI. [Kakao JavaScript Login](https://developers.kakao.com/docs/ko/kakaologin/js)

## API and persistence

Add backend routes:

- `GET /user/oauth/kakao/state`: create a cryptographically random short-lived state, set its HttpOnly cookie, and return the state for the SDK authorization request. Return a clear service-unavailable response if Kakao config is missing.
- `POST /user/oauth/kakao/callback`: accept the one-time code and state, validate state cookie, exchange the code, retrieve profile, resolve/create the user and social mapping, set `EN_AT`, and return a minimal authenticated display payload.
- `GET /user/me`: validate `EN_AT`, resolve the local user, and return `{display_name, display_kind}` where kind is `email` or `nickname`. Clear the cookie and return 401 for missing, invalid, expired, or orphaned sessions.

Keep `POST /user/signup` and `POST /user/login` routes and request contracts unchanged. Correct token creation to use the actual local user ID as JWT `sub`, so `/user/me` can safely resolve either authentication type. Existing tokens with the current constant subject will require a fresh login after rollout.

Add `SocialAccount` with `user_id`, provider, and provider user ID, plus a uniqueness constraint on `(provider, provider_user_id)`. Update `User.email` and `User.password` to nullable for social-only accounts; keep `User.name` required and use it for the current nickname. This requires an explicit SQLite migration/rebuild for the existing `user` table because `create_all` will not change nullability. Preserve existing rows and the current email lookup behavior. The migration must be repeatable and tested against a temporary copy of the current schema. Import all models before metadata initialization.

Use `KAKAO_JAVASCRIPT_KEY` in frontend build/runtime configuration and `KAKAO_REST_API_KEY`, optional `KAKAO_CLIENT_SECRET`, `KAKAO_REDIRECT_URI`, `FRONTEND_URL`, and `COOKIE_SECURE` on the backend. The JavaScript key is public; REST credentials and Kakao tokens must remain server-side. Kakao Developers must have Kakao Login enabled, the profile/nickname consent item configured, the frontend JavaScript domain registered, and the exact redirect URI registered. Keep frontend and `/user/*` API routes on the same public origin for cookie behavior. Local development should use the current frontend origin and its API proxy. Production cookies use HttpOnly, SameSite=Lax, Secure, and an expiry matching the 30-minute application JWT.

## Failure handling and privacy

- Handle missing configuration, user cancellation, absent code, invalid/expired state, provider timeout/error, missing nickname consent, invalid callback payload, existing-email collision when an email is present, and database identity races with allowlisted UI error codes. The frontend maps known codes to Korean messages and ignores unknown provider details.
- Apply short timeouts to Kakao HTTP requests. Never log authorization codes, Kakao tokens, client secrets, emails, or raw provider bodies.
- Store the Kakao user ID and current nickname only as required for identity and display. Do not store Kakao access or refresh tokens.
- `/user/me` returning 401 clears frontend authentication display and restores the logged-out header without a public-page error.
- Do not add account linking, Kakao unlink/logout, other providers, or OIDC in this release.

## Verification and acceptance

Backend pytest coverage uses temporary SQLite and mocked Kakao HTTP responses. Cover repeatable migration preserving existing accounts, missing/invalid state, cancellation, code exchange/profile failures, missing nickname, first-time user/mapping creation with null email/password, repeated provider-ID login, returned-email collision without linking, concurrent duplicate mapping handling, `/user/me` for both account kinds and invalid cookies, and unchanged password signup/login behavior.

Frontend Jest coverage verifies SDK initialization/config handling, Kakao CTA on login and registration, state and callback handling including URL cleanup, callback error messages, successful `/user/me` hydration for email and nickname, and logged-out fallback on 401. Run the backend pytest suite, frontend Jest suite, and production build.

Acceptance requires that one Kakao user ID always resolves to one local user; Kakao login succeeds without an email; email/password accounts keep their current display and auth behavior; social users see their Kakao nickname; a returned email collision is rejected without account linking; and Kakao credentials/tokens never reach frontend code or application callback URLs.
