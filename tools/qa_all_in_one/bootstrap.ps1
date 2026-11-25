$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$base = Join-Path $env:LOCALAPPDATA 'FrontlineQA'
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6)
$run = Join-Path $base $stamp
New-Item -ItemType Directory -Path $run -Force | Out-Null
$setup = Join-Path $run 'setup.log'
$rc = 1
function Native([string]$exe, [string[]]$arguments) {
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) { throw "$exe failed: $LASTEXITCODE" }
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
function Portable([string]$url,[string]$folder,[string]$filename) {
    $dest = Join-Path $run $folder
    $archive = Join-Path $run ($folder + '.zip')
    Write-Host "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing
    Expand-Archive -LiteralPath $archive -DestinationPath $dest
    $exe = Get-ChildItem -Path $dest -Recurse -File -Filter $filename | Select-Object -First 1
    if (-not $exe) { throw "Missing $filename in archive" }
    Remove-Item -LiteralPath $archive
    return $exe.FullName
}
Start-Transcript -Path $setup | Out-Null
try {
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Windows x64 required.' }
    $rev = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'REVISION.txt') -Raw).Trim()
    if ($rev -notmatch '^[0-9a-f]{40}$') { throw 'Invalid pinned revision.' }
    $git = Find-Git
    if (-not $git) { Install-Dependency 'Git.Git'; $git = Find-Git }
    $python = Find-Python
    if (-not $python) {
        Write-Host 'Python 3.11 not found; installing via Windows Package Manager.'
        Install-Dependency 'Python.Python.3.11'
        $python = Find-Python
    }
    if (-not $git -or -not $python) { throw 'Git or Python not found after installation.' }
    $env:Path = (Split-Path $git) + ';' + $env:Path
    $repo = Join-Path $run 'source'
    Native $git @('clone','--no-checkout','--single-branch','--branch','main','https://github.com/TPollTech/Frontline-Survival.git',$repo)
    Native $git @('-C',$repo,'merge-base','--is-ancestor',$rev,'origin/main')
    Native $git @('-C',$repo,'checkout','--detach',$rev)
    $node = Portable 'https://nodejs.org/dist/v22.16.0/node-v22.16.0-win-x64.zip' 'node' 'node.exe'
    $npm = Join-Path (Split-Path $node) 'node_modules\npm\bin\npm-cli.js'
    if (-not (Test-Path $npm)) { throw 'Portable npm missing.' }
    $godot = Portable 'https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_win64.exe.zip' 'godot' 'Godot_v4.4.1-stable_win64_console.exe'
    $env:Path = (Split-Path $node) + ';' + (Split-Path $godot) + ';' + $env:Path
    try {
        $blender = Portable 'https://download.blender.org/release/Blender3.0/blender-3.0.1-windows-x64.zip' 'blender' 'blender.exe'
        $env:FRONTLINE_BLENDER = $blender
        Native $blender @('--version')
    } catch { Write-Warning "Blender unavailable; required Blender tests may fail: $_" }
    Native $node @('--version')
    Native $godot @('--version')
    Native $python @('--version')
    $venv = Join-Path $run 'venv'
    Native $python @('-m','venv',$venv)
    $py = Join-Path $venv 'Scripts\python.exe'
    Native $py @('-m','pip','install','numpy==2.2.6','trimesh==4.11.1','scipy==1.15.3')
    & $py (Join-Path $repo 'tools\qa_all_in_one\run.py') --root $repo --out (Join-Path $run 'evidence') --work (Join-Path $run 'work') --godot $godot --node $node --npm $npm
    $rc = $LASTEXITCODE
} catch { Write-Host "QA setup/run failed: $_" -ForegroundColor Red }
finally { Stop-Transcript | Out-Null }
try {
    $result = Join-Path $run 'evidence.zip'
    $destination = Join-Path $PSScriptRoot ("RESULTADOS-"+$stamp+".zip")
    if (Test-Path $result) { Compress-Archive -LiteralPath @($result,$setup) -DestinationPath $destination }
    else { Compress-Archive -LiteralPath $setup -DestinationPath $destination }
    Write-Host "Send this ZIP to ChatGPT: $destination" -ForegroundColor Cyan
} catch { Write-Host "Could not export beside launcher. Evidence and setup log: $run" }
Write-Host "Exit code: $rc. A successful automated run is not visual approval."
exit $rc
