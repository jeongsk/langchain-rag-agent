# Docker 로컬 환경 설정 가이드

이 가이드는 LangSmith 클라우드 없이 로컬 Docker 환경에서 LangGraph 애플리케이션을 실행하는 방법을 설명합니다.

## 사전 요구사항

- Docker Desktop 또는 Docker Engine 설치
- Docker Compose 설치 (Docker Desktop에 포함)
- API 키 (Google AI, OpenAI)

## 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 설정합니다:

```bash
# Google AI API Key (필수)
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI API Key (필수 - 폴백 모델용)
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith 설정 (선택사항 - 로컬에서는 false로 설정)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=langchain-rag-agent
```

## 2. Docker 컨테이너 빌드 및 실행

### 전체 서비스 시작

```bash
docker-compose up -d
```

이 명령은 다음 서비스를 시작합니다:
- **PostgreSQL**: LangGraph 상태 저장용 데이터베이스 (포트 5432)
- **Redis**: 캐싱 서비스 (포트 6379)
- **LangGraph API**: LangGraph 애플리케이션 서버 (포트 8123)
- **Frontend**: Next.js 웹 인터페이스 (포트 3000)

### 로그 확인

```bash
# 모든 서비스 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f langgraph-api
```

### 서비스 상태 확인

```bash
docker-compose ps
```

## 3. 서비스 접속

### 프론트엔드

Next.js 웹 인터페이스:
- **웹 UI**: http://localhost:3000

### 백엔드 API

LangGraph API는 다음 주소에서 접속 가능합니다:

- **API Base URL**: http://localhost:8123
- **Health Check**: http://localhost:8123/ok (응답: `{"ok":true}`)
- **API Docs**: http://localhost:8123/docs
- **Server Info**: http://localhost:8123/info
- **Metrics**: http://localhost:8123/metrics

### 테스트 요청 예시

```bash
# Health check
curl http://localhost:8123/ok

# 예상 응답: {"ok":true}

# 서버 정보 확인
curl http://localhost:8123/info

# API 문서 확인 (브라우저에서)
open http://localhost:8123/docs

# 사용 가능한 그래프 목록
curl http://localhost:8123/assistants/search
```

## 4. 서비스 중지 및 제거

### 서비스 중지 (데이터 보존)

```bash
docker-compose stop
```

### 서비스 중지 및 컨테이너 제거 (데이터 보존)

```bash
docker-compose down
```

### 모든 데이터 포함 완전 제거

```bash
docker-compose down -v
```

## 5. 서비스 재시작

```bash
# 코드 변경 후 재빌드
docker-compose up -d --build

# 서비스만 재시작 (빌드 없이)
docker-compose restart langgraph-api
```

## 참고: langgraph dev vs langgraph up

이 설정은 `langgraph dev` 명령을 사용합니다:
- **langgraph dev**: 개발 모드로 실행 (핫 리로드 지원, 디버깅에 적합)
- **langgraph up**: 프로덕션 모드로 실행

프로덕션 환경에서는 `langgraph up` 사용을 권장합니다.

## 6. 문제 해결

### 포트 충돌 문제

기본 포트(5432, 6379, 8123, 3000)가 이미 사용 중인 경우, `docker-compose.yml`에서 포트를 변경할 수 있습니다:

```yaml
services:
  postgres:
    ports:
      - "15432:5432"  # 왼쪽 포트 변경

  langgraph-api:
    ports:
      - "18123:8123"  # API 포트 변경

  frontend:
    ports:
      - "13000:3000"  # 프론트엔드 포트 변경
```

### 데이터베이스 연결 실패

1. PostgreSQL 컨테이너가 정상 실행 중인지 확인:
   ```bash
   docker-compose ps postgres
   ```

2. PostgreSQL 로그 확인:
   ```bash
   docker-compose logs postgres
   ```

### 벡터 스토어 파일 문제

`backend/vectorstore` 디렉토리가 존재하고 파일이 있는지 확인:

```bash
ls -la backend/vectorstore/
```

### API 키 문제

환경 변수가 올바르게 설정되었는지 확인:

```bash
docker-compose exec langgraph-api env | grep API_KEY
```

## 7. 개발 모드

### 백엔드 개발 모드

개발 중 코드 변경 사항을 실시간으로 반영하려면 `docker-compose.yml`의 langgraph-api 서비스 volumes 설정을 다음과 같이 수정:

```yaml
langgraph-api:
  volumes:
    - ./backend:/app  # 백엔드 코드 마운트
    - ./backend/vectorstore:/app/vectorstore:ro
    - ./backend/prompts:/app/prompts:ro
```

그리고 다음 명령으로 재시작:

```bash
docker-compose restart langgraph-api
```

### 프론트엔드 개발 모드

프론트엔드는 로컬에서 개발하는 것이 더 편리합니다:

```bash
cd frontend
pnpm install
pnpm dev
```

프론트엔드가 http://localhost:3000에서 실행되며, API는 환경 변수 `LANGGRAPH_API_URL`을 통해 백엔드와 연결됩니다.

frontend/.env.local 파일 생성:
```bash
LANGGRAPH_API_URL=http://localhost:8123
```

## 8. 데이터 백업

### PostgreSQL 데이터 백업

```bash
docker-compose exec postgres pg_dump -U langgraph langgraph > backup.sql
```

### PostgreSQL 데이터 복원

```bash
docker-compose exec -T postgres psql -U langgraph langgraph < backup.sql
```

## 9. 프로젝트 구조

```
langchain-rag-agent/
├── backend/              # LangGraph API 백엔드
│   ├── app.py           # 애플리케이션 엔트리포인트
│   ├── graph.py         # LangGraph 그래프 정의
│   ├── vectorstore/     # RAG 벡터 저장소
│   ├── prompts/         # 프롬프트 템플릿
│   ├── Dockerfile       # 백엔드 Docker 이미지
│   └── pyproject.toml   # Python 의존성
├── frontend/            # Next.js 프론트엔드
│   ├── app/            # Next.js 앱 라우터
│   ├── components/     # React 컴포넌트
│   ├── Dockerfile      # 프론트엔드 Docker 이미지
│   └── package.json    # Node.js 의존성
└── docker-compose.yml  # 전체 스택 오케스트레이션
```

## 참고사항

- 로컬 환경에서는 LangSmith 클라우드 연동 없이 동작합니다
- 모든 상태는 PostgreSQL에 저장됩니다
- Redis는 선택사항이지만 성능 향상을 위해 권장됩니다
- 프로덕션 환경에서는 보안을 위해 데이터베이스 비밀번호를 변경하세요
- 프론트엔드는 Next.js로 구축되어 있으며, 백엔드 API와 통신합니다
