# Make videos out of every Webcam directory

$sourcedir=$args[0]
$destvideodir=$args[1]

$encodescript="encode_pictures.ps1"

function PrintUsage {
    Write-Output 'Usage: $script "<sourcedir>" "<video/destignation/dir>"'
    Write-Output '    <sourcedir> must contain subdirectorys with the date as name in format "YYYYmmdd".'
    Write-Output '    Example:'
    Write-Output '    <sourcedir> +- 20191223 +-pv000237.jpg'
    Write-Output '                |           +-pv000237.jpg'
    Write-Output '                |           | ....'
    Write-Output '                |           +-pv235924.jpg'
    Write-Output '                +- 20191224'
    Write-Output '                | ....'
    Write-Output '                L- 20200112'
    Write-Output ' Example: .\scripts\makeallpvvideos.ps1 \\192.168.15.241\web\html\webcam \\192.168.15.241\web\html\webcam\videos'
}

if($null -eq $sourcedir){
    Write-Output 'Usage Error! No source dir!'
    PrintUsage
    exit 1
    # default dir"
    #$sourcedir = "\\czsrv01\web\html\webcam" 
}

if($null -eq $destvideodir){
    Write-Output 'Usage Error! No destignation dir!'
    PrintUsage
    exit 1
    # default dir"
    # $destvideodir = "\\czsrv01\web\html\webcam\videos" 
}

$scriptdir = Split-Path $script:MyInvocation.MyCommand.Path
Write-Output "Current script directory is $scriptdir"

Get-ChildItem "$sourcedir\*" | ForEach-Object {
    if((Get-Item $_) -is [System.IO.DirectoryInfo]){
        Write-Output "Working on directory '$_'"
        & $scriptdir\$encodescript $_ $destvideodir
    }
    else{
        Write-Output "$_ is not a directory"
    }
}