# 📚 LLM 기반 웹툰/웹소설 추천 챗봇([PIXARY](http://3.38.96.243/))  

<br>



## 🚀 프로젝트 개요
웹툰과 웹소설의 폭발적인 성장 속에서, 사용자의 취향을 반영한 **맞춤형 콘텐츠 추천**이 중요해졌습니다.  
본 프로젝트는 **대화형 AI 챗봇을 활용하여 웹툰/웹소설을 추천하는 시스템**을 개발하는 것을 목표로 합니다.

LLM 과 RAG 기술을 적용하여,  
사용자의 질의에 맞는 웹툰/웹소설을 추천하고 상세한 작품 정보를 제공하는 서비스를 제공합니다.

<br>



## 🔍 주요 기능

### 🗂️  **웹툰/웹소설 추천 시스템**
- LLM을 기반으로 사용자 입력 분석 후 **개인화된 작품 추천**
- **RAG** 기법을 활용하여 데이터베이스에서 최적의 추천 목록 생성
- **장르별 특화 모델** 적용 (예: 로맨스, 판타지, 무협 등)

### 🗂️  **데이터 수집 및 관리**
- **네이버 웹툰, 카카오웹툰, 카카오페이지, 네이버시리즈** API 및 Selenium을 활용한 크롤링
- 작품의 **별점, 조회수, 관심도** 등을 활용한 정량적 분석
- **ChromaDB** 를 활용한 벡터 검색 시스템 적용

### 🗂️  **데이터 크롤링 및 전처리 과정**
#### 1️⃣ **데이터 크롤링**:
   - 네이버 웹툰, 카카오웹툰, 카카오페이지, 네이버시리즈에서 API 및 Selenium을 활용하여 데이터 수집
   - 작품별 메타데이터(제목, 작가, 장르, 별점, 조회수, 완결 여부 등) 저장
   - HTML 파싱을 통해 추가적인 사용자 리뷰 및 댓글 데이터 크롤링

#### 2️⃣ **크롤링한 데이터 형식 및 설명**:

| 변수명 | 컬럼명 | 데이터 타입 | 설명 |
|------|------|-----------|------|
| title | 제목 | STRING | 작품의 제목 |
| author | 글 작가 | STRING | 작품을 집필한 글 작가명 |
| illustrator | 그림 작가 | STRING | 작품을 그린 그림 작가명 |
| genre | 장르 | STRING | 웹툰/웹소설의 장르 (예: 판타지, 로맨스, 액션) |
| rating | 별점 | FLOAT | 사용자가 평가한 평균 별점 |
| views | 조회수 | INT | 해당 작품의 총 조회수 |
| type | 타입 | STRING | 웹툰 또는 웹소설 구분 |
| status | 연재상태 | STRING | 연재 중 또는 완결 여부 |
| update_days | 연재요일 | STRING | 정기적으로 연재되는 요일 |
| thumbnail | 썸네일 | STRING | 작품 대표 이미지 URL |
| url | URL | STRING |작품 URL |
| keywords | 키워드 | STRING | 작품을 대표하는 주요 키워드 |
| synopsis | 줄거리 | STRING | 작품의 간략한 줄거리 |
| original | 원작 | STRING | 원작 소설이 존재하는 경우 원작 정보 |
| age_limit | 이용 연령 | STRING | 작품의 연령 제한 |
| episodes | 에피소드 수 | INT | 현재까지 공개된 총 에피소드 개수 |
| comments | 댓글 수 | INT | 사용자들이 남긴 총 댓글 수 |
| recent_comments_count | 최신 댓글 수 | INT | 최근 31일 이내의 댓글 개수 |
| first_episode | 최초 연재일 | STRING | 최초 연재 날짜 |

#### 3️⃣ **데이터 변환 및 벡터화**:
   - TF-IDF, Word2Vec, BERT 등의 NLP 기법을 활용하여 작품 설명 및 리뷰 데이터를 벡터화
   - ChromaDB에 벡터 저장하여 고속 검색 최적화

#### 4️⃣ **정규화 (Score Normalization)**:
   - 서로 다른 플랫폼(네이버웹툰, 카카오페이지, 카카오웹툰, 네이버시리즈)의 평점 체계를 장르별로 일관되게 조정
   - 변수별 EDA분석을 통한 이상치 조정 및 Min-Max Scaling 또는 Log Scaling을 적용하여 정규화
   - 웹툰별 조회수 대비 별점 비율을 조정하여 신뢰성 있는 평점 모델 구축

#### 5️⃣ 🤖 **대화형 챗봇 인터페이스**
- NLP 기반의 **텍스트 질의응답**
- 추천된 작품에 대한 **추가 정보 제공 및 필터링** (예: 완결 여부, 특정 장르 선호 등)
- 지속적인 학습을 통해 사용자 맞춤형 추천 개선

<br>



## 🛠 기술 스택
#### 1️⃣ **백엔드**
- **Python, Django**
- **MySQL / AWS RDS** (데이터 저장 및 관리)
- **ChromaDB** (벡터 검색)
- **LangChain / OpenAI API** (LLM 활용)

#### 2️⃣ **프론트엔드**
- **Django**

#### 3️⃣ **데이터 및 머신러닝**
- **Selenium / BeautifulSoup** (크롤링)
- **Hugging Face Transformers / OpenAI GPT** (언어 모델 활용)
- **TensorFlow / PyTorch/ HuggingFace** (모델 학습 및 벡터 임베딩)
<br>

## 📊 추천 알고리즘
#### 1️⃣ **협업 필터링 + 콘텐츠 기반 필터링 혼합 모델 적용**
   - 사용자 선호도 기반 추천 (Explicit/Implicit Feedback)
   - 콘텐츠 유사도 기반 추천 (TF-IDF, Word2Vec, BERT 등 활용)

#### 2️⃣ **LLM을 활용한 RAG 기반 추천**
   - 사용자 질의를 분석하여 적절한 작품 추천
   - 자연어 이해를 통해 세부적인 취향 반영

#### 3️⃣ **웹툰/웹소설 메타데이터 분석**
   - 조회수, 별점, 댓글 등 주요 지표를 활용한 스코어별 추천 개선
<br>



## 🏗️ 시스템 아키텍처
![system_architecture](https://github.com/user-attachments/assets/96a2e143-1f27-4523-8391-886cf4550bcd)

```
사용자 → 프론트엔드 → 백엔드(Django) → 데이터베이스(MySQL) → LLM 추천 엔진(OpenAI API, LangChain) → 결과 반환
```
<br>


## :gear: 실행 방법
#### 1️⃣ 프로젝트 클론
```bash
git clone https://github.com/SKNETWORKS-FAMILY-AICAMP/SKN06-FINAL-2Team.git
cd SKN06-FINAL-2Team
```

#### 2️⃣ 가상 환경 설정 및 패키지 설치
```bash
conda create -n pixary python=3.12
conda activate pixary
pip install -r requirements.txt
```

#### 3️⃣ 서버 실행
```bash
python manage.py runserver --insecure
```                   
