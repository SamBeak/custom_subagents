# Example: B2B SaaS User Persona Analysis

## Input

```
아이디어: AI 기반 코드 리뷰 자동화 도구
타겟: 스타트업 개발팀
요청: 상세 페르소나 및 여정 분석
```

## Output

```markdown
## User Persona Report

### Analysis Summary
- **Idea**: AI 기반 코드 리뷰 자동화 도구
- **Primary Persona**: 김민수 (Tech Lead)
- **Secondary Personas**: 2
- **Key Insight**: 코드 리뷰 병목이 배포 속도의 핵심 제약

### User Segmentation

#### Identified Segments
| Segment | Size | Accessibility | WTP | Priority |
|---------|------|---------------|-----|----------|
| 스타트업 Tech Lead | 15,000+ | High | High | 1 |
| 시니어 개발자 | 50,000+ | Medium | Medium | 2 |
| 주니어 개발자 | 100,000+ | High | Low | 3 |

---

### Primary Persona

#### 👤 김민수 (Tech Lead)

**Basic Profile**
| Attribute | Details |
|-----------|---------|
| **Age** | 34세 |
| **Occupation** | Tech Lead @ 시리즈 A 스타트업 |
| **Location** | 서울 강남 |
| **Income** | 8,000만원 |
| **Tech Savviness** | 5/5 |
| **Archetype** | "바쁜 기술 리더" |

**Background Story**
> 민수는 5명의 개발팀을 이끄는 테크 리드다. 빠르게 성장하는 스타트업에서 
> 코드 품질과 배포 속도 사이에서 균형을 잡아야 하는 압박을 받고 있다.
> PR이 쌓일수록 리뷰 부담이 커지고, 이것이 팀 전체 속도를 늦추고 있다.

**A Day in Their Life**
- 아침: 슬랙 확인, 밀린 PR 리뷰 시작
- 낮: 미팅 3-4개, 코드 리뷰 중간중간 수행
- 저녁: 본인 코드 작업 (리뷰하느라 낮에 못함)

#### Goals & Motivations

**Primary Goals**
1. 코드 리뷰 시간을 50% 줄이기
2. 팀 전체 배포 주기 단축
3. 코드 품질 표준 유지

**Quote**
> "PR 리뷰가 쌓이면 팀 전체가 블로킹돼요. 
> 제가 병목이 되는 게 제일 싫어요."

#### Pain Points & Frustrations

**Pain Points**
| Pain Point | Severity | Frequency | Workaround |
|------------|----------|-----------|------------|
| 리뷰 시간 부족 | 5/5 | 매일 | 대충 승인 |
| 컨텍스트 스위칭 | 4/5 | 매일 | 리뷰 시간 블록 |
| 일관성 없는 피드백 | 3/5 | 주 2-3회 | 컨벤션 문서 |

#### Jobs-to-be-Done

**Functional Jobs**
| Job | Importance | Satisfaction |
|-----|------------|--------------|
| PR 코드 변경 이해 | High | 2/5 |
| 버그/보안 이슈 탐지 | High | 3/5 |
| 피드백 코멘트 작성 | Medium | 2/5 |

**Emotional Jobs**
| Job | Description |
|-----|-------------|
| 팀의 신뢰 유지 | 꼼꼼한 리뷰로 팀원 성장 지원 |
| 성취감 | 고품질 코드 배포 |

---

### User Journey Map

#### Current Journey (As-Is)

| Stage | Actions | Thoughts | Emotions | Pain Points |
|-------|---------|----------|----------|-------------|
| **PR 알림** | 슬랙/깃허브 알림 확인 | "또 쌓였네" | 😟 | 알림 피로 |
| **코드 이해** | 변경사항 파악 | "이거 뭐 바꾼 거지" | 😐 | 컨텍스트 부족 |
| **리뷰 작성** | 코멘트 작성 | "이걸 어떻게 설명하지" | 😟 | 시간 소모 |
| **승인** | Approve/Request changes | "제대로 봤나" | 😐 | 불확실성 |

#### Ideal Journey (To-Be)

| Stage | Improved Experience | Value Delivered |
|-------|---------------------|-----------------|
| PR 알림 | AI 요약과 함께 알림 | 즉시 컨텍스트 파악 |
| 코드 이해 | AI가 변경 영향 분석 | 5분 → 1분 |
| 리뷰 작성 | AI 제안 코멘트 | 직접 작성 최소화 |
| 승인 | AI 신뢰도 점수 | 확신 있는 결정 |

---

### Adoption Barriers Analysis

| Barrier | Description | Severity | Mitigation |
|---------|-------------|----------|------------|
| Trust | AI 리뷰 정확성 의심 | 4/5 | 정확도 대시보드 |
| Habit | 기존 워크플로우 변경 저항 | 3/5 | 점진적 도입 |
| Privacy | 코드 보안 우려 | 4/5 | 온프레미스 옵션 |

### Value Proposition Fit

#### Problem-Solution Fit
| User Problem | Solution | Fit Score |
|--------------|----------|-----------|
| 리뷰 시간 부족 | AI 자동 분석 | 5/5 |
| 컨텍스트 스위칭 | PR 요약 | 4/5 |
| 일관성 부족 | 표준 피드백 | 4/5 |

### Handoff Notes
- **For Idea-Expander**: Tech Lead 페인포인트 중심 확장
- **For Idea-Critic**: 신뢰/프라이버시 장벽 집중 검토
- **For Idea-Refiner**: "리뷰 시간 50% 절감" 가치 제안 강화
```
