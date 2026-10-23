$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

if (-not $env:DATABASE_PATH) {
    $env:DATABASE_PATH = Join-Path $Root "database"
}
if (-not $env:DATABASE_URL) {
    $dbPathForUrl = $env:DATABASE_PATH.Replace("\", "/").TrimEnd("/")
    $env:DATABASE_URL = "sqlite:$dbPathForUrl/the_last_signal.db"
}

New-Item -ItemType Directory -Path $env:DATABASE_PATH -Force | Out-Null

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "Rust/Cargo is required but was not found in PATH."
    exit 127
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is required but was not found in PATH."
    exit 127
}

$Manifest = Join-Path $Root "server_rust/Cargo.toml"
Write-Host "[launcher] Building Rust server..."
& cargo build --locked --manifest-path $Manifest
if ($LASTEXITCODE -ne 0) {
    Write-Error "Server build failed (exit $LASTEXITCODE); the client was not started."
    exit $LASTEXITCODE
}

$ServerExe = Join-Path $Root "server_rust/target/debug/the-last-signal-server.exe"
if (-not (Test-Path $ServerExe)) {
    Write-Error "Expected server executable was not produced: $ServerExe"
    exit 1
}

$Server = $null
$Client = $null

function Stop-ProcessTree($Process) {
    if ($null -ne $Process) {
        $Process.Refresh()
        if (-not $Process.HasExited) {
            & taskkill.exe /PID $Process.Id /T /F | Out-Null
        }
    }
}

try {
    Write-Host "[launcher] Starting Rust server (127.0.0.1:5000)..."
    $Server = Start-Process -FilePath $ServerExe -WorkingDirectory $Root -PassThru -NoNewWindow

    $Ready = $false
    for ($Attempt = 0; $Attempt -lt 60; $Attempt++) {
        $Server.Refresh()
        if ($Server.HasExited) {
            throw "Server exited before becoming ready (exit $($Server.ExitCode))."
        }

        $Tcp = New-Object System.Net.Sockets.TcpClient
        try {
            $Tcp.Connect("127.0.0.1", 5000)
            $Ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        } finally {
            $Tcp.Dispose()
        }
    }

    if (-not $Ready) {
        throw "Server did not listen on 127.0.0.1:5000 within 60 seconds."
    }

    Write-Host "[launcher] Server is ready; starting Python client..."
    $Client = Start-Process -FilePath "python" -ArgumentList @("-m", "client_python.main") -WorkingDirectory $Root -PassThru -NoNewWindow

    while ($true) {
        $Server.Refresh()
        $Client.Refresh()
        if ($Server.HasExited) {
            Write-Host "[launcher] Server stopped; shutting down the client."
            break
        }
        if ($Client.HasExited) {
            Write-Host "[launcher] Client stopped; shutting down the server."
            break
        }
        Start-Sleep -Milliseconds 500
    }
} catch {
    Write-Error $_
    exit 1
} finally {
    Stop-ProcessTree $Client
    Stop-ProcessTree $Server
}
