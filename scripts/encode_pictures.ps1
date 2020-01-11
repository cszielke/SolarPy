# Script for encoding Webcam pictures through ffmpeg
# FFMpeg has to be installed and destignation dir must not contain JPG images. 
# They will be erased without further questions

$ffmpeg="V:\Videotools\ffmpeg\ffmpeg.exe"
$bitrate=1500000
$sourcedir=$args[0]
$destdir="V:\Videotools\ffmpeg\tmp"

if($null -eq $sourcedir){
    # Testcase"
    $sourcedir = "C:\Users\zielke\Desktop\20200110" 
}

$date = Split-Path -Path $sourcedir -Resolve -Leaf
Write-Output "Date: $date"

if(!(Test-Path -Path $destdir)){
    Write-Output "Create $destdir"

    New-Item -ItemType directory -Path $destdir
}
else{
    Write-Output "Delete $destdir Images"
    Get-ChildItem $destdir/*.jpg -Include * -Recurse | Remove-Item
}

Write-Output "Copy $sourcedir to $destdir"

Copy-Item -Path "$sourcedir\*" -Destination "$destdir" -Recurse

$i = 0
Get-ChildItem "$destdir\*.jpg" | ForEach-Object {
    Write-Output "Rename file $_ to $i"
    Rename-Item $_ -NewName ('pv{0:D4}.jpg' -f $i++)
}

Write-Output "State FFMpeg"
& $ffmpeg -r 12 -f image2 -i "$destdir\pv%04d.jpg" -b:v $bitrate "V:\Videotools\ffmpeg\tmp\pv$date.mp4"
$success = $?
Write-Output ExitCode=$success
if($success){
    Write-Output "Removing images"
    Get-ChildItem $destdir/*.jpg -Include * -Recurse | Remove-Item
}
# Read-Host -Prompt "Press Enter to continue"
