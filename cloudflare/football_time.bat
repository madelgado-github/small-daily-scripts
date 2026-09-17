@echo off
setlocal enabledelayedexpansion
REM ==========================================================================
REM  check_alive.bat  -  checks whether a domain is alive using curl.
REM  It makes TWO requests per domain:
REM     1) PUBLIC   : normal, may go THROUGH Cloudflare (it gets blocked if the
REM                    ISP cuts Cloudflare's IPs).
REM     2) ORIGIN   : forces --resolve to the server's real IP, bypassing
REM                    Cloudflare. If this responds, the site IS alive.
REM  Detects whether you are behind Cloudflare by looking at the "Server:"
REM  header and the presence of "CF-RAY".
REM
REM  USAGE:
REM     check_alive.bat DOMAIN [ORIGIN_IP] [PATTERN]
REM        DOMAIN      e.g. tabandblank.com
REM        ORIGIN_IP   optional; defaults to the SOURCE variable below.
REM        PATTERN     optional; filters the HTML for lines that match
REM                    (e.g. "googletagmanager" or "GTM-ZZZ7HWB2" or whatever).
REM
REM     check_alive.bat list.txt
REM        batch mode: one domain per line -> "DOMAIN [ORIGIN_IP] [PATTERN]"
REM
REM  EXAMPLES:
REM     check_alive.bat tabandblank.com
REM     check_alive.bat tabandblank.com 1.1.1.1 GTM
REM     check_alive.bat mydomains.txt
REM ==========================================================================

REM ---- EDIT HERE: your VPS IP (origin) to bypass Cloudflare ----
set "SOURCE=1.1.1.1"

set "CURL=curl.exe"
set "TIMEOUT=10"
set "CT=5"
set "HDR=%TEMP%\_chk_headers.txt"

if "%~1"=="" (
  echo Usage: %~nx0 DOMAIN [ORIGIN_IP] [PATTERN]
  echo        %~nx0 list.txt
  echo Ex:  %~nx0 tabandblank.com
  echo      %~nx0 tabandblank.com 94.143.142.31 googletagmanager
  goto :fin
)

REM ---- batch mode: if the 1st argument is an existing file, loop over it ----
if not exist "%~1" goto :individual
echo ^>^>^> Processing list: %~1
for /f "usebackq tokens=1,2,3 delims= " %%a in ("%~1") do (
  if /i not "%%a"=="#" if not "%%a"=="" call :check "%%a" "%%b" "%%c"
)
goto :fin

:individual
call :check "%~1" "%~2" "%~3"

:fin
del "%HDR%" >nul 2>&1
endlocal
exit /b 0

REM --------------------------------------------------------------------------
:check
set "D=%~1"
set "O=%~2"
set "P=%~3"
if "%O%"=="" set "O=%SOURCE%"
echo.
echo =======================================================================
echo  %D%
echo =======================================================================

REM public IPs of the domain (Cloudflare's if it is proxied)
for /f "delims=" %%i in ('powershell -NoProfile -Command "(Resolve-DnsName %D% -Type A -ErrorAction SilentlyContinue).IPAddress -join ', '"') do echo   Public DNS.......: %%i

echo   ORIGIN   %O% (bypassing Cloudflare with --resolve):
%CURL% -s -m %TIMEOUT% --connect-timeout %CT% --resolve %D%:443:%O% -D "%HDR%" -o NUL -w "       HTTP %%{http_code}   ip %%{remote_ip}   %%{time_total}s\n" https://%D%/
call :whoami_hdr "       "
for /f "delims=" %%c in ('%CURL% -s -m %TIMEOUT% --connect-timeout %CT% --resolve %D%:443:%O% -o NUL -w "%%{http_code}" https://%D%/') do set "OC=%%c"

if not "%P%"=="" (
  echo   FILTER of the origin HTML, lines containing "%P%":
  %CURL% -s -m %TIMEOUT% --connect-timeout %CT% --resolve %D%:443:%O% https://%D%/ | findstr /i "%P%"
)

echo   PUBLIC (via normal DNS / Cloudflare):
%CURL% -s -m %TIMEOUT% --connect-timeout %CT% -D "%HDR%" -o NUL -w "       HTTP %%{http_code}   ip %%{remote_ip}   %%{time_total}s\n" https://%D%/
call :whoami_hdr "       "

echo   ---------------------------------------------------------------
if "%OC%"=="000" (
  echo   VERDICT: origin does NOT respond ^(HTTP 000^) - down, firewall or TLS.
) else (
  if "%OC%"=="200" (
    echo   VERDICT: ALIVE - the origin server responds OK.
  ) else (
    echo   VERDICT: ALIVE ^(origin responds with HTTP %OC%^).
  )
)
exit /b 0

:whoami_hdr
REM parse the headers in %HDR%: Server: and CF-RAY to know if you go through Cloudflare
set "PFX=%~1"
set "SRV="
set "CF="
if not exist "%HDR%" goto :wh_none
for /f "delims=" %%h in ('findstr /i /c:"server:" "%HDR%"') do (set "SRV=1" & echo   !PFX!%%h)
for /f "delims=" %%h in ('findstr /i /c:"cf-ray" "%HDR%"') do set "CF=yes"
if not defined SRV goto :wh_none
if defined CF (echo   !PFX!=^> you go through Cloudflare) else (echo   !PFX!=^> DIRECT access to the origin, no Cloudflare)
exit /b 0
:wh_none
echo   !PFX!=^> no HTTP response ^(no headers^)
exit /b 0
