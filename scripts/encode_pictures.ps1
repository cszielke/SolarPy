# Script for encoding Webcam pictures through ffmpeg
# FFMpeg has to be installed and destignation dir must not contain JPG images. 
# They will be erased without further questions

$sourcedir=$args[0]
$destvideodir=$args[1]

$ffmpeg="V:\Videotools\ffmpeg\ffmpeg.exe"
$bitrate=6000000
$tmpdir="V:\Videotools\ffmpeg\tmp"

if($null -eq $sourcedir){
    # Testcase"
    $sourcedir = "\\raspidbsrv\web\html\webcam\20200111" 
}

if($null -eq $destvideodir){
    # Testcase"
    $destvideodir="\\raspidbsrv\web\html\webcam\videos"
}

if(!(Test-Path $ffmpeg -PathType Leaf)){
    Write-Output "FFMpeg expected to be installed in '$ffmpeg'"
    exit 1
}


#Get the Date from file paths last chunk. (file date could be also possible)
$date = Split-Path -Path $sourcedir -Resolve -Leaf
Write-Output "Date: $date"

# Check if $date is numeric
if(!($date -match "^\d+$")){
    Write-Output "Last chunk of $sourcedir is not numeric. Exiting."
    exit 2
}

$destvideofile="$destvideodir\pv$date.mp4"
write-output "Check if Video file '$destvideofile' already exist."

if(Test-Path $destvideofile -PathType Leaf){
    Write-Output "'$destvideofile' exist."
    exit 0
}
else{
    write-output "Check Video output dir '$destvideodir'"
    if(!(Test-Path -Path $destvideodir)){
        Write-Output "Create '$destvideodir'"
    
        New-Item -ItemType directory -Path $destvideodir
    }
    else{
        Write-Output "$destvideodir exist."
    }

    write-output "Check Tmp dir '$tmpdir'"
    if(!(Test-Path -Path $tmpdir)){
        Write-Output "Create Temp dir: '$tmpdir'"

        New-Item -ItemType directory -Path $tmpdir
    }
    else{
        Write-Output "Delete files in '$tmpdir' "
        Get-ChildItem $tmpdir/* -Include * -Recurse | Remove-Item
    }

    Write-Output "Copy images from '$sourcedir' to '$tmpdir'"
    Copy-Item -Path "$sourcedir\*.jpg" -Destination "$tmpdir" -Recurse

    Write-Output "Rename files for numeric order"
    $i = 0
    Get-ChildItem "$tmpdir\*.jpg" | ForEach-Object {
        $newfn = ('pv{0:D4}.jpg' -f $i++)
        # Write-Output "Rename file $_ to $newfn"
        Rename-Item $_ -NewName $newfn
    }

    Write-Output "'$destvideofile' not exist."

    Write-Output "Start FFMpeg"
    & $ffmpeg -r 12 -f image2 -i "$tmpdir\pv%04d.jpg" -b:v $bitrate "$destvideofile"
    $success = $?
    Write-Output ExitCode=$success
    if($success){
        Write-Output "FFMpeg Ok"
        Write-Output "Removing temp files"
        Get-ChildItem $tmpdir/* -Include * -Recurse | Remove-Item
        exit 0
    }
    else{
        Write-Output "FFMpeg Error!"
        # Read-Host -Prompt "Press Enter to continue"
        exit 1
    }
}
exit 100  # should not happen
