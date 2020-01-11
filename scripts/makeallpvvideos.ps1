# Make videos out of every Webcam directory

$sourcedir=$args[0]
$encodescript="V:\Videotools\ffmpeg\encode_pictures.ps1"

if($null -eq $sourcedir){
    # default dir"
    $sourcedir = "\\192.168.15.160\c\SolarPy\templates\public\webcam" 
}

Get-ChildItem "$sourcedir\*" | ForEach-Object {
    if((Get-Item $_) -is [System.IO.DirectoryInfo]){
        Write-Output "Working on directory '$_'"
        & $encodescript $_
    }
    else{
        Write-Output "$_ is not a directory"
    }
}