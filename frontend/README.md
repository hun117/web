# 모퉁이 프론트엔드

Vue 3와 Vite로 만든 FastAPI 게시판 화면입니다.

## 개발

```bash
cd frontend
npm install
npm run dev
```

개발 서버는 `/board`와 `/user` 요청을 `http://127.0.0.1:8000`으로 전달합니다. FastAPI를 먼저 실행한 뒤 Vite 주소를 열어 주세요.

## FastAPI에서 제공

```bash
npm run build
```

빌드 결과는 저장소 루트의 `static/`에 생성됩니다. FastAPI의 `/` 경로에서 화면을 제공하고 `/static/` 경로에서 번들을 읽습니다.

## 테스트

```bash
npm test -- --runInBand
```
