#!/usr/bin/env pwsh
# Custom Subagents Installer for Claude Code
# This script copies selected agent files to .claude/agents directory

function Show-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Custom Subagents Installer" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Get-AvailableAgents {
    $agents = @()
    $categories = Get-ChildItem -Path "agents" -Directory

    foreach ($category in $categories) {
        $agentDirs = Get-ChildItem -Path $category.FullName -Directory

        foreach ($agentDir in $agentDirs) {
            $agentJsonPath = Join-Path $agentDir.FullName "agent.json"

            if (Test-Path $agentJsonPath) {
                $agentJson = Get-Content $agentJsonPath | ConvertFrom-Json

                $agents += [PSCustomObject]@{
                    Name = $agentDir.Name
                    Category = $category.Name
                    Path = $agentDir.FullName
                    Description = $agentJson.description
                    MdFile = Join-Path $agentDir.FullName "$($agentDir.Name).md"
                }
            }
        }
    }

    return $agents
}

function Show-AgentList {
    param (
        [Parameter(Mandatory=$true)]
        [array]$Agents
    )

    Write-Host "Available agents:" -ForegroundColor Yellow
    Write-Host "================" -ForegroundColor Yellow
    Write-Host ""

    for ($i = 0; $i -lt $Agents.Count; $i++) {
        $agent = $Agents[$i]
        Write-Host "$($i + 1). " -NoNewline -ForegroundColor Green
        Write-Host "$($agent.Name)" -ForegroundColor White
        Write-Host "   Category: " -NoNewline -ForegroundColor Gray
        Write-Host "$($agent.Category)" -ForegroundColor Cyan
        Write-Host "   Description: " -NoNewline -ForegroundColor Gray
        Write-Host "$($agent.Description)" -ForegroundColor White
        Write-Host ""
    }

    Write-Host "================" -ForegroundColor Yellow
    Write-Host ""
}

function Install-Agent {
    param (
        [Parameter(Mandatory=$true)]
        [PSCustomObject]$Agent,

        [Parameter(Mandatory=$true)]
        [string]$DestinationDir
    )

    if (Test-Path $Agent.MdFile) {
        $destFile = Join-Path $DestinationDir "$($Agent.Name).md"

        try {
            Copy-Item -Path $Agent.MdFile -Destination $destFile -Force
            Write-Host "[OK] " -NoNewline -ForegroundColor Green
            Write-Host "$($Agent.Name) installed successfully"
            return $true
        }
        catch {
            Write-Host "[ERROR] " -NoNewline -ForegroundColor Red
            Write-Host "Failed to install $($Agent.Name): $_"
            return $false
        }
    }
    else {
        Write-Host "[WARNING] " -NoNewline -ForegroundColor Yellow
        Write-Host "$($Agent.Name).md not found at $($Agent.MdFile)"
        return $false
    }
}

# Main Script
Clear-Host
Show-Header

# Check if we're in the correct directory
if (-not (Test-Path "agents")) {
    Write-Host "Error: 'agents' directory not found." -ForegroundColor Red
    Write-Host "Please run this script from the custom_subagents repository root." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create .claude/agents directory if it doesn't exist
$claudeAgentsDir = ".claude/agents"
if (-not (Test-Path ".claude")) {
    New-Item -ItemType Directory -Path ".claude" | Out-Null
}
if (-not (Test-Path $claudeAgentsDir)) {
    New-Item -ItemType Directory -Path $claudeAgentsDir | Out-Null
}

Write-Host "[OK] .claude/agents directory is ready" -ForegroundColor Green
Write-Host ""

# Get available agents
$agents = Get-AvailableAgents

if ($agents.Count -eq 0) {
    Write-Host "No agents found in the agents directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Display agents
Show-AgentList -Agents $agents

# Get user selection
Write-Host "Enter the numbers of agents to install (comma-separated, e.g., 1,2)" -ForegroundColor Cyan
Write-Host "Or press 'A' to install all agents" -ForegroundColor Cyan
Write-Host "Or press 'Q' to quit" -ForegroundColor Cyan
Write-Host ""

$selection = Read-Host "Your choice"

if ($selection -eq 'Q' -or $selection -eq 'q') {
    Write-Host "Installation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Installing agents..." -ForegroundColor Cyan
Write-Host ""

$installedCount = 0
$failedCount = 0

if ($selection -eq 'A' -or $selection -eq 'a') {
    # Install all agents
    foreach ($agent in $agents) {
        if (Install-Agent -Agent $agent -DestinationDir $claudeAgentsDir) {
            $installedCount++
        }
        else {
            $failedCount++
        }
    }
}
else {
    # Install selected agents
    $numbers = $selection -split ',' | ForEach-Object { $_.Trim() }

    foreach ($num in $numbers) {
        if ($num -match '^\d+$') {
            $index = [int]$num - 1

            if ($index -ge 0 -and $index -lt $agents.Count) {
                if (Install-Agent -Agent $agents[$index] -DestinationDir $claudeAgentsDir) {
                    $installedCount++
                }
                else {
                    $failedCount++
                }
            }
            else {
                Write-Host "[ERROR] Invalid selection: $num" -ForegroundColor Red
                $failedCount++
            }
        }
        else {
            Write-Host "[ERROR] Invalid input: $num" -ForegroundColor Red
            $failedCount++
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Successfully installed: " -NoNewline -ForegroundColor Green
Write-Host "$installedCount agent(s)"
if ($failedCount -gt 0) {
    Write-Host "Failed: " -NoNewline -ForegroundColor Red
    Write-Host "$failedCount agent(s)"
}
Write-Host ""
Write-Host "Agent files have been copied to: " -NoNewline
Write-Host $claudeAgentsDir -ForegroundColor Yellow
Write-Host "You can now use these agents in Claude Code." -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
