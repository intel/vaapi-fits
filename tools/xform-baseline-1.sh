#!/bin/bash

set -x

sed -i "s/test\/ffmpeg-vaapi\/decode\/avc.py:test_default(/test\/ffmpeg-vaapi\/decode\/avc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/hevc.py:test_8bit(/test\/ffmpeg-vaapi\/decode\/hevc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/hevc.py:test_10bit(/test\/ffmpeg-vaapi\/decode\/10bit\/hevc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/vp9.py:test_8bit(/test\/ffmpeg-vaapi\/decode\/vp9.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/vp9.py:test_10bit(/test\/ffmpeg-vaapi\/decode\/10bit\/vp9.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/jpeg.py:test_default(/test\/ffmpeg-vaapi\/decode\/jpeg.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/mpeg2.py:test_default(/test\/ffmpeg-vaapi\/decode\/mpeg2.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/vc1.py:test_default(/test\/ffmpeg-vaapi\/decode\/vc1.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/decode\/vp8.py:test_default(/test\/ffmpeg-vaapi\/decode\/vp8.py:default.test(/g" $1

