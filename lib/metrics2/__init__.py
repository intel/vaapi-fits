###
### Copyright (C) 2022 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from . import factory
from . import filesize, md5, mse, nrmse, psnr, ssim

def check(**params):
  factory.create(**params).check()
