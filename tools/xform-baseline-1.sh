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

sed -i "s/test\/ffmpeg-vaapi\/encode\/avc.py:test_cqp(/test\/ffmpeg-vaapi\/encode\/avc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/avc.py:test_cqp_lp(/test\/ffmpeg-vaapi\/encode\/avc.py:cqp_lp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/avc.py:test_cbr(/test\/ffmpeg-vaapi\/encode\/avc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/avc.py:test_vbr(/test\/ffmpeg-vaapi\/encode\/avc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_8bit_cqp(/test\/ffmpeg-vaapi\/encode\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_8bit_cbr(/test\/ffmpeg-vaapi\/encode\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_8bit_vbr(/test\/ffmpeg-vaapi\/encode\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_10bit_cqp(/test\/ffmpeg-vaapi\/encode\/10bit\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_10bit_cbr(/test\/ffmpeg-vaapi\/encode\/10bit\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/hevc.py:test_10bit_vbr(/test\/ffmpeg-vaapi\/encode\/10bit\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/jpeg.py:test_cqp(/test\/ffmpeg-vaapi\/encode\/jpeg.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/mpeg2.py:test_cqp(/test\/ffmpeg-vaapi\/encode\/mpeg2.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp8.py:test_cqp(/test\/ffmpeg-vaapi\/encode\/vp8.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp8.py:test_cbr(/test\/ffmpeg-vaapi\/encode\/vp8.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp8.py:test_vbr(/test\/ffmpeg-vaapi\/encode\/vp8.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp9.py:test_8bit_cqp(/test\/ffmpeg-vaapi\/encode\/vp9.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp9.py:test_8bit_cbr(/test\/ffmpeg-vaapi\/encode\/vp9.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/encode\/vp9.py:test_8bit_vbr(/test\/ffmpeg-vaapi\/encode\/vp9.py:vbr.test(/g" $1
