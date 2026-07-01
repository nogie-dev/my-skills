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

### 설치

Marketplace 방식 권장:

```bash
codex plugin marketplace add nogie-dev/my-skills --ref main
codex plugin add github-issue-manager@my-skills
```

설치 후 Codex를 새로 시작합니다.

직접 skill만 설치하려면:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo nogie-dev/my-skills \
  --path codex-skills/github-issue-manager
```

### 사용 준비

1. `gh` CLI 설치
2. GitHub 인증

```bash
gh auth login
gh auth status
```

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



## GitHub Project Manager

`codex-skills/github-project-manager`는 GitHub Projects 작업을 `gh` CLI 기준으로 처리하는 Codex 스킬입니다.

### 주요 기능

- `gh` 설치·인증·Project scope 사전 검사
- project 목록, 상세, field, item 조회
- issue/PR/draft item 추가 및 project item 관리 가이드
- Status 같은 single-select field 변경 helper: 기본 dry-run, `--apply`일 때만 실제 변경
- `Priority`, `Size` 같은 다른 single-select field도 `--field`로 변경 가능

### 설치

Marketplace 방식 권장:

```bash
codex plugin marketplace add nogie-dev/my-skills --ref main
codex plugin add github-project-manager@my-skills
```

설치 후 Codex를 새로 시작합니다.

직접 skill만 설치하려면:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo nogie-dev/my-skills \
  --path codex-skills/github-project-manager
```

### 사용 준비

GitHub Projects는 `project` scope가 필요합니다.

```bash
gh auth login
gh auth refresh -s project
gh auth status
```

### 자주 쓰는 요청 예시

```text
내 GitHub Project 목록을 보여줘
프로젝트 2번의 field와 item을 요약해줘
이슈 #4를 In progress로 옮겨줘
이 이슈를 프로젝트에 추가하고 Ready 상태로 바꿔줘
```

### helper script 사용법

```bash
# 인증/scope/project 접근 가능 여부 확인
python3 codex-skills/github-project-manager/scripts/gh_project_readiness.py --owner OWNER

# Status 변경 미리보기: 실제 변경 안 함
python3 codex-skills/github-project-manager/scripts/gh_project_status.py \
  --owner OWNER \
  --project PROJECT_NUMBER_OR_TITLE \
  --repo OWNER/REPO \
  --item ISSUE_NUMBER \
  --status "In progress"

# 실제 변경: preview 확인 후 --apply 명시
python3 codex-skills/github-project-manager/scripts/gh_project_status.py \
  --owner OWNER \
  --project PROJECT_NUMBER_OR_TITLE \
  --repo OWNER/REPO \
  --item ISSUE_NUMBER \
  --status "In progress" \
  --apply

# 다른 single-select field 변경
python3 codex-skills/github-project-manager/scripts/gh_project_status.py \
  --owner OWNER \
  --project PROJECT_NUMBER_OR_TITLE \
  --repo OWNER/REPO \
  --item ISSUE_NUMBER \
  --field Priority \
  --status P1
```

### 배포 구조

이 저장소는 두 설치 방식을 모두 제공합니다.

```text
.agents/plugins/marketplace.json              # Codex plugin marketplace
plugins/github-issue-manager/                 # Marketplace용 issue manager plugin 패키지
plugins/github-project-manager/               # Marketplace용 project manager plugin 패키지
codex-skills/github-issue-manager/            # 직접 issue manager skill 설치용 원본
codex-skills/github-project-manager/          # 직접 project manager skill 설치용 원본
```

자세한 동작은 다음 파일을 봅니다.

- [`plugins/github-issue-manager/.codex-plugin/plugin.json`](plugins/github-issue-manager/.codex-plugin/plugin.json)
- [`plugins/github-project-manager/.codex-plugin/plugin.json`](plugins/github-project-manager/.codex-plugin/plugin.json)
- [`codex-skills/github-issue-manager/SKILL.md`](codex-skills/github-issue-manager/SKILL.md)
- [`codex-skills/github-project-manager/SKILL.md`](codex-skills/github-project-manager/SKILL.md)
- [`codex-skills/github-issue-manager/references/branch-naming-policy.md`](codex-skills/github-issue-manager/references/branch-naming-policy.md)
- [`codex-skills/github-issue-manager/references/issue-template-policy.md`](codex-skills/github-issue-manager/references/issue-template-policy.md)
