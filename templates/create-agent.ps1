# Custom Subagent Creator Script for Windows (PowerShell)
# Usage: .\create-agent.ps1

param()

# Set error action preference
$ErrorActionPreference = "Stop"

# Available categories
$categories = @("frontend", "backend", "devops", "documentation", "business", "fullstack")

# Colors
function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [Parameter(Mandatory=$false)]
        [string]$ForegroundColor = "White"
    )
    Write-Host $Message -ForegroundColor $ForegroundColor
}

# Header
Write-ColorOutput "==================================" -ForegroundColor Cyan
Write-ColorOutput "  Custom Subagent Creator" -ForegroundColor Cyan
Write-ColorOutput "==================================" -ForegroundColor Cyan
Write-Host ""

# Function to display categories
function Show-Categories {
    Write-ColorOutput "Available categories:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $categories.Count; $i++) {
        Write-Host "  $($i + 1). $($categories[$i])"
    }
}

# Get agent name
$agentName = Read-Host "Enter agent name (e.g., 'my-custom-agent')"
if ([string]::IsNullOrWhiteSpace($agentName)) {
    Write-ColorOutput "Error: Agent name cannot be empty" -ForegroundColor Red
    exit 1
}

# Get category
Write-Host ""
Show-Categories
$categoryIndex = Read-Host "Select category (1-$($categories.Count))"

if (-not ($categoryIndex -match '^\d+$') -or [int]$categoryIndex -lt 1 -or [int]$categoryIndex -gt $categories.Count) {
    Write-ColorOutput "Error: Invalid category selection" -ForegroundColor Red
    exit 1
}

$category = $categories[[int]$categoryIndex - 1]

# Get other details
Write-Host ""
$agentDescription = Read-Host "Enter agent description"
$agentType = Read-Host "Enter agent type (e.g., 'generator', 'analyzer', 'optimizer')"
$author = Read-Host "Enter author name"

# Create agent directory
$agentDir = Join-Path -Path ".\agents" -ChildPath "$category\$agentName"

if (Test-Path $agentDir) {
    Write-ColorOutput "Error: Agent directory already exists: $agentDir" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-ColorOutput "Creating agent directory: $agentDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $agentDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $agentDir "examples") -Force | Out-Null

# Copy and process templates
Write-ColorOutput "Generating files from templates..." -ForegroundColor Yellow

# Function to replace placeholders
function Replace-Placeholders {
    param(
        [string]$Content,
        [hashtable]$Replacements
    )

    foreach ($key in $Replacements.Keys) {
        $Content = $Content -replace [regex]::Escape($key), $Replacements[$key]
    }

    return $Content
}

# Define replacements
$replacements = @{
    "{{AGENT_NAME}}" = $agentName
    "{{AGENT_TYPE}}" = $agentType
    "{{AGENT_DESCRIPTION}}" = $agentDescription
    "{{CATEGORY}}" = $category
    "{{AUTHOR}}" = $author
    "{{CAPABILITY_1}}" = "Capability 1"
    "{{CAPABILITY_2}}" = "Capability 2"
    "{{CAPABILITY_3}}" = "Capability 3"
    "{{TAG_1}}" = "tag1"
    "{{TAG_2}}" = "tag2"
    "{{TAG_3}}" = "tag3"
    "{{EXAMPLE_TITLE}}" = "Example Usage"
    "{{EXAMPLE_DESCRIPTION}}" = "Basic example"
    "{{EXAMPLE_INPUT}}" = "Sample input"
    "{{EXAMPLE_OUTPUT}}" = "Sample output"
    "{{EXAMPLE_USAGE}}" = "Add your example here"
    "{{ADVANCED_EXAMPLE}}" = "Add your advanced example here"
    "{{INPUT_FORMAT}}" = "Describe input format"
    "{{OUTPUT_FORMAT}}" = "Describe output format"
    "{{BEST_PRACTICE_1}}" = "Best practice 1"
    "{{BEST_PRACTICE_2}}" = "Best practice 2"
    "{{BEST_PRACTICE_3}}" = "Best practice 3"
    "{{LIMITATION_1}}" = "Limitation 1"
    "{{LIMITATION_2}}" = "Limitation 2"
    "{{AGENT_PURPOSE}}" = "your custom purpose"
    "{{EXPERTISE_1}}" = "Expertise area 1"
    "{{EXPERTISE_2}}" = "Expertise area 2"
    "{{EXPERTISE_3}}" = "Expertise area 3"
    "{{OBJECTIVE_1}}" = "Objective 1"
    "{{OBJECTIVE_2}}" = "Objective 2"
    "{{OBJECTIVE_3}}" = "Objective 3"
    "{{ANALYSIS_STEP_1}}" = "Analysis step 1"
    "{{ANALYSIS_STEP_2}}" = "Analysis step 2"
    "{{EXECUTION_STEP_1}}" = "Execution step 1"
    "{{EXECUTION_STEP_2}}" = "Execution step 2"
    "{{VALIDATION_STEP_1}}" = "Validation step 1"
    "{{VALIDATION_STEP_2}}" = "Validation step 2"
    "{{OUTPUT_STANDARD_1}}" = "Output standard 1"
    "{{OUTPUT_STANDARD_2}}" = "Output standard 2"
    "{{OUTPUT_STANDARD_3}}" = "Output standard 3"
    "{{ACCURACY_GUIDELINE}}" = "Accuracy guideline"
    "{{COMPLETENESS_GUIDELINE}}" = "Completeness guideline"
    "{{CONSISTENCY_GUIDELINE}}" = "Consistency guideline"
    "{{ERROR_HANDLING_1}}" = "Error handling step 1"
    "{{ERROR_HANDLING_2}}" = "Error handling step 2"
    "{{ERROR_HANDLING_3}}" = "Error handling step 3"
    "{{CONSTRAINT_1}}" = "Constraint 1"
    "{{CONSTRAINT_2}}" = "Constraint 2"
    "{{CONSTRAINT_3}}" = "Constraint 3"
    "{{SUCCESS_CRITERIA_1}}" = "Success criteria 1"
    "{{SUCCESS_CRITERIA_2}}" = "Success criteria 2"
    "{{SUCCESS_CRITERIA_3}}" = "Success criteria 3"
}

# Process agent.json
$agentJsonTemplate = Get-Content ".\templates\agent-template\agent.json.template" -Raw -Encoding UTF8
$agentJsonContent = Replace-Placeholders -Content $agentJsonTemplate -Replacements $replacements
Set-Content -Path (Join-Path $agentDir "agent.json") -Value $agentJsonContent -Encoding UTF8

# Process README.md
$readmeTemplate = Get-Content ".\templates\agent-template\README.md.template" -Raw -Encoding UTF8
$readmeContent = Replace-Placeholders -Content $readmeTemplate -Replacements $replacements
Set-Content -Path (Join-Path $agentDir "README.md") -Value $readmeContent -Encoding UTF8

# Process prompt.md
$promptTemplate = Get-Content ".\templates\agent-template\prompt.md.template" -Raw -Encoding UTF8
$promptContent = Replace-Placeholders -Content $promptTemplate -Replacements $replacements
Set-Content -Path (Join-Path $agentDir "prompt.md") -Value $promptContent -Encoding UTF8

# Create example file
$exampleContent = @"
# Example 1: Basic Usage

## Input
``````
Add your example input here
``````

## Process
1. Step 1
2. Step 2
3. Step 3

## Output
``````
Add your example output here
``````
"@

Set-Content -Path (Join-Path $agentDir "examples\example1.md") -Value $exampleContent -Encoding UTF8

Write-Host ""
Write-ColorOutput "✓ Agent created successfully!" -ForegroundColor Green
Write-Host ""
Write-ColorOutput "Agent Details:" -ForegroundColor Cyan
Write-Host "  Name: $agentName"
Write-Host "  Category: $category"
Write-Host "  Type: $agentType"
Write-Host "  Location: $agentDir"
Write-Host ""
Write-ColorOutput "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit $agentDir\prompt.md to define agent behavior"
Write-Host "  2. Update $agentDir\README.md with detailed documentation"
Write-Host "  3. Customize $agentDir\agent.json with specific tools and capabilities"
Write-Host "  4. Add usage examples in $agentDir\examples\"
Write-Host ""
Write-ColorOutput "Happy coding!" -ForegroundColor Green
