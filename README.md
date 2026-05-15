## 📖 프로젝트 소개

>본 프로젝트는 분산된 교육 운영 도구와 비효율적인 학습 관리 환경을 개선하기 위해 통합 교육 플랫폼(LMS) 개발을 목표로 선정되었습니다. 기존 교육 과정에서는 과제, 평가, 커뮤니케이션이 개별 도구로 분리되어 있어 운영 복잡도와 관리 비용이 지속적으로 증가하고 있었습니다. 이에 학습자·강사·관리자가 하나의 플랫폼에서 학습 진행 현황과 데이터를 일관되게 관리할 수 있는 환경을 구축하고자 했습니다. 본 기획은 실제 교육 운영 흐름을 반영한 기능 중심 설계를 통해 사용성과 확장성을 확보하는 데 중점을 두었습니다. 또한 향후 콘텐츠 확장과 데이터 기반 학습 분석이 가능한 구조를 마련하는 것을 핵심 기획 의도로 삼았습니다.
---


## 🧰 사용 스택

<div>
  <img src="https://img.shields.io/badge/Python 3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Django 5.2-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/DRF 3.16-ff1709?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL 14-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white">
  <img src="https://img.shields.io/badge/Celery 5.5-37814A?style=for-the-badge&logo=celery&logoColor=white">
  <img src="https://img.shields.io/badge/AWS S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white">
  <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white">
  <img src="https://img.shields.io/badge/AWS EC2-FF9900?style=for-the-badge&logo=amazonec2&logoColor=white">
  <img src="https://img.shields.io/badge/GitHub Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white">
  <img src="https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white">
  <img src="https://img.shields.io/badge/Black-000000?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/mypy-2A6DB2?style=for-the-badge&logo=python&logoColor=white">
</div>


---
## 🔗  배포링크

#### <a href="https://my.ozcodingschool.site/" target="_blank">통합교육 플랫폼(LMS)사이트 바로가기</a>

---

## 👥 팀 소개

###  1팀 — 인증 & 수강

| <a href="https://github.com/EMEM-Kim"><img src="https://avatars.githubusercontent.com/u/93540726?v=4" width=100px/><br/><sub><b>@EMEM-Kim</b></sub></a> | <a href="https://github.com/jongwonkim987"><img src="https://avatars.githubusercontent.com/u/252281839?s=96&v=4" width=100px/><br/><sub><b>@jongwonkim987</b></sub></a> | <a href="https://github.com/netrunnerr25"><img src="https://avatars.githubusercontent.com/u/252514779?s=400&v=4" width=100px/><br/><sub><b>@netrunnerr25</b></sub></a> | <a href="https://github.com/jihyeongh21-svg"><img src="https://avatars.githubusercontent.com/u/111436967?v=4" width=100px/><br/><sub><b>@jihyeongh21-svg</b></sub></a> |
|:---:|:---:|:---:|:---:|
| 김영민 | 김종원 | 윤수현 | 하지형 |

**담당 기능:** 인증(이메일/휴대폰 인증, 카카오·네이버 소셜 로그인, 비밀번호 재설정 및 계정 복구), 수강(기수별 수강 신청, 수강 이력 조회)

<details>
<summary><b>🔐 로그인 & 회원가입</b></summary>
<br>

**다양한 가입 및 로그인**
이메일 기반 회원가입은 물론, 카카오·네이버 소셜 로그인 연동으로 빠르게 학습을 시작할 수 있습니다.

**본인 인증**
Gmail을 이용한 이메일 인증과 Twilio 기반의 휴대폰 번호 인증을 통해 실제 사용자를 검증하고 보안을 강화했습니다.

**보안 체계**
JWT(Access/Refresh Token) 인증 방식을 도입하여 로그인 상태를 안정적으로 유지하고 보안 사고를 방지합니다.

</details>

<details>
<summary><b>📚 수강 신청 & 이력 조회</b></summary>
<br>

**스마트 수강 신청**
현재 모집 중인 기수 목록을 실시간으로 조회하고, 클릭 한 번으로 수강 신청을 완료할 수 있습니다.

**학습 이력 관리**
참여 과정, 기수 정보, 학습 상태를 대시보드에서 한눈에 확인하여 체계적인 학습 계획을 세울 수 있습니다.

</details>

<details>
<summary><b>👤 프로필 & 회원 탈퇴</b></summary>
<br>

**프로필 관리**
닉네임 중복 검사 및 S3 Presigned URL을 활용한 프로필 이미지 업로드를 지원합니다.

**안전한 회원 탈퇴**
데이터 손실을 방지하기 위해 14일 유예 기간을 두는 논리 삭제(Soft Delete) 방식을 적용하여 사용자의 기록을 보호합니다.

</details>

---

###  2팀 — 쪽지시험

| <a href="https://github.com/kochanyeol"><img src="https://avatars.githubusercontent.com/u/252294378?v=4" width="100px"/><br/><sub><b>@kochanyeol</b></sub></a> | <a href="https://github.com/wasw2123"><img src="https://avatars.githubusercontent.com/u/51053345?v=4" width="100px"/><br/><sub><b>@wasw2123</b></sub></a> | <a href="https://github.com/yoojinsohn"><img src="https://avatars.githubusercontent.com/u/251306944?v=4" width="100px"/><br/><sub><b>@yoojinsohn</b></sub></a> | <a href="https://github.com/gunung-kim"><img src="https://avatars.githubusercontent.com/u/251298309?v=4" width="100px"/><br/><sub><b>@gunung-kim</b></sub></a> |
|:---:|:---:|:---:|:---:|
| 고찬열 | 서민혁 | 손유진 | 김건웅 |

**담당 기능:** 쪽지시험 출제 및 배포, 자동 채점, 결과 확인

<details>
<summary><b>📋 시험 출제 및 배포</b></summary>
<br>

**유연한 시험 설계**
시험 → 문제 → 배포 → 제출의 4단계 구조로 분리 설계하여, 하나의 시험에 다양한 유형의 문제를 자유롭게 구성할 수 있습니다.

**안정적인 시험 운영**
배포 시점의 문제를 스냅샷으로 고정하여, 이후 문제가 수정되더라도 수강생의 시험에 영향을 주지 않아 데이터 무결성을 보장합니다.

</details>

<details>
<summary><b>⚡ 자동 채점 & 부정행위 감지</b></summary>
<br>

**즉시 자동 채점**
수강생이 답안을 제출하는 즉시 DB에 저장된 정답과 비교하여 채점이 이루어지며, OX·단답형·다지선다 등 모든 문항 유형에 통일된 채점 로직을 적용합니다.

**부정행위 감지**
시험 도중 화면 이탈을 부정행위로 간주하며, 3회 적발 시 시험이 즉시 종료되고 작성한 답안이 자동으로 제출됩니다.

</details>

<details>
<summary><b>📊 결과 확인</b></summary>
<br>

**상세한 결과 확인**
제출 후 문항별 정오답, 배점, 해설을 한눈에 확인할 수 있는 결과 페이지로 자동 이동하여 학습 성취도를 즉시 파악할 수 있습니다.

</details>

---

###  3팀 — QnA & AI 챗봇

| <a href="https://github.com/gumba6740"><img src="https://avatars.githubusercontent.com/u/252312782?v=4" width="100px"/><br/><sub><b>@gumba6740</b></sub></a> | <a href="https://github.com/Mashiro2465"><img src="https://avatars.githubusercontent.com/u/164816209?v=4" width="100px"/><br/><sub><b>@Mashiro2465</b></sub></a> | <a href="https://github.com/Di-Mo-De-OH"><img src="https://avatars.githubusercontent.com/u/171827467?v=4" width="100px"/><br/><sub><b>@Di-Mo-De-OH</b></sub></a> |
|:---:|:---:|:---:|
| 최승용 | 김민석 | 오디모데 |

**담당 기능:** QnA 게시판, AI 챗봇, CS 상담 챗봇

<details>
<summary><b>❓ 질문 (Question)</b></summary>
<br>

**질문 등록 및 수정**
제목, 내용, 카테고리, 이미지 URL 기반으로 질문을 생성하며, 본인이 작성한 질문만 수정할 수 있습니다. 권한 외 접근 시 예외 처리가 적용됩니다.

**질문 조회**
검색어, 카테고리, 답변 상태, 정렬 조건 기반의 페이지네이션 조회를 지원하며, 상세 조회 시 질문 본문·이미지·작성자 정보·답변 목록·댓글을 한 번에 확인할 수 있습니다.

</details>

<details>
<summary><b>🤖 AI / 챗봇 (AI & Chatbot)</b></summary>
<br>

**AI 답변 생성**
질문 기반으로 GPT 모델이 자동 답변을 생성하며, 중복 생성 시 예외 처리가 적용됩니다.

**QnA 챗봇**
질문 컨텍스트 기반으로 AI와 실시간 스트리밍(SSE) 대화를 지원하며, 횟수 초과 시 게시판으로 유도합니다. 이전 대화 내역 조회 및 세션 만료 처리를 지원합니다.

**CS 상담 챗봇**
수강·탈퇴 등 서비스 관련 문의에 실시간 스트리밍(SSE)으로 응답하며, 이전 상담 내역 조회가 가능합니다.

**AI 세션 관리**
사용자가 진행 중인 QnA AI 대화 세션 목록 및 마지막 메시지를 조회할 수 있습니다.

</details>

<details>
<summary><b>✅ 답변 (Answer)</b></summary>
<br>

**답변 등록 및 수정**
특정 질문에 내용 및 이미지를 포함하여 답변을 작성할 수 있으며, 본인이 작성한 답변만 수정 가능합니다. 권한 없는 사용자 접근 시 예외 처리가 적용됩니다.

**답변 채택**
질문 작성자가 답변을 채택할 수 있으며, 이미 채택된 답변이 존재할 경우 409 예외 처리를 통해 중복 채택을 방지합니다.

**댓글**
특정 답변에 댓글을 등록할 수 있으며, 내용은 1~500자로 제한됩니다.

</details>

<details>
<summary><b>🗂️ 카테고리 (Category)</b></summary>
<br>

**카테고리 관리 (어드민)**
`parent_id` depth 기반으로 대/중/소 분류를 자동으로 처리하며, 중복 이름 등록 시 예외 처리가 적용됩니다. 검색어 및 카테고리 타입 기반의 페이지네이션 조회를 지원합니다.

**카테고리 조회 (일반)**
대/중/소 분류의 트리 구조로 전체 카테고리를 반환합니다.

**게시판 카테고리 (어드민)**
카테고리 이름, 활성 상태, 생성/수정 시각을 상세 조회할 수 있습니다.

</details>

---

###  4팀 — 커뮤니티 & 교육 운영

| <a href="https://github.com/RyuHawon"><img src="https://avatars.githubusercontent.com/u/251678501?v=4" width=100px/><br/><sub><b>@RyuHawon</b></sub></a> | <a href="https://github.com/JaeheeLee-be"><img src="https://avatars.githubusercontent.com/u/250348641?v=4" width=100px/><br/><sub><b>@JaeheeLee-be</b></sub></a> | <a href="https://github.com/DHChe"><img src="https://avatars.githubusercontent.com/u/185660120?v=4" width=100px/><br/><sub><b>@DHChe</b></sub></a> | <a href="https://github.com/YoonMawel"><img src="https://avatars.githubusercontent.com/u/152850885?v=4" width=100px/><br/><sub><b>@YoonMawel</b></sub></a> |
|:---:|:---:|:---:|:---:|
| 류하원 | 이재희 | 채동훈 | 임혜민 |

**담당 기능:** 커뮤니티 게시판, 좋아요·댓글·사용자 태그, 과정·기수·과목 관리

<details>
<summary><b>📌 커뮤니티 게시판</b></summary>
<br>

**게시글 관리**
카테고리별 분류와 함께 제목·본문·조회수·노출 여부·공지 여부를 세분화하여 관리합니다. 작성자만 수정·삭제할 수 있으며, 관리자에게는 공지 등록·노출 제어 권한이 부여됩니다.

**이미지 업로드**
S3 Presigned URL 기반의 안전한 썸네일 업로드를 지원하여, 서버 부하 없이 대용량 이미지를 빠르게 첨부할 수 있습니다.

</details>

<details>
<summary><b>❤️ 좋아요 & 댓글 시스템</b></summary>
<br>

**좋아요**
`UniqueConstraint`로 한 사용자가 한 게시글에 한 번만 좋아요를 누를 수 있도록 보장하며, `is_liked` 토글 구조로 좋아요/취소 이력을 관리합니다. 인덱스 최적화(`idx_post_is_liked`)로 인기 게시글 집계 성능도 확보했습니다.

**댓글**
게시글당 다중 댓글을 지원하며, `PostCommentTag` 모델로 댓글 내 다른 사용자 멘션(@태그)을 구현했습니다. 댓글-태그 조합에는 `unique_together`를 적용하여 중복 태그를 방지합니다.

</details>

<details>
<summary><b>🎓 과정·기수·과목 관리</b></summary>
<br>

**과정 관리**
부트캠프 단위의 과정(Course) CRUD를 어드민 전용으로 제공하며, 과정명·태그의 유일성을 보장합니다. 중복 등록 시 409 Conflict로 응답하며, 썸네일 업로드도 Presigned URL로 지원합니다.

**기수 운영**
기수(Cohort) 모델로 동일 과정 내 차수, 정원, 시작/종료일, 진행 상태(준비중/진행중/종료)를 관리합니다. `(course, number)` 복합 유니크 제약으로 동일 차수 중복 생성을 방지합니다.

**세부 과목 구성**
과목(Subject) 단위로 과정 내 커리큘럼을 분할 관리하며, 일수·시간·운영 상태를 함께 저장해 학사 일정과 시수 정보를 체계적으로 제공합니다.

</details>

---

## 📑 프로젝트 규칙
 
### Branch Strategy
 
- `main` / `dev` 브랜치 기본 생성
- `main`, `dev` 브랜치 직접 push 금지
- PR 승인 시 최소 1인 이상의 리뷰 필수


### Git Convention

**커밋 메시지 형식**

1. 커밋 타이틀   : {이모지} {type}: {간결한 커밋 메시지 요약}
2. 변경사항      : 무엇을 변경했는지, 왜 변경했는지 작성
3. 관련 이슈     : #이슈번호 (선택)



 
커밋 타이틀은 아래 형식으로 작성합니다: `{이모지} {type}: {내용}`
 
| 이모지 | 타입 | 설명 |
|:---:|:---:|:---|
| ✨ | `feat` | 새로운 기능 추가 |
| 🐛 | `fix` | 버그 수정 |
| 💡 | `chore` | 기능 추가 없이 코드 수정 (오타, 주석 등) |
| 🎨 | `style` | 코드 포매팅 수정 |
| 📝 | `docs` | 문서 수정 (README 등) |
| 🚚 | `build` | 빌드 관련 파일 수정 |
| ✅ | `test` | 테스트 코드 추가/변경 (프로덕션 코드 변경 없음) |
| ♻️ | `refactor` | 리팩터링 (기능 변화 없음) |
| 🚑 | `hotfix` | 긴급 수정 |
 
### Pull Request
 
- 제목 형식: `{이모지} {type}: {작업 내용}` (예: `✨ feat: 로그인 API 구현`)
- PR 생성 전 `dev` 브랜치 최신화 필수
- 최소 1인 이상 코드 리뷰 후 머지

**PR 템플릿**
 
```markdown
## ✅ PR 요약
- 관련 이슈 번호: #이슈번호
- 작업 요약: 어떤 작업을 했는지 간단하게 적어주세요.
 
## 📄 상세 내용
- [ ] 주요 변경 사항 1
- [ ] 주요 변경 사항 2
- [ ] 주요 변경 사항 3
 
## 📸 스크린샷 (선택)
> UI 변경이 있는 경우 스크린샷을 첨부해 주세요.
 
## 📝 기타 참고 사항
> 리뷰어가 알아야 할 추가 정보나 논의할 사항을 적어주세요.
 
## 🧪 PR Checklist
- [ ] 커밋 메시지 컨벤션에 맞게 작성했습니다.
- [ ] 변경 사항에 대한 테스트를 했습니다. (버그 수정 / 기능에 대한 테스트)
```
 
### Code Convention
 
- 코드 포매터: `Black` — 일관된 코드 스타일 자동 적용
- import 정렬: `isort` — import 순서 자동 정렬
- 타입 검사: `mypy` — 정적 타입 분석으로 런타임 오류 사전 방지


### Communication
 
- Discord 활용
- 정기 회의 진행
- 노션 활용

---

## 📋 주요 문서

| 문서 | 링크 |
|:---:|:---:|
| 📜 API 명세서 | [바로가기](https://docs.google.com/spreadsheets/d/1hahPeS9qtbuaVF5811BAdMJtpIsp67T7fPVE9d6-KoU/edit?usp=drive_link) |
| 📜 요구사항 정의서 | [바로가기](https://docs.google.com/spreadsheets/d/1R9nLz_03tXHqZ6CzUpih-iP5nnX2_Q3dMdKOKM22rzM/edit?usp=drive_link) |
| 📜 ERD | [바로가기](https://dbdiagram.io/d/Externship-6823ff4e5b2fc4582f7c2afa) |

