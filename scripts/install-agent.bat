@echo off
setlocal enabledelayedexpansion

:: Custom Subagents Installer for Claude Code
:: This script copies selected agent files to ~/.claude/agents directory

echo ========================================
echo Custom Subagents Installer
echo ========================================
echo.

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
:: Go up one level to get repository root
set "REPO_ROOT=%SCRIPT_DIR%.."

:: Set Claude agents directory (user home)
set "CLAUDE_AGENTS_DIR=%USERPROFILE%\.claude\agents"

echo Script location: %SCRIPT_DIR%
echo Repository root: %REPO_ROOT%
echo Target directory: %CLAUDE_AGENTS_DIR%
echo.

:: Check if agents directory exists in repo
if not exist "%REPO_ROOT%\agents\" (
    echo Error: 'agents' directory not found at %REPO_ROOT%\agents
    echo Please ensure the script is in the 'scripts' folder of the repository.
    pause
    exit /b 1
)

:: Create .claude/agents directory in user home if it doesn't exist
if not exist "%USERPROFILE%\.claude\" mkdir "%USERPROFILE%\.claude"
if not exist "%CLAUDE_AGENTS_DIR%\" mkdir "%CLAUDE_AGENTS_DIR%"
echo [OK] %CLAUDE_AGENTS_DIR% is ready
echo.

:: Display available agents
echo Available agents:
echo ================
echo.

set count=0
for /d %%C in ("%REPO_ROOT%\agents\*") do (
    for /d %%A in ("%%C\*") do (
        set /a count+=1
        set "agent[!count!]=%%A"
        for %%F in ("%%A\agent.json") do (
            if exist "%%F" (
                :: Extract agent name from path
                for %%N in (%%A) do set agentname=%%~nxN
                echo !count!. !agentname!
                :: Show description if available (simplified - just show the path)
                echo    Path: %%A
                echo.
            )
        )
    )
)

if %count%==0 (
    echo No agents found in the agents directory.
    pause
    exit /b 1
)

echo ================
echo.
echo Enter the numbers of agents to install (comma-separated, e.g., 1,2)
echo Or press 'A' to install all agents
echo Or press 'Q' to quit
echo.
set /p selection="Your choice: "

:: Handle quit
if /i "%selection%"=="Q" (
    echo Installation cancelled.
    exit /b 0
)

:: Handle install all
if /i "%selection%"=="A" (
    echo.
    echo Installing all agents...
    echo.

    for /d %%C in ("%REPO_ROOT%\agents\*") do (
        for /d %%A in ("%%C\*") do (
            for %%N in (%%A) do set agentname=%%~nxN
            if exist "%%A\!agentname!.md" (
                echo Copying !agentname!.md to %CLAUDE_AGENTS_DIR%\
                copy /Y "%%A\!agentname!.md" "%CLAUDE_AGENTS_DIR%\" >nul
                if !errorlevel! equ 0 (
                    echo [OK] !agentname! installed successfully
                ) else (
                    echo [ERROR] Failed to install !agentname!
                )
            ) else (
                echo [WARNING] !agentname!.md not found in %%A
            )
            echo.
        )
    )

    goto :done
)

:: Handle specific selection
echo.
echo Installing selected agents...
echo.

:: Parse comma-separated input
set "selection=!selection: =!"
set "selection=!selection:,= !"

for %%S in (%selection%) do (
    set num=%%S
    set agentpath=!agent[%%S]!

    if "!agentpath!"=="" (
        echo [ERROR] Invalid selection: %%S
    ) else (
        for %%N in (!agentpath!) do set agentname=%%~nxN

        if exist "!agentpath!\!agentname!.md" (
            echo Copying !agentname!.md to %CLAUDE_AGENTS_DIR%\
            copy /Y "!agentpath!\!agentname!.md" "%CLAUDE_AGENTS_DIR%\" >nul
            if !errorlevel! equ 0 (
                echo [OK] !agentname! installed successfully
            ) else (
                echo [ERROR] Failed to install !agentname!
            )
        ) else (
            echo [ERROR] !agentname!.md not found in !agentpath!
        )
        echo.
    )
)

:done
echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Agent files have been copied to: %CLAUDE_AGENTS_DIR%
echo You can now use these agents in Claude Code.
echo.
pause
