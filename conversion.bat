@echo off
cd F:\Almighty Rasputin\dist
set "input_file=%1"
set "output_file=%~dpn1_converted.mp4"

ffmpeg -i "%input_file%" -vf "scale=-2:720" -c:v libx264 -preset slow -crf 22 -c:a aac -strict experimental -b:a 192k "%output_file%"