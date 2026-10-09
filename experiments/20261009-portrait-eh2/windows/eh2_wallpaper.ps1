# EH2 of the portrait (Windows): machine checks of the desktop wallpaper API.
#
# What it does, with placeholder images only:
#   1. saves the current wallpaper of every monitor and the picture position (to a temporary file,
#      not to the results), and refuses to run (unless -Force is given) when the background is a
#      slideshow, a solid colour or Windows Spotlight, when a monitor's original picture file is
#      missing, or when it is the copy Windows keeps in its Themes folder (overwritten as soon as the
#      wallpaper changes): none of these can be restored through this API
#   2. sets the wallpaper per monitor and for all monitors at once, reads it back and times each call
#   3. measures the CPU time and working set of this process, explorer and dwm while idle and while
#      updating every few seconds
#   4. optionally (-Manual) asks the operator to check virtual desktops and a screen share
#   5. always restores the saved settings (finally block) and reads them back
#
# The results file holds no machine name, user name or file path: only monitor sizes, timings,
# booleans and counts.
#
# Usage (Windows PowerShell 5.1 or PowerShell 7):
#   powershell -NoProfile -ExecutionPolicy Bypass -File eh2_wallpaper.ps1 [-Quick] [-Manual] [-Force]
#     -Quick   3 updates, 10 s idle, 10 s updating (smoke test, about 1 minute)
#     -DryRun  never sets the wallpaper: enumerates monitors, makes the images, reads the current
#              wallpaper, samples CPU for a few seconds and writes the results (checks the script
#              on a machine whose background cannot be restored)
#     default  30 updates, 300 s idle, 300 s updating every 10 s (about 12 minutes)
#
# Do not run it on a machine that is running a measurement: the CPU figures would disturb each other.

[CmdletBinding()]
param(
    [switch]$Quick,
    [switch]$Manual,
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace GseEh2 {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

    public enum DESKTOP_WALLPAPER_POSITION { Center = 0, Tile = 1, Stretch = 2, Fit = 3, Fill = 4, Span = 5 }

    [ComImport, Guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    public interface IDesktopWallpaper {
        void SetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.LPWStr)] string wallpaper);
        [return: MarshalAs(UnmanagedType.LPWStr)] string GetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
        [return: MarshalAs(UnmanagedType.LPWStr)] string GetMonitorDevicePathAt(uint monitorIndex);
        uint GetMonitorDevicePathCount();
        RECT GetMonitorRECT([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
        void SetBackgroundColor(uint color);
        uint GetBackgroundColor();
        void SetPosition(DESKTOP_WALLPAPER_POSITION position);
        DESKTOP_WALLPAPER_POSITION GetPosition();
        void SetSlideshow(IntPtr items);
        IntPtr GetSlideshow();
        void SetSlideshowOptions(int options, uint slideshowTick);
        void GetSlideshowOptions(out int options, out uint slideshowTick);
        void AdvanceSlideshow([MarshalAs(UnmanagedType.LPWStr)] string monitorID, int direction);
        int GetStatus();
    }

    // PowerShell cannot call methods of an IUnknown-only COM interface on a System.__ComObject,
    // so every call goes through this wrapper.
    public class Api {
        private readonly IDesktopWallpaper w;
        public Api() {
            Type t = Type.GetTypeFromCLSID(new Guid("C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD"));
            w = (IDesktopWallpaper)Activator.CreateInstance(t);
        }
        public int Status() { return w.GetStatus(); }
        public uint Count() { return w.GetMonitorDevicePathCount(); }
        public string PathAt(uint i) { return w.GetMonitorDevicePathAt(i); }
        public int[] Rect(string id) { RECT r = w.GetMonitorRECT(id); return new int[] { r.Left, r.Top, r.Right, r.Bottom }; }
        public string Get(string id) { return w.GetWallpaper(id); }
        public void Set(string id, string path) { w.SetWallpaper(id, path); }
        public int GetPosition() { return (int)w.GetPosition(); }
        public void SetPosition(int p) { w.SetPosition((DESKTOP_WALLPAPER_POSITION)p); }
    }
}
'@

function Get-Median([double[]]$xs) {
    if ($xs.Count -eq 0) { return $null }
    $s = @($xs | Sort-Object)
    $n = $s.Count
    if ($n % 2 -eq 1) { return $s[[int](($n - 1) / 2)] }
    return ($s[$n / 2 - 1] + $s[$n / 2]) / 2
}

function Get-Pct([double[]]$xs, [double]$p) {
    if ($xs.Count -eq 0) { return $null }
    $s = @($xs | Sort-Object)
    $i = [Math]::Min($s.Count - 1, [Math]::Max(0, [int][Math]::Ceiling($p / 100.0 * $s.Count) - 1))
    return $s[$i]
}

function New-PlaceholderImage([string]$path, [int]$w, [int]$h, [int]$variant) {
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.Clear([System.Drawing.Color]::FromArgb(235, 232, 225))
        $step = [Math]::Max(8, [int]($w / 24))
        for ($x = 0; $x -lt $w; $x += $step * 2) {
            $c = if ($variant -eq 0) { [System.Drawing.Color]::FromArgb(120, 150, 190) } else { [System.Drawing.Color]::FromArgb(200, 140, 170) }
            $brush = New-Object System.Drawing.SolidBrush($c)
            if ($variant -eq 0) { $g.FillRectangle($brush, $x, 0, $step, $h) } else { $g.FillEllipse($brush, $x, [int]($h / 3), $step, $step) }
            $brush.Dispose()
        }
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $g.Dispose(); $bmp.Dispose()
    }
}

function Get-Sha256([string]$path) {
    # .NET directly: Get-FileHash is missing on some Windows PowerShell 5.1 installations
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $fs = [System.IO.File]::OpenRead($path)
    try { return ([BitConverter]::ToString($sha.ComputeHash($fs))).Replace('-', '') }
    finally { $fs.Dispose(); $sha.Dispose() }
}

function Get-ProcSample([string]$name) {
    # Sum over all processes of that name. Returns $null fields when access is denied (dwm often is).
    $cpu = 0.0; $ws = 0.0; $ok = $true; $n = 0
    foreach ($p in @(Get-Process -Name $name -ErrorAction SilentlyContinue)) {
        $n++
        try { $cpu += $p.TotalProcessorTime.TotalSeconds } catch { $ok = $false }
        try { $ws += $p.WorkingSet64 / 1MB } catch { }
    }
    if ($n -eq 0) { return @{ cpu_s = $null; ws_mb = $null; n = 0 } }
    return @{ cpu_s = $(if ($ok) { $cpu } else { $null }); ws_mb = $ws; n = $n }
}

function Get-Samples {
    $self = Get-Process -Id $PID
    return @{
        self = @{ cpu_s = $self.TotalProcessorTime.TotalSeconds; ws_mb = $self.WorkingSet64 / 1MB; n = 1 }
        explorer = Get-ProcSample 'explorer'
        dwm = Get-ProcSample 'dwm'
    }
}

function Get-Delta($a, $b) {
    $out = @{}
    foreach ($k in $a.Keys) {
        $d = $null
        if ($a[$k].cpu_s -ne $null -and $b[$k].cpu_s -ne $null) { $d = [Math]::Round($b[$k].cpu_s - $a[$k].cpu_s, 3) }
        $out[$k] = @{ cpu_s = $d; ws_mb_start = $a[$k].ws_mb; ws_mb_end = $b[$k].ws_mb }
    }
    return $out
}

function Read-YesNo([string]$prompt) {
    while ($true) {
        $r = (Read-Host "$prompt [y/n/u(unknown)]").Trim().ToLower()
        if ($r -in @('y', 'n', 'u')) { return @{ y = 'yes'; n = 'no'; u = 'unknown' }[$r] }
    }
}

$nUpdates = if ($Quick) { 3 } else { 30 }
$idleS = if ($Quick) { 10 } else { 300 }
$busyS = if ($Quick) { 10 } else { 300 }
$busyEvery = if ($Quick) { 3 } else { 10 }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$resultsDir = Join-Path (Split-Path -Parent $here) 'results'
New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$work = Join-Path $env:TEMP "gse-eh2-$stamp"
New-Item -ItemType Directory -Force -Path $work | Out-Null
$restoreFile = Join-Path $env:TEMP "gse-eh2-restore-$stamp.json"

$res = [ordered]@{
    os = 'windows'
    os_version = [Environment]::OSVersion.Version.ToString()
    powershell = $PSVersionTable.PSVersion.ToString()
    mode = $(if ($DryRun) { 'dryrun' } elseif ($Quick) { 'quick' } else { 'full' })
    started = (Get-Date).ToString('s')
}

# Background type (read only). 0 = picture, 1 = solid colour, 2 = slideshow, 3 = Windows Spotlight
$bgType = $null
try {
    $bgType = (Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers' -Name BackgroundType -ErrorAction Stop).BackgroundType
} catch { }
$res.background_type = $bgType

$dw = New-Object GseEh2.Api
$status = $dw.Status()
# DSS_SLIDESHOW (0x2) = a slideshow is configured. DSS_ENABLED (0x1) only says slideshows are possible.
$res.slideshow_status_raw = $status
$res.slideshow_enabled = [bool]($status -band 2)
if (-not $DryRun -and -not $Force -and ($res.slideshow_enabled -or ($bgType -ne $null -and $bgType -ne 0))) {
    Write-Host "The current background is not a single picture (type $bgType, slideshow $($res.slideshow_enabled))."
    Write-Host 'It cannot be restored through this API. Switch to a picture background first, or pass -Force.'
    exit 3
}

$count = $dw.Count()
$monitors = @()
$orig = @()
$inactive = 0
for ($i = 0; $i -lt $count; $i++) {
    $id = $dw.PathAt([uint32]$i)
    try { $r = $dw.Rect($id) } catch { $inactive++; continue }  # monitors not attached now
    $w = $r[2] - $r[0]; $h = $r[3] - $r[1]
    if ($w -le 0 -or $h -le 0) { $inactive++; continue }
    $monitors += [ordered]@{ index = $monitors.Count; width = $w; height = $h }
    $orig += [ordered]@{ id = $id; wallpaper = $dw.Get($id); w = $w; h = $h }
}
$res.inactive_monitor_entries = $inactive
$count = $orig.Count
$origPos = $dw.GetPosition()  # 0 Center, 1 Tile, 2 Stretch, 3 Fit, 4 Fill, 5 Span
$res.monitors = $monitors
$res.original_position = $origPos
$res.original_exists = @($orig | ForEach-Object { [bool]($_.wallpaper -and (Test-Path -LiteralPath $_.wallpaper)) })
$themes = Join-Path $env:APPDATA 'Microsoft\Windows\Themes'
$res.original_in_themes_cache = @($orig | ForEach-Object { [bool]($_.wallpaper -and $_.wallpaper.StartsWith($themes, [StringComparison]::OrdinalIgnoreCase)) })
foreach ($o in $orig) {
    # the hash confirms after the restore that the original file itself was not overwritten
    $o.sha256 = $(if ($o.wallpaper -and (Test-Path -LiteralPath $o.wallpaper)) { (Get-Sha256 $o.wallpaper) } else { $null })
}
if ($DryRun) {
    $lat = @()
    for ($i = 0; $i -lt $count; $i++) {
        $a = Join-Path $work "m$i-a.png"
        New-PlaceholderImage $a $orig[$i].w $orig[$i].h 0
        $res.dryrun_image_bytes = (Get-Item -LiteralPath $a).Length
        $sw = [Diagnostics.Stopwatch]::StartNew(); $null = $dw.Get($orig[$i].id); $sw.Stop()
        $lat += $sw.Elapsed.TotalMilliseconds
    }
    $res.dryrun_get_latency_ms_median = (Get-Median $lat)
    $s0 = Get-Samples; Start-Sleep -Seconds 3; $s1 = Get-Samples
    $res.dryrun_cpu = (Get-Delta $s0 $s1)
    $res.finished = (Get-Date).ToString('s')
    $out = Join-Path $resultsDir "eh2-windows-$stamp-dryrun.json"
    ($res | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $out -Encoding UTF8
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Dry run (the wallpaper was not changed). Results: $out"
    exit 0
}
if (-not $Force -and ((@($res.original_exists) -contains $false) -or (@($res.original_in_themes_cache) -contains $true))) {
    Write-Host 'The original wallpaper of a monitor is missing, or it is the copy Windows keeps in its Themes folder'
    Write-Host '(overwritten as soon as the wallpaper changes). It cannot be restored safely.'
    Write-Host 'Pick a picture file in Settings > Personalisation > Background first, or pass -Force.'
    exit 3
}
# The restore file is the only place that holds the original paths. It stays in %TEMP%.
(@{ position = $origPos; monitors = $orig } | ConvertTo-Json -Depth 4) | Set-Content -LiteralPath $restoreFile -Encoding UTF8
Write-Host "Saved the original settings to $restoreFile"

try {
    # Placeholder images per monitor
    $imgs = @()
    for ($i = 0; $i -lt $count; $i++) {
        $a = Join-Path $work "m$i-a.png"; $b = Join-Path $work "m$i-b.png"
        New-PlaceholderImage $a $orig[$i].w $orig[$i].h 0
        New-PlaceholderImage $b $orig[$i].w $orig[$i].h 1
        $imgs += , @($a, $b)
    }
    $dw.SetPosition(4)  # Fill

    # 1. Per-monitor set and read back
    $lat = @(); $okN = 0; $tot = 0
    for ($k = 0; $k -lt $nUpdates; $k++) {
        for ($i = 0; $i -lt $count; $i++) {
            $p = $imgs[$i][$k % 2]
            $sw = [Diagnostics.Stopwatch]::StartNew()
            $dw.Set($orig[$i].id, $p)
            $sw.Stop()
            $lat += $sw.Elapsed.TotalMilliseconds
            $tot++
            if ($dw.Get($orig[$i].id) -eq $p) { $okN++ }
        }
        Start-Sleep -Milliseconds 300
    }
    $res.per_monitor = [ordered]@{ calls = $tot; readback_ok = $okN; latency_ms_median = (Get-Median $lat); latency_ms_p95 = (Get-Pct $lat 95); latency_ms_max = ($lat | Measure-Object -Maximum).Maximum }

    # 2. Distinct images per monitor (only meaningful with two or more monitors)
    if ($count -ge 2) {
        for ($i = 0; $i -lt $count; $i++) { $dw.Set($orig[$i].id, $imgs[$i][$i % 2]) }
        $distinct = $true
        for ($i = 0; $i -lt $count; $i++) { if ($dw.Get($orig[$i].id) -ne $imgs[$i][$i % 2]) { $distinct = $false } }
        $res.distinct_per_monitor_readback_ok = $distinct
    } else {
        $res.distinct_per_monitor_readback_ok = 'single_monitor'
    }

    # 3. All monitors at once (monitorID = null)
    $lat2 = @()
    for ($k = 0; $k -lt [Math]::Min($nUpdates, 10); $k++) {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $dw.Set($null, $imgs[0][$k % 2])
        $sw.Stop()
        $lat2 += $sw.Elapsed.TotalMilliseconds
        Start-Sleep -Milliseconds 300
    }
    $res.all_monitors = [ordered]@{ calls = $lat2.Count; latency_ms_median = (Get-Median $lat2); latency_ms_p95 = (Get-Pct $lat2 95) }

    # 4. CPU and memory: idle, then updating
    $s0 = Get-Samples
    Start-Sleep -Seconds $idleS
    $s1 = Get-Samples
    $updates = 0
    $t = [Diagnostics.Stopwatch]::StartNew()
    while ($t.Elapsed.TotalSeconds -lt $busyS) {
        for ($i = 0; $i -lt $count; $i++) { $dw.Set($orig[$i].id, $imgs[$i][$updates % 2]) }
        $updates++
        Start-Sleep -Seconds $busyEvery
    }
    $s2 = Get-Samples
    $res.cpu = [ordered]@{
        idle_s = $idleS; busy_s = $busyS; busy_every_s = $busyEvery; busy_updates = $updates
        idle = (Get-Delta $s0 $s1); busy = (Get-Delta $s1 $s2)
    }

    # 5. Optional manual checks
    if ($Manual) {
        Write-Host ''
        Write-Host 'Manual check A: virtual desktops.'
        Write-Host 'Create a second virtual desktop (Win+Ctrl+D), come back to the first one (Win+Ctrl+Left), then press Enter.'
        Read-Host | Out-Null
        $dw.Set($null, $imgs[0][0])
        Write-Host 'The striped image is now set on this desktop. Switch to the second desktop (Win+Ctrl+Right) and press Enter.'
        Read-Host | Out-Null
        $res.manual_virtual_desktop = [ordered]@{
            readback_matches_on_other_desktop = ($dw.Get($orig[0].id) -eq $imgs[0][0])
            striped_image_visible_on_other_desktop = (Read-YesNo 'Do you see the striped image on the second desktop?')
        }
        Write-Host 'Switch back to the first desktop, then press Enter.'
        Read-Host | Out-Null
        # Everything after this (the share check and the restore) acts on the current desktop.
        $back = $true
        while ($dw.Get($orig[0].id) -ne $imgs[0][0]) {
            $ans = (Read-Host 'The wallpaper here is not the striped image, so this may not be the first desktop. Switch back and press Enter, or type skip').Trim().ToLower()
            if ($ans -eq 'skip') { $back = $false; break }
        }
        $res.manual_back_on_first_desktop_confirmed = $back
        Write-Host ''
        Write-Host 'Manual check B: screen share or recording.'
        Write-Host 'Start a screen share or a screen recording that shows the desktop, then press Enter. Three updates follow, 5 s apart.'
        Read-Host | Out-Null
        for ($k = 0; $k -lt 3; $k++) { $dw.Set($null, $imgs[0][($k + 1) % 2]); Start-Sleep -Seconds 5 }
        $res.manual_screen_share = [ordered]@{
            change_visible_in_share = (Read-YesNo 'Was the change of wallpaper visible in the share or recording?')
            flicker_or_flash = (Read-YesNo 'Was there a flicker or a flash on the screen when the wallpaper changed?')
        }
    }
}
finally {
    # Always restore
    $restored = @()
    try { $dw.SetPosition($origPos) } catch { }
    for ($i = 0; $i -lt $count; $i++) {
        $o = $orig[$i]
        if ($o.wallpaper -and (Test-Path -LiteralPath $o.wallpaper)) {
            try {
                $dw.Set($o.id, $o.wallpaper)
                $sameFile = ((Get-Sha256 $o.wallpaper) -eq $o.sha256)
                $restored += (($dw.Get($o.id) -eq $o.wallpaper) -and $sameFile)
            } catch { $restored += $false }
        } else {
            $restored += 'original_missing'
        }
    }
    $res.restored = $restored
    $res.restored_position_ok = ($dw.GetPosition() -eq $origPos)
    $res.finished = (Get-Date).ToString('s')
    $out = Join-Path $resultsDir "eh2-windows-$stamp.json"
    ($res | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath $out -Encoding UTF8
    Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Results: $out"
    Write-Host "Restored: $($restored -join ', ')  position ok: $($res.restored_position_ok)"
    if (@($restored | Where-Object { $_ -ne $true }).Count -eq 0 -and $res.restored_position_ok) {
        Remove-Item -LiteralPath $restoreFile -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Restore was not confirmed. The original settings are kept in $restoreFile (see README)."
    }
}
