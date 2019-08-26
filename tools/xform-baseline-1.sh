#!/bin/bash

set -x

# ffmpeg-vaapi
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

sed -i "s/test\/ffmpeg-vaapi\/vpp\/brightness.py:test_default(/test\/ffmpeg-vaapi\/vpp\/brightness.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/contrast.py:test_default(/test\/ffmpeg-vaapi\/vpp\/contrast.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/hue.py:test_default(/test\/ffmpeg-vaapi\/vpp\/hue.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/saturation.py:test_default(/test\/ffmpeg-vaapi\/vpp\/saturation.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/denoise.py:test_default(/test\/ffmpeg-vaapi\/vpp\/denoise.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/mirroring.py:test_default(/test\/ffmpeg-vaapi\/vpp\/mirroring.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/rotation.py:test_default(/test\/ffmpeg-vaapi\/vpp\/rotation.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/sharpen.py:test_default(/test\/ffmpeg-vaapi\/vpp\/sharpen.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-vaapi\/vpp\/transpose.py:test_default(/test\/ffmpeg-vaapi\/vpp\/transpose.py:default.test(/g" $1

# gst-vaapi
sed -i "s/test\/gst-vaapi\/decode\/avc.py:test_default(/test\/gst-vaapi\/decode\/avc.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/hevc.py:test_8bit(/test\/gst-vaapi\/decode\/hevc.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/hevc.py:test_10bit(/test\/gst-vaapi\/decode\/10bit\/hevc.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/vp9.py:test_8bit(/test\/gst-vaapi\/decode\/vp9.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/vp9.py:test_10bit(/test\/gst-vaapi\/decode\/10bit\/vp9.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/jpeg.py:test_default(/test\/gst-vaapi\/decode\/jpeg.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/mpeg2.py:test_default(/test\/gst-vaapi\/decode\/mpeg2.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/vc1.py:test_default(/test\/gst-vaapi\/decode\/vc1.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/decode\/vp8.py:test_default(/test\/gst-vaapi\/decode\/vp8.py:default.test(/g" $1

sed -i "s/test\/gst-vaapi\/encode\/avc.py:test_cqp(/test\/gst-vaapi\/encode\/avc.py:cqp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/avc.py:test_cqp_lp(/test\/gst-vaapi\/encode\/avc.py:cqp_lp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/avc.py:test_cbr(/test\/gst-vaapi\/encode\/avc.py:cbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/avc.py:test_vbr(/test\/gst-vaapi\/encode\/avc.py:vbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_8bit_cqp(/test\/gst-vaapi\/encode\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_8bit_cbr(/test\/gst-vaapi\/encode\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_8bit_vbr(/test\/gst-vaapi\/encode\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_10bit_cqp(/test\/gst-vaapi\/encode\/10bit\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_10bit_cbr(/test\/gst-vaapi\/encode\/10bit\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/hevc.py:test_10bit_vbr(/test\/gst-vaapi\/encode\/10bit\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/jpeg.py:test_cqp(/test\/gst-vaapi\/encode\/jpeg.py:cqp.test(/g" $1
sed -Ei "s/test\/gst-vaapi\/encode\/mpeg2.py:test_cqp\(bframes=(.*),case=(.*),gop=(.*),qp=(.*),quality=(.*)\)/test\/gst-vaapi\/encode\/mpeg2.py:cqp.test\(bframes=\1,case=\2,gop=\3,profile=simple,qp=\4,quality=\5\)/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp8.py:test_cqp(/test\/gst-vaapi\/encode\/vp8.py:cqp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp8.py:test_cbr(/test\/gst-vaapi\/encode\/vp8.py:cbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp8.py:test_vbr(/test\/gst-vaapi\/encode\/vp8.py:vbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp9.py:test_8bit_cqp(/test\/gst-vaapi\/encode\/vp9.py:cqp.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp9.py:test_8bit_cbr(/test\/gst-vaapi\/encode\/vp9.py:cbr.test(/g" $1
sed -i "s/test\/gst-vaapi\/encode\/vp9.py:test_8bit_vbr(/test\/gst-vaapi\/encode\/vp9.py:vbr.test(/g" $1

sed -i "s/test\/gst-vaapi\/vpp\/brightness.py:test_default(/test\/gst-vaapi\/vpp\/brightness.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/contrast.py:test_default(/test\/gst-vaapi\/vpp\/contrast.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/hue.py:test_default(/test\/gst-vaapi\/vpp\/hue.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/saturation.py:test_default(/test\/gst-vaapi\/vpp\/saturation.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/denoise.py:test_default(/test\/gst-vaapi\/vpp\/denoise.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/mirroring.py:test_default(/test\/gst-vaapi\/vpp\/mirroring.py:default.test(/g" $1
sed -i "s/test\/gst-vaapi\/vpp\/sharpen.py:test_default(/test\/gst-vaapi\/vpp\/sharpen.py:default.test(/g" $1

# ffmpeg-qsv
sed -i "s/test\/ffmpeg-qsv\/decode\/avc.py:test_default(/test\/ffmpeg-qsv\/decode\/avc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/hevc.py:test_8bit(/test\/ffmpeg-qsv\/decode\/hevc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/hevc.py:test_10bit(/test\/ffmpeg-qsv\/decode\/10bit\/hevc.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/vp9.py:test_8bit(/test\/ffmpeg-qsv\/decode\/vp9.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/vp9.py:test_10bit(/test\/ffmpeg-qsv\/decode\/10bit\/vp9.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/jpeg.py:test_default(/test\/ffmpeg-qsv\/decode\/jpeg.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/mpeg2.py:test_default(/test\/ffmpeg-qsv\/decode\/mpeg2.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/vc1.py:test_default(/test\/ffmpeg-qsv\/decode\/vc1.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/decode\/vp8.py:test_default(/test\/ffmpeg-qsv\/decode\/vp8.py:default.test(/g" $1

sed -i "s/test\/ffmpeg-qsv\/encode\/avc.py:test_cqp(/test\/ffmpeg-qsv\/encode\/avc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/avc.py:test_cqp_lp(/test\/ffmpeg-qsv\/encode\/avc.py:cqp_lp.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/avc.py:test_cbr(/test\/ffmpeg-qsv\/encode\/avc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/avc.py:test_vbr(/test\/ffmpeg-qsv\/encode\/avc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_8bit_cqp(/test\/ffmpeg-qsv\/encode\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_8bit_cbr(/test\/ffmpeg-qsv\/encode\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_8bit_vbr(/test\/ffmpeg-qsv\/encode\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_10bit_cqp(/test\/ffmpeg-qsv\/encode\/10bit\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_10bit_cbr(/test\/ffmpeg-qsv\/encode\/10bit\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/hevc.py:test_10bit_vbr(/test\/ffmpeg-qsv\/encode\/10bit\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/jpeg.py:test_cqp(/test\/ffmpeg-qsv\/encode\/jpeg.py:cqp.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/encode\/mpeg2.py:test_cqp(/test\/ffmpeg-qsv\/encode\/mpeg2.py:cqp.test(/g" $1

sed -i "s/test\/ffmpeg-qsv\/vpp\/brightness.py:test_default(/test\/ffmpeg-qsv\/vpp\/brightness.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/contrast.py:test_default(/test\/ffmpeg-qsv\/vpp\/contrast.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/hue.py:test_default(/test\/ffmpeg-qsv\/vpp\/hue.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/saturation.py:test_default(/test\/ffmpeg-qsv\/vpp\/saturation.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/denoise.py:test_default(/test\/ffmpeg-qsv\/vpp\/denoise.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/mirroring.py:test_default(/test\/ffmpeg-qsv\/vpp\/mirroring.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/rotation.py:test_default(/test\/ffmpeg-qsv\/vpp\/rotation.py:default.test(/g" $1
sed -i "s/test\/ffmpeg-qsv\/vpp\/sharpen.py:test_default(/test\/ffmpeg-qsv\/vpp\/sharpen.py:default.test(/g" $1

# gst-msdk
sed -i "s/test\/gst-msdk\/decode\/avc.py:test_default(/test\/gst-msdk\/decode\/avc.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/hevc.py:test_8bit(/test\/gst-msdk\/decode\/hevc.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/hevc.py:test_10bit(/test\/gst-msdk\/decode\/10bit\/hevc.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/vp9.py:test_8bit(/test\/gst-msdk\/decode\/vp9.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/vp9.py:test_10bit(/test\/gst-msdk\/decode\/10bit\/vp9.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/jpeg.py:test_default(/test\/gst-msdk\/decode\/jpeg.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/mpeg2.py:test_default(/test\/gst-msdk\/decode\/mpeg2.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/vc1.py:test_default(/test\/gst-msdk\/decode\/vc1.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/decode\/vp8.py:test_default(/test\/gst-msdk\/decode\/vp8.py:default.test(/g" $1

sed -i "s/test\/gst-msdk\/encode\/avc.py:test_cqp(/test\/gst-msdk\/encode\/avc.py:cqp.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/avc.py:test_cqp_lp(/test\/gst-msdk\/encode\/avc.py:cqp_lp.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/avc.py:test_cbr(/test\/gst-msdk\/encode\/avc.py:cbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/avc.py:test_vbr(/test\/gst-msdk\/encode\/avc.py:vbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_8bit_cqp(/test\/gst-msdk\/encode\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_8bit_cbr(/test\/gst-msdk\/encode\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_8bit_vbr(/test\/gst-msdk\/encode\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_10bit_cqp(/test\/gst-msdk\/encode\/10bit\/hevc.py:cqp.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_10bit_cbr(/test\/gst-msdk\/encode\/10bit\/hevc.py:cbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/hevc.py:test_10bit_vbr(/test\/gst-msdk\/encode\/10bit\/hevc.py:vbr.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/jpeg.py:test_cqp(/test\/gst-msdk\/encode\/jpeg.py:cqp.test(/g" $1
sed -i "s/test\/gst-msdk\/encode\/mpeg2.py:test_cqp(/test\/gst-msdk\/encode\/mpeg2.py:cqp.test(/g" $1

sed -i "s/test\/gst-msdk\/vpp\/brightness.py:test_default(/test\/gst-msdk\/vpp\/brightness.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/contrast.py:test_default(/test\/gst-msdk\/vpp\/contrast.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/hue.py:test_default(/test\/gst-msdk\/vpp\/hue.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/saturation.py:test_default(/test\/gst-msdk\/vpp\/saturation.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/denoise.py:test_default(/test\/gst-msdk\/vpp\/denoise.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/mirroring.py:test_default(/test\/gst-msdk\/vpp\/mirroring.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/rotation.py:test_default(/test\/gst-msdk\/vpp\/rotation.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/sharpen.py:test_default(/test\/gst-msdk\/vpp\/sharpen.py:default.test(/g" $1
sed -i "s/test\/gst-msdk\/vpp\/transpose.py:test_default(/test\/gst-msdk\/vpp\/transpose.py:default.test(/g" $1

# common
sed -i "s/test_422/test/g" $1
sed -i "s/test_444/test/g" $1
sed -i "s/test_highres/test/g" $1

# since 377ee39e7c09
sed -Ei "s/encode\/mpeg2.py:cqp.test\(bframes=(.*),case=(.*),gop=(.*),profile=(.*),qp=(.*),quality=(.*)\)/encode\/mpeg2.py:cqp.test\(bframes=\1,case=\2,gop=\3,qp=\5,quality=\6\)/g" $1
sed -Ei "s/encode\/mpeg2.py:cqp.test_r2r\(bframes=(.*),case=(.*),gop=(.*),profile=(.*),qp=(.*),quality=(.*)\)/encode\/mpeg2.py:cqp.test_r2r\(bframes=\1,case=\2,gop=\3,qp=\5,quality=\6\)/g" $1

