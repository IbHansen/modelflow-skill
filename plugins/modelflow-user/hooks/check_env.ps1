# SessionStart hook of the modelflow-user plugin. Tells Claude when the
# environment for the modelflow MCP server is missing or incomplete, so Claude
# can tell the user. Prints nothing when everything is in place.
$ErrorActionPreference = 'SilentlyContinue'
$cfg   = Join-Path $env:USERPROFILE '.modelflow_mcp_env'
$roots = "$env:USERPROFILE\miniforge3", "$env:LOCALAPPDATA\miniforge3", "$env:ProgramData\miniforge3"
$pre   = 'ModelFlow plugin (modelflow MCP server):'

if (Test-Path $cfg) {
    $envdir = (Get-Content $cfg -TotalCount 1).Trim()
    $how    = "the environment selected in $cfg"
} else {
    $root = $roots | Where-Object { Test-Path (Join-Path $_ 'python.exe') } | Select-Object -First 1
    if (-not $root) {
        Write-Output "$pre Miniforge is not installed, so the modelflow MCP tools can not start. If the user wants to work with ModelFlow, offer to guide them through installing Miniforge and then: conda create -n modelflow -c ibh -c conda-forge modelflow mcp  (see the mf-getting-started skill). Afterwards the server is started with /mcp -> modelflow -> Reconnect."
        exit 0
    }
    $envdir = Join-Path $root 'envs\modelflow'
    $how    = "the default environment 'modelflow'"
}

if (-not (Test-Path (Join-Path $envdir 'python.exe'))) {
    Write-Output "$pre $how ($envdir) does not exist, so the modelflow MCP tools can not start. If the user wants to work with ModelFlow, offer: conda create -n modelflow -c ibh -c conda-forge modelflow mcp  or, if they already have an environment with ModelFlow, delete $cfg or point it at that environment's folder. Then /mcp -> modelflow -> Reconnect."
    exit 0
}

$sp = Join-Path $envdir 'Lib\site-packages'
$missing = @()
if (-not (Test-Path (Join-Path $sp 'modelclass.py'))) { $missing += 'modelflow' }
if (-not (Test-Path (Join-Path $sp 'mcp')))           { $missing += 'mcp' }
if ($missing) {
    Write-Output "$pre $how ($envdir) lacks $($missing -join ' and '), so the modelflow MCP tools will not work. If the user wants to work with ModelFlow, offer: conda install -p `"$envdir`" -c ibh -c conda-forge $($missing -join ' ')  then /mcp -> modelflow -> Reconnect."
}
exit 0
