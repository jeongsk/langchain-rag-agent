# 🤖 LangChain & LangGraph RAG 챗봇

LangChain과 LangGraph 공식 문서를 기반으로 질문에 답변하는 RAG 에이전트입니다.

## 기능

- 📚 LangChain/LangGraph 공식 문서 기반 검색
- 💬 한국어 질문/답변 지원
- 🔄 스트리밍 응답
- 💾 세션별 대화 기록 관리
- 📝 예제 질문 제공
- 🐳 Docker 기반 배포 지원
- 🎨 Next.js 프론트엔드 UI

## 프로젝트 구조

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

## 실행 방법

### Docker로 실행 (권장)

```bash
# 환경 변수 설정
cp backend/.env.example .env
# .env 파일에 API 키 설정

# 전체 스택 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

서비스 접속:
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8123
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 로컬 개발 모드

#### 백엔드

```bash
cd backend

# 의존성 설치
uv sync

# 앱 실행
uv run streamlit run app.py
```

#### 프론트엔드

```bash
cd frontend

# 의존성 설치
pnpm install

# 개발 서버 실행
pnpm dev
```

## 지원하는 주제

- LangChain/LangGraph API, 클래스, 메서드
- 구현 패턴과 모범 사례
- 상태 관리, 에이전트 워크플로우
- 도구 통합 및 함수 호출
- 문제 해결 및 디버깅

## 환경 변수

필수 환경 변수:
- `GOOGLE_API_KEY`: Google AI API 키
- `OPENAI_API_KEY`: OpenAI API 키

선택 환경 변수:
- `LANGSMITH_TRACING`: LangSmith 추적 활성화 (기본값: false)
- `LANGSMITH_API_KEY`: LangSmith API 키
- `LANGSMITH_PROJECT`: LangSmith 프로젝트 이름

자세한 내용은 [DOCKER_SETUP.md](./DOCKER_SETUP.md)를 참조하세요.
