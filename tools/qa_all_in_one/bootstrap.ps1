$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$launch = $env:FRONTLINE_QA_LAUNCH_DIR
if (-not $launch) { $launch = $PSScriptRoot }
$base = Join-Path $env:LOCALAPPDATA 'FrontlineQA'
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6)
$run = Join-Path $base $stamp
New-Item -ItemType Directory -Path $run -Force | Out-Null
$oldRuns = @(Get-ChildItem -LiteralPath $base -Directory | Where-Object { $_.FullName -ne $run } | Sort-Object LastWriteTime -Descending)
$repoUrl = 'https://github.com/TPollTech/Frontline-Survival.git'
$setup = Join-Path $run 'setup.log'
$rc = 1
function Probe([string]$exe,[string[]]$arguments) {
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $exe @arguments 2>&1
        $code = $LASTEXITCODE
        return [pscustomobject]@{Code=$code; Text=($output | Out-String).Trim()}
    } catch { return [pscustomobject]@{Code=-1; Text=$_.Exception.Message} }
}
function Native([string]$exe, [string[]]$arguments) {
    $ErrorActionPreference = 'Continue'
    & $exe @arguments 2>&1 | Out-Host
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "$exe failed: $code" }
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') + ';' + $env:Path
}
function Find-Git {
    $cmd = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in @("$env:ProgramFiles\Git\cmd\git.exe", "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe")) { if (Test-Path $p) { return $p } }
}
function Find-Python {
    # On Windows PowerShell 5.1, native stderr can become a terminating
    # error under Stop, even with 2>$null. A missing runtime is expected
    # during this optional probe; it must not abort dependency setup.
    $ErrorActionPreference = 'Continue'
    foreach ($candidate in @("$env:LOCALAPPDATA\Programs\Python\Python311\python.exe", "$env:ProgramFiles\Python311\python.exe")) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
    }
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        try {
            $p = & $launcher.Source -3.11 -c 'import sys; print(sys.executable)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $p -and (Test-Path -LiteralPath $p -PathType Leaf)) { return $p }
        } catch {
            Write-Host "Python 3.11 probe unavailable: $($_.Exception.Message)"
        }
    }
    return $null
}
function Install-Dependency([string]$id) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget) { throw 'Windows Package Manager (winget) unavailable. Install Git and Python 3.11 from their official sites, then rerun.' }
    Native $winget.Source @('install','--id',$id,'--exact','--source','winget','--accept-package-agreements','--accept-source-agreements')
    Refresh-Path
}
function Portable([string]$url,[string]$folder,[string]$filename,[string]$pattern,[string[]]$extra) {
    $candidates = @()
    $cmd = Get-Command $filename -ErrorAction SilentlyContinue
    if ($cmd) { $candidates += $cmd.Source }
    $candidates += $extra
    foreach ($d in $oldRuns) {
        $root = Join-Path $d.FullName $folder
        if (Test-Path -LiteralPath $root -PathType Container) {
            $candidates += @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter $filename -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
        }
    }
    foreach ($f in ($candidates | Select-Object -Unique)) {
        if (-not $f -or -not (Test-Path -LiteralPath $f -PathType Leaf)) { continue }
        $p = Probe $f @('--version')
        if ($p.Code -eq 0 -and $p.Text -match $pattern) {
            if ($folder -eq 'node' -and -not (Test-Path -LiteralPath (Join-Path (Split-Path $f) 'node_modules\npm\bin\npm-cli.js'))) { continue }
            Write-Host "Reusing $folder : $f"
            return $f
        }
    }
    $stage = Join-Path $run ($folder + '-staging')
    $dest = Join-Path $run $folder
    $archive = Join-Path $run ($folder + '.zip')
    Write-Host "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing
    Expand-Archive -LiteralPath $archive -DestinationPath $stage
    $exe = Get-ChildItem -LiteralPath $stage -Recurse -File -Filter $filename | Select-Object -First 1
    if (-not $exe) { throw "Missing $filename in archive" }
    $p = Probe $exe.FullName @('--version')
    if ($p.Code -ne 0 -or $p.Text -notmatch $pattern) { throw "Wrong $folder version: $($p.Text)" }
    Move-Item -LiteralPath $stage -Destination $dest
    $exe = Get-ChildItem -LiteralPath $dest -Recurse -File -Filter $filename | Select-Object -First 1
    Remove-Item -LiteralPath $archive
    return $exe.FullName
}
function Find-Repo([string]$git) {
    foreach ($d in $oldRuns) {
        $f = Join-Path $d.FullName 'source'
        if (-not (Test-Path -LiteralPath $f -PathType Container)) { continue }
        $p = Probe $git @('-C',$f,'remote','get-url','origin')
        if ($p.Code -eq 0 -and $p.Text -eq $repoUrl) { return $f }
    }
}
function Find-Venv {
    foreach ($d in $oldRuns) {
        $py = Join-Path $d.FullName 'venv\Scripts\python.exe'
        if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { continue }
        $p = Probe $py @('-c','import sys,struct,numpy,trimesh,scipy; print("QA_READY" if sys.version_info[:2]==(3,11) and struct.calcsize("P")==8 and (numpy.__version__,trimesh.__version__,scipy.__version__)==("2.2.6","4.11.1","1.15.3") else "wrong")')
        if ($p.Code -eq 0 -and $p.Text -eq 'QA_READY') { return $py }
    }
}
function Find-ReviewedSummary {
    foreach ($d in $oldRuns) {
        $f = Join-Path $d.FullName 'evidence\summary.json'
        if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { continue }
        if ((Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant() -eq '3b574ae73109cea34ac16fb48a389a5880d85143f7123c892fa469d7a64a4ffc') { return $f }
    }
}
Start-Transcript -Path $setup | Out-Null
try {
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Windows x64 required.' }
    Refresh-Path
    $git = Find-Git
    if (-not $git) { Install-Dependency 'Git.Git'; $git = Find-Git }
    if (-not $git) { throw 'Git not found after installation' }
    $env:Path = (Split-Path $git) + ';' + $env:Path
    $py = Find-Venv
    if (-not $py) {
        $python = Find-Python
        if (-not $python) { Install-Dependency 'Python.Python.3.11'; $python = Find-Python }
        if (-not $python) { throw 'Python 3.11 not found after installation' }
        $p = Probe $python @('-c','import sys,struct; print("QA311" if sys.version_info[:2]==(3,11) and struct.calcsize("P")==8 else "wrong")')
        if ($p.Code -ne 0 -or $p.Text -ne 'QA311') { throw 'Python 3.11 x64 required' }
        $venv = Join-Path $run 'venv'
        Native $python @('-m','venv',$venv)
        $py = Join-Path $venv 'Scripts\python.exe'
        Native $py @('-m','pip','install','numpy==2.2.6','trimesh==4.11.1','scipy==1.15.3')
    }
    Write-Host "Using Python: $py"
    $store = Find-Repo $git
    $repo = Join-Path $run 'source'
    if (-not $store) {
        Native $git @('-c','core.autocrlf=false','clone','--no-checkout','--single-branch','--branch','main',$repoUrl,$repo)
        $store = $repo
    }
    Native $git @('-C',$store,'fetch','--no-tags','origin','main')
    $pin = Join-Path $launch 'REVISION.txt'
    if (Test-Path -LiteralPath $pin -PathType Leaf) {
        $rev = (Get-Content -LiteralPath $pin -Raw).Trim()
    } else {
        $p = Probe $git @('-C',$store,'rev-parse','FETCH_HEAD')
        if ($p.Code -ne 0) { throw $p.Text }
        $rev = $p.Text
    }
    if ($rev -notmatch '^[0-9a-f]{40}$') { throw 'Invalid pinned revision' }
    Native $git @('-C',$store,'merge-base','--is-ancestor',$rev,'FETCH_HEAD')
    if ($store -eq $repo) {
        Native $git @('-C',$repo,'-c','core.autocrlf=false','checkout','--detach',$rev)
    } else {
        Native $git @('-C',$store,'-c','core.autocrlf=false','worktree','add','--detach',$repo,$rev)
    }
    Write-Host "QA revision: $rev"
    $node = Portable 'https://nodejs.org/dist/v22.16.0/node-v22.16.0-win-x64.zip' 'node' 'node.exe' '(?m)^v22\.16\.0$' @("$env:ProgramFiles\nodejs\node.exe")
    $npm = Join-Path (Split-Path $node) 'node_modules\npm\bin\npm-cli.js'
    if (-not (Test-Path $npm)) { throw 'Portable npm missing.' }
    $godot = Portable 'https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_win64.exe.zip' 'godot' 'Godot_v4.4.1-stable_win64_console.exe' '(?m)^4\.4\.1\.stable\.official' @()
    $env:Path = (Split-Path $node) + ';' + (Split-Path $godot) + ';' + $env:Path
    try {
        $blender = Portable 'https://download.blender.org/release/Blender3.0/blender-3.0.1-windows-x64.zip' 'blender' 'blender.exe' '(?m)^Blender 3\.0\.1(\s|$)' @("$env:ProgramFiles\Blender Foundation\Blender 3.0\blender.exe")
        $env:FRONTLINE_BLENDER = $blender
        Write-Host "Using Blender: $blender"
    } catch { Write-Warning "Blender unavailable; required Blender tests may fail: $_" }
    $browserCache = Join-Path $base 'browsers'
    foreach ($d in $oldRuns) {
        $f = Join-Path $d.FullName 'work\browsers'
        if (Test-Path -LiteralPath $f -PathType Container) { $browserCache = $f; break }
    }
    $env:PLAYWRIGHT_BROWSERS_PATH = $browserCache
    $previous = Find-ReviewedSummary
    $qaArgs = @((Join-Path $repo 'tools\qa_all_in_one\run.py'),'--root',$repo,'--out',(Join-Path $run 'evidence'),'--work',(Join-Path $run 'work'),'--godot',$godot,'--node',$node,'--npm',$npm)
    if ($previous) {
        Write-Host 'Reviewed local evidence found; runner checks whether LOD can be deferred.'
        $qaArgs += @('--previous-summary',$previous)
    } else { Write-Host 'No reviewed local evidence; running full QA on this computer.' }
    $ErrorActionPreference = 'Continue'
    & $py @qaArgs 2>&1 | Out-Host
    $rc = $LASTEXITCODE
    $ErrorActionPreference = 'Stop'
} catch { Write-Host "QA setup/run failed: $_" -ForegroundColor Red }
finally { Stop-Transcript | Out-Null }
try {
    $diagnostic = Join-Path $launch ('DIAGNOSTICO-' + $stamp + '.txt')
    "Frontline QA exit code: $rc" | Set-Content -LiteralPath $diagnostic -Encoding UTF8
    if (Test-Path -LiteralPath $setup) {
        '=== SETUP (last 100 lines) ===' | Add-Content -LiteralPath $diagnostic -Encoding UTF8
        Get-Content -LiteralPath $setup -Tail 100 | Add-Content -LiteralPath $diagnostic -Encoding UTF8
    }
    $evidence = Join-Path $run 'evidence'
    $summary = Join-Path $evidence 'summary.json'
    if (Test-Path -LiteralPath $summary) {
        '=== SUMMARY ===' | Add-Content -LiteralPath $diagnostic -Encoding UTF8
        Get-Content -LiteralPath $summary -Raw | Add-Content -LiteralPath $diagnostic -Encoding UTF8
        $data = Get-Content -LiteralPath $summary -Raw | ConvertFrom-Json
        foreach ($step in $data.steps) {
            if ($step.status -ne 'failed' -or $step.log -notmatch '^[A-Za-z0-9_.-]+\.log$') { continue }
            $log = Join-Path $evidence $step.log
            if (Test-Path -LiteralPath $log -PathType Leaf) {
                ('=== ' + $step.log + ' (last 100 lines) ===') | Add-Content -LiteralPath $diagnostic -Encoding UTF8
                Get-Content -LiteralPath $log -Tail 100 | Add-Content -LiteralPath $diagnostic -Encoding UTF8
            }
        }
    }
    $result = Join-Path $run 'evidence.zip'
    if (Test-Path -LiteralPath $result) {
        Copy-Item -LiteralPath $result -Destination (Join-Path $launch ('RESULTADOS-' + $stamp + '.zip'))
    }
    Write-Host "Send first: $diagnostic" -ForegroundColor Cyan
    Write-Host "Full evidence: $run"
} catch { Write-Host "Export failed: $_. Original files: $run" }
Write-Host "Exit code: $rc. Automated QA is not visual approval."
exit $rc
