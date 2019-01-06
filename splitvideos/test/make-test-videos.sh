#!/bin/bash
#ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 -c:v libx264 -preset slow -crf 22 -c:a copy
SCREENDIM=640x480
FPS=25
for duration in 1 2 3
do
    ffmpeg -f lavfi -i testsrc=duration=$duration:size=$SCREENDIM:rate=$FPS -pix_fmt yuv420p testvideo-$duration.mp4
done
