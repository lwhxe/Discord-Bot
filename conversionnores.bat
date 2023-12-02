@echo off
cd F:\Almighty Rasputin\dist
set "input_file=%1"
set "output_file=%~dpn1_converted.mp4"

ffmpeg -i "%input_file%" "%output_file%"