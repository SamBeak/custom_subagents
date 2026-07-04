# Commands

Claude Code 슬래시 커맨드 정본. 수정은 이 디렉토리에서 하고 `scripts/sync-agents.ps1 -Apply`로 `~/.claude/commands/`에 배포한다.

| 커맨드 | 용도 |
|---|---|
| `일일마감` | 당일(또는 지정 날짜) 일일업무보고를 검토·확정(`status: confirmed`) |
| `주간마감` | 주간 마감 캐스케이드(주간보고 → 팀장브리핑 → PPT)를 대화형 실행 |

> 주의: `주간마감.md`는 zero-touch 리포의 절대 경로(`C:\Users\ATL\...`)를 참조하는 머신 종속 커맨드다.
