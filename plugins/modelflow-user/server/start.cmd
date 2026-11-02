@echo off
rem Start the ModelFlow MCP server with the python of the selected conda
rem environment: the full path saved in %USERPROFILE%\.modelflow_mcp_env by
rem the select_environment tool, else the Miniforge environment "modelflow".
rem Errors go to stderr (stdout is the MCP protocol).
setlocal
set "ENVDIR="
if exist "%USERPROFILE%\.modelflow_mcp_env" set /p ENVDIR=<"%USERPROFILE%\.modelflow_mcp_env"
if defined ENVDIR goto run

for %%R in ("%USERPROFILE%\miniforge3" "%LOCALAPPDATA%\miniforge3" "%ProgramData%\miniforge3") do (
  if exist "%%~R\envs\modelflow\python.exe" if not defined ENVDIR set "ENVDIR=%%~R\envs\modelflow"
)
if not defined ENVDIR (
  echo ModelFlow MCP: no Miniforge environment "modelflow" found. 1>&2
  exit /b 1
)

:run
if not exist "%ENVDIR%\python.exe" (
  echo ModelFlow MCP: "%ENVDIR%" has no python.exe. 1>&2
  exit /b 1
)
set "PATH=%ENVDIR%;%ENVDIR%\Library\mingw-w64\bin;%ENVDIR%\Library\usr\bin;%ENVDIR%\Library\bin;%ENVDIR%\Scripts;%PATH%"
"%ENVDIR%\python.exe" -X utf8 "%~dp0modelflow_mcp.py"
