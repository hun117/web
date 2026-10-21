# 모퉁이 프론트엔드

Vue 3와 Vite로 만든 FastAPI 게시판 화면입니다.

## 개발

```bash
cd frontend
npm install
npm run dev
```

프론트는 브라우저에서 백엔드로 직접 요청합니다. 개발 서버는 `http://localhost:8000`을 사용하며, 백엔드 `.env`에는 `CORS_ORIGINS=http://localhost:5173`을 포함해야 합니다.

## 배포

```bash
npm run build
```

빌드 결과는 `frontend/dist/`에 생성됩니다. `npm run build`는 [vite.config.js](./vite.config.js)의 `API_BASE_URLS.production` 값인 `https://api.pepepe.p-e.kr`을 번들에 넣습니다. 백엔드 주소를 바꿀 때는 이 값 한 곳을 수정하세요. 카카오 JS 로그인을 쓸 경우 개발 환경에서는 `frontend/.env.local`에 `VITE_KAKAO_JAVASCRIPT_KEY`를 설정하고, 배포 환경에서는 GitHub Actions Repository Variable에 같은 이름으로 등록합니다. 이 키는 브라우저에 전달되는 공개 키입니다.

Nginx는 `nginx.conf.example`을 참고해 배포된 `dist/` 파일과 Vue history 경로를 제공하도록 설정합니다. API 경로는 Nginx에서 프록시하지 않습니다. 백엔드 `.env`에는 `COOKIE_DOMAIN=.pepepe.p-e.kr`와 실제 프론트 origin을 포함한 `CORS_ORIGINS`를 설정하세요. `www`와 `api`는 같은 사이트의 서브도메인이므로 `COOKIE_SAMESITE=lax`를 사용할 수 있습니다. 프론트가 HTTPS라면 백엔드도 HTTPS로 제공하고 `COOKIE_SECURE=true`로 설정해야 합니다.

## 테스트

```bash
npm test -- --runInBand
```
