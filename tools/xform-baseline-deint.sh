#!/bin/bash

set -x

# gst-vaapi
sed -i "s/test\/gst-vaapi\/vpp\/deinterlace.py:test_default(/test\/gst-vaapi\/vpp\/deinterlace.py:raw.test(/g" $1
