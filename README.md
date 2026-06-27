# my-skills

개인 Codex 스킬 모음입니다.

## GitHub Issue Manager

`codex-skills/github-issue-manager`는 GitHub issue 작업을 `gh` CLI 기준으로 처리하는 Codex 스킬입니다.

### 주요 기능

- `gh` 설치·인증 상태 사전 검사
- issue 조회, 생성, 수정, 댓글, close/reopen 작업 가이드
- `.github/ISSUE_TEMPLATE` 자동 감지 후 template mode on/off 판단
- 안전한 issue 생성 helper: 기본 dry-run, `--apply`일 때만 실제 생성
- issue 기반 branch naming 정책 문서화

### 사용 준비

1. `gh` CLI 설치
2. GitHub 인증

```bash
gh auth login
gh auth status
```

3. 스킬을 Codex가 읽을 수 있는 skills 경로에 설치하거나 이 저장소 경로에서 사용합니다.

### 자주 쓰는 요청 예시

```text
이 저장소의 열린 이슈를 정리해줘
이 버그 내용을 GitHub issue로 만들어줘
#123 이슈 작업용 브랜치를 만들어줘
현재 레포의 issue template 사용 가능 여부를 확인해줘
```

### helper script 사용법

```bash
# gh 인증, 레포 정보, issue template, label 상태 확인
python3 codex-skills/github-issue-manager/scripts/gh_issue.py inspect \
  --repo OWNER/REPO \
  --repo-dir /path/to/repo

# issue 생성 미리보기: 실제 생성 안 함
python3 codex-skills/github-issue-manager/scripts/gh_issue.py create \
  --repo OWNER/REPO \
  --repo-dir /path/to/repo \
  --title "Issue title" \
  --body-file /tmp/issue.md \
  --label bug

# 실제 생성: preview 확인 후 --apply 명시
python3 codex-skills/github-issue-manager/scripts/gh_issue.py create \
  --repo OWNER/REPO \
  --repo-dir /path/to/repo \
  --title "Issue title" \
  --body-file /tmp/issue.md \
  --label bug \
  --apply
```

### issue template 동작

스킬은 대상 작업 레포의 다음 경로를 검사합니다.

```text
.github/ISSUE_TEMPLATE/
.github/ISSUE_TEMPLATE.md
```

- 사용 가능한 Markdown template 또는 YAML issue form이 있으면 template mode를 켭니다.
- 없거나 유효하지 않으면 template mode만 끄고 issue 작업은 계속합니다.
- template 파일 생성·수정은 사용자가 명시적으로 요청할 때만 합니다.

### branch naming 설정

설정이 없으면 기본값은 다음 형식입니다.

```text
issue/<number>-<slug>
```

레포별 규칙이 필요하면 대상 레포에 `.github/github-issue-manager.yml`을 둡니다.

```yaml
branch_naming:
  default_prefix: issue
  prefixes:
    bug: fix
    feature: feat
    task: chore
  prefix_priority: [bug, feature, task]
  format: "{prefix}/{number}-{slug}"
  slug:
    max_length: 48
    separator: "-"
    lowercase: true
  base_branch: default
  create_remote: false
  comment_on_issue: false
```

자세한 동작은 다음 파일을 봅니다.

- [`codex-skills/github-issue-manager/SKILL.md`](codex-skills/github-issue-manager/SKILL.md)
- [`codex-skills/github-issue-manager/references/branch-naming-policy.md`](codex-skills/github-issue-manager/references/branch-naming-policy.md)
- [`codex-skills/github-issue-manager/references/issue-template-policy.md`](codex-skills/github-issue-manager/references/issue-template-policy.md)
