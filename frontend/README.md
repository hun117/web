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

빌드 결과는 저장소 루트의 `static/`에 생성됩니다. `npm run build`는 [vite.config.js](./vite.config.js)의 `API_BASE_URLS.production` 값인 `http://100.100.100.20:8000`을 번들에 넣습니다. 백엔드 주소를 바꿀 때는 이 값 한 곳을 수정하세요. 카카오 JS 로그인을 쓰면 공개 키를 `KAKAO_JAVASCRIPT_KEY` 변수로 설정합니다.

Nginx는 `nginx.conf.example`을 참고해 `static/` 파일과 Vue history 경로를 제공하도록 설정합니다. API 경로는 Nginx에서 프록시하지 않습니다. 백엔드 주소는 브라우저에서 직접 접속할 수 있어야 하며, 프론트가 HTTPS라면 백엔드도 HTTPS여야 합니다. 백엔드의 `CORS_ORIGINS`에는 사용자가 접속하는 프론트 origin을 정확히 등록하세요. 서로 다른 사이트 간 쿠키를 쓸 때는 HTTPS와 `COOKIE_SECURE=true`, `COOKIE_SAMESITE=none` 설정이 필요합니다.

## 테스트

```bash
npm test -- --runInBand
```
