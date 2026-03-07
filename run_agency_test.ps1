# THE AGENCY - 28 SKILL ORCHESTRATION SCRIPT (Windows native equivalent to Makefile)
# This script sequences the Virtual IT Team using a local Ollama instance in PowerShell.

$Model = "llama3.2"
$OutDir = "output"
$PlanDir = "$OutDir/1_planning"
$DesignDir = "$OutDir/2_design"
$ArchDir = "$OutDir/3_architecture"

$UserRequirement = "I want a new feature for our e-commerce site that recommends products to users based on their browsing history using AI."

Write-Host "Setting up directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $OutDir, $PlanDir, $DesignDir, $ArchDir | Out-Null

function Run-OllamaTask {
    param(
        [string]$SkillFile,
        [string]$Context,
        [string]$Task,
        [string]$OutputFile,
        [string]$StepName
    )
    Write-Host "🚀 $StepName" -ForegroundColor Yellow
    $SkillContent = Get-Content -Path "skills\$SkillFile" -Raw
    $Prompt = "$SkillContent`n`nCONTEXT: $Context`n`nTASK: $Task"
    
    # Run Ollama natively by piping the prompt into stdin to avoid flag parsing errors
    $Prompt | ollama run $Model | Out-File -FilePath $OutputFile -Encoding utf8
    Write-Host "   ✅ Saved to $OutputFile`n" -ForegroundColor Green
}

# --- Fast Test (First 3 Skills to verify pipeline works) ---

# 1. Project Manager
Run-OllamaTask `
    -SkillFile "project_manager\SKILL.md" `
    -Context "New Request" `
    -Task "Route this feature request and generate an initial execution plan: $UserRequirement" `
    -OutputFile "$PlanDir\1_pm_init.md" `
    -StepName "1/3 Project Manager: Initializing..."

# 2. CMO Analyst
$PMOutput = Get-Content -Path "$PlanDir\1_pm_init.md" -Raw
Run-OllamaTask `
    -SkillFile "cmo_analyst\SKILL.md" `
    -Context "$UserRequirement`n`nProject Manager Plan:`n$PMOutput" `
    -Task "Define the digital twin constraints and necessary documentation folders for this new feature." `
    -OutputFile "$PlanDir\2_cmo_discovery.md" `
    -StepName "2/3 CMO Analyst: Discovery..."

# 3. UX/UI Designer
$CMOOutput = Get-Content -Path "$PlanDir\2_cmo_discovery.md" -Raw
Run-OllamaTask `
    -SkillFile "ux_ui_designer\SKILL.md" `
    -Context "$UserRequirement`n`nCMO Docs:`n$CMOOutput" `
    -Task "Describe the wireframe flow, UI components, and accessibility requirements for this feature." `
    -OutputFile "$DesignDir\3_ux_wireframe.md" `
    -StepName "3/3 UX/UI Designer: Wireframing..."

Write-Host "🎉 Fast Pipeline Complete! Check the '$OutDir' folder for the artifacts." -ForegroundColor Cyan
