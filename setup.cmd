@echo off
rem One-step setup of the ModelFlow plugins for Claude Code (Windows).
rem
rem   setup.cmd                 plugins from GitHub (IbHansen/modelflow-skill)
rem   setup.cmd local           plugins from this folder (a clone you can edit)
rem   ... modeller dev          also install modelflow-modeller / modelflow-dev
rem
rem   e.g.  setup.cmd modeller        setup.cmd local modeller dev
rem
rem It needs Miniforge and Claude Code, and Git for the GitHub source (without
rem Git it installs from this folder instead). It creates the conda environment
rem "modelflow" (ModelFlow + mcp) that the MCP server runs in, adds the
rem marketplace "modelflow" and installs the plugins at user scope.
setlocal EnableExtensions
set "HERE=%~dp0"
set "HERE=%HERE:~0,-1%"
set "SOURCE=IbHansen/modelflow-skill"
set "PLUGINS=modelflow-user"

:args
if "%~1"=="" goto argsdone
if /i "%~1"=="local"    set "SOURCE=%HERE%"
if /i "%~1"=="modeller" set "PLUGINS=%PLUGINS% modelflow-modeller"
if /i "%~1"=="dev"      set "PLUGINS=%PLUGINS% modelflow-dev"
shift
goto args
:argsdone

rem --- 1. Miniforge ---------------------------------------------------------
set "ROOT="
for %%R in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3") do (
  if not defined ROOT if exist "%%~R\condabin\conda.bat" set "ROOT=%%~R"
)
if defined ROOT goto haveconda
echo Miniforge was not found. Install it, then run setup.cmd again:
echo     winget install CondaForge.Miniforge3
echo or download the Windows installer from https://conda-forge.org/download/
exit /b 1
:haveconda
echo Miniforge: %ROOT%

rem --- 2. The conda environment "modelflow" ---------------------------------
set "ENVDIR=%ROOT%\envs\modelflow"
if exist "%ENVDIR%\python.exe" goto haveenv
echo Creating the conda environment "modelflow" (this takes a few minutes) ...
call "%ROOT%\condabin\conda.bat" create -y -n modelflow -c ibh -c conda-forge modelflow mcp
if errorlevel 1 goto failconda
goto envok

:haveenv
set "MISSING="
if not exist "%ENVDIR%\Lib\site-packages\modelclass.py" set "MISSING=modelflow"
if not exist "%ENVDIR%\Lib\site-packages\mcp" set "MISSING=%MISSING% mcp"
if not defined MISSING goto envok
echo Adding%MISSING% to the environment "modelflow" ...
call "%ROOT%\condabin\conda.bat" install -y -n modelflow -c ibh -c conda-forge %MISSING%
if errorlevel 1 goto failconda

:envok
echo Environment: %ENVDIR% (ModelFlow and mcp present)
if exist "%USERPROFILE%\.modelflow_mcp_env" (
  echo Note: %USERPROFILE%\.modelflow_mcp_env selects another environment for the
  echo MCP server. Delete that file to use "modelflow".
)

rem --- 3. Claude Code -------------------------------------------------------
where claude >nul 2>nul
if not errorlevel 1 goto haveclaude
rem The official installer puts claude.exe in .local\bin but may leave it off PATH.
if exist "%USERPROFILE%\.local\bin\claude.exe" (
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
  echo Claude Code found in %USERPROFILE%\.local\bin, which is not on your PATH.
  echo To start "claude" from any terminal, add that folder to your user PATH:
  echo     Settings - System - About - Advanced system settings - Environment Variables
  goto haveclaude
)
echo Claude Code was not found. Install it, open a new terminal and run setup.cmd again:
echo     powershell -c "irm https://claude.ai/install.ps1 | iex"
exit /b 1
:haveclaude

rem --- 4. Git (Claude Code clones a GitHub marketplace with git) ------------
if /i "%SOURCE%"=="%HERE%" goto market
where git >nul 2>nul
if not errorlevel 1 goto market
if exist "%ProgramFiles%\Git\cmd\git.exe" (
  set "PATH=%ProgramFiles%\Git\cmd;%PATH%"
  goto market
)
echo Git was not found. Claude Code needs Git to get the plugins from GitHub,
echo so they are installed from this folder instead: %HERE%
echo That works the same, but without automatic updates. To get those later:
echo     winget install Git.Git
echo then open a new terminal, run  claude plugin marketplace remove modelflow
echo and run setup.cmd again.
set "SOURCE=%HERE%"

rem --- 5. Marketplace and plugins -------------------------------------------
:market
echo Adding the marketplace "modelflow" from %SOURCE% ...
call claude plugin marketplace add "%SOURCE%"
if not errorlevel 1 goto marketok
echo The marketplace may already be added; updating it instead.
call claude plugin marketplace update modelflow
if errorlevel 1 goto failmarket
:marketok
set "FAILED="
for %%P in (%PLUGINS%) do (
  echo Installing %%P ...
  call claude plugin install %%P@modelflow
  if errorlevel 1 set "FAILED=%%P"
)
if defined FAILED goto failplugin

echo.
echo Done. Start Claude Code with "claude", type /mcp and check that
echo "plugin:modelflow-user:modelflow" is connected. Then try for example:
echo     load the PAK model and run a carbon tax of 30
exit /b 0

:failconda
echo conda failed - see the messages above.
exit /b 1

:failmarket
echo Could not add the marketplace from %SOURCE% - see the messages above.
exit /b 1

:failplugin
echo Installing %FAILED% failed - see the messages above.
exit /b 1
