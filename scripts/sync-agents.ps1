#!/usr/bin/env pwsh
<#
sync-agents.ps1 — 리포(정본) → ~/.claude 배포본 동기화 (비대화형)

사용법 (리포 루트에서 실행):
  pwsh scripts/sync-agents.ps1                 # 드리프트 리포트만 (무변경)
  pwsh scripts/sync-agents.ps1 -Apply          # DIFFERENT 항목만 갱신
  pwsh scripts/sync-agents.ps1 -Apply -All     # NOT_DEPLOYED 항목도 설치
  pwsh scripts/sync-agents.ps1 -Agent daily-work-reporter,weekly-work-reporter -Apply
  pwsh scripts/sync-agents.ps1 -Dest <path>    # 기본: $HOME\.claude

종료 코드: 리포트 모드 0=전부 IDENTICAL, 1=드리프트 존재 / Apply 모드 0=성공, 1=실패 항목 존재
-Agent 필터는 에이전트(및 번들 스크립트)에만 적용되며 commands/*.md는 항상 포함된다.
#>
param(
    [switch]$Apply,
    [switch]$All,
    [string[]]$Agent,
    [string]$Dest = (Join-Path $HOME ".claude")
)

$ErrorActionPreference = 'Stop'
# pwsh -File 호출 시 "-Agent a,b"가 단일 문자열로 바인딩되므로 콤마 분리 정규화
if ($Agent) { $Agent = @($Agent | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ }) }
if (-not (Test-Path "agents")) {
    Write-Host "오류: 리포 루트에서 실행하세요 ('agents' 디렉토리 없음)"
    exit 1
}

function Get-Sha256([string]$Path) { (Get-FileHash -Path $Path -Algorithm SHA256).Hash }

$items = @()

# 1) 에이전트 .md + 번들 스크립트 (test_*, fixtures 제외)
foreach ($categoryDir in Get-ChildItem -Path "agents" -Directory) {
    foreach ($agentDir in Get-ChildItem -Path $categoryDir.FullName -Directory) {
        $name = $agentDir.Name
        $json = Join-Path $agentDir.FullName "agent.json"
        $md   = Join-Path $agentDir.FullName "$name.md"
        if (-not (Test-Path $json) -or -not (Test-Path $md)) { continue }
        if ($Agent -and $name -notin $Agent) { continue }
        $version = (Get-Content $json -Raw | ConvertFrom-Json).version
        $items += [pscustomobject]@{ Kind='agent'; Name=$name; Source=$md
            Target=(Join-Path $Dest "agents\$name.md"); Version=$version }
        $scriptsDir = Join-Path $agentDir.FullName "scripts"
        if (Test-Path $scriptsDir) {
            foreach ($f in Get-ChildItem $scriptsDir -File) {
                if ($f.Name -like 'test_*') { continue }
                $items += [pscustomobject]@{ Kind='script'; Name="$name/$($f.Name)"; Source=$f.FullName
                    Target=(Join-Path $Dest "agent-scripts\$name\$($f.Name)"); Version=$version }
            }
        }
    }
}

# 2) 커맨드 (필터 무관 항상 포함)
if (Test-Path "commands") {
    foreach ($f in Get-ChildItem "commands" -Filter *.md -File) {
        if ($f.Name -eq 'README.md') { continue }
        $items += [pscustomobject]@{ Kind='command'; Name=$f.BaseName; Source=$f.FullName
            Target=(Join-Path $Dest "commands\$($f.Name)"); Version='' }
    }
}

$report = foreach ($i in $items) {
    $status = if (-not (Test-Path $i.Target)) { 'NOT_DEPLOYED' }
              elseif ((Get-Sha256 $i.Source) -eq (Get-Sha256 $i.Target)) { 'IDENTICAL' }
              else { 'DIFFERENT' }
    [pscustomobject]@{ Kind=$i.Kind; Name=$i.Name; Version=$i.Version; Status=$status
                       Source=$i.Source; Target=$i.Target }
}

$report | Format-Table Kind, Name, Version, Status -AutoSize | Out-String | Write-Host

if ($Apply) {
    $failed = 0
    $targets = @($report | Where-Object { $_.Status -eq 'DIFFERENT' -or ($All -and $_.Status -eq 'NOT_DEPLOYED') })
    foreach ($t in $targets) {
        try {
            $dir = Split-Path $t.Target -Parent
            if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
            Copy-Item -Path $t.Source -Destination $t.Target -Force
            Write-Host "[SYNCED] $($t.Kind) $($t.Name)"
        } catch {
            Write-Host "[FAIL] $($t.Kind) $($t.Name): $_"
            $failed++
        }
    }
    if ($targets.Count -eq 0) { Write-Host "변경 없음 — 모두 동기화 상태입니다." }
    exit ([int]($failed -gt 0))
} else {
    $drift = @($report | Where-Object { $_.Status -ne 'IDENTICAL' }).Count
    Write-Host ("드리프트: {0}건 / 전체 {1}건" -f $drift, $report.Count)
    exit ([int]($drift -gt 0))
}
