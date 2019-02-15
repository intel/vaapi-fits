# VA-API Functional Integration Test Suite

The VA-API Functional Integration Test Suite is a configurable test suite for VA-API-based media software/middleware.  It is written in Python and currently provides tests for VA-API hardware accelerated encode, decode and vpp video pipelines for gstreamer and ffmpeg.  It can be easily extended to support additional VA-API-based software/middleware.  The tests execute the video pipelines and validate their outputs using common image and video metrics such as checksum, SSIM and PSNR.

## License

See [LICENSE.md](LICENSE.md) file

## Overview

A vaapi-fits bootstrap script is provided at the top-level directory. By default, it loads a test config (spec) file from `config/default` and a baseline (references) file from `baseline/default`.  These default files provide a minimal set of example test cases and can be used as a reference guide to create your own custom config and baseline files.

To have vaapi-fits load a custom config file, you can use the `VAAPI_FITS_CONFIG_FILE` environment variable.  To use a custom baseline file, use `--baseline-file` command-line option.

## Cloning the Repository

This project uses Git Large File Storage (Git LFS) to track the [assets.tbz2](assets.tbz2) file.  Therefore, you will need to install [Git LFS](https://help.github.com/articles/versioning-large-files/) before cloning this repository to your local system.

distro|command
------|-------
Fedora | `sudo dnf install git-lfs` (NOTE: may not be available on older versions)
Ubuntu | `sudo apt install git-lfs && git lfs install` (NOTE: may not be available on older versions)
Other | please follow the instructions [here](https://help.github.com/articles/installing-git-large-file-storage/#platform-linux)

After Git LFS is installed, you can clone and interact with this repository using the same standard Git workflow as usual.

## Requirements

* Python Slash library.

  ```sudo pip install slash==1.5.1```

* Python NumPy library.

  ```sudo pip install numpy```

* Python scikit-image library.

  ```sudo pip install scikit-image```

## Examples

* Run all available test cases

  ```vaapi-fits run test```

* Run only test cases that are supported by SKL platform

  ```vaapi-fits run test -k tag:SKL```

* Run only gst-vaapi test cases on iHD driver

  ```LIBVA_DRIVER_NAME=iHD GST_VAAPI_ALL_DRIVERS=1 vaapi-fits run test/gst-vaapi```

## Some Useful Options

#### _run_ sub-command

option|description
------|-----------
<nobr>`-v`</nobr> | Make console more verbose (can be specified multiple times)
<nobr>`--artifact-retention NUM`</nobr> | Retention policy for test artifacts (e.g. encoded or decoded output files) 0 = Keep None; 1 = Keep Failed; 2 = Keep All
<nobr>`--parallel-metrics`</nobr> | SSIM and PSNR calculations will be processed in parallel mode
<nobr>`--parallel NUM`</nobr> | Run test cases in parallel using NUM worker processes
<nobr>`--call-timeout SECONDS`</nobr> | The maximum amount of time that any execution of external programs (e.g. ffmpeg, gst-launch-1.0, etc.) is allowed before being terminated/killed
<nobr>`-l DIR`</nobr> | Specify root directory to store logs

## Contributing

Patches should be submitted via GitHub pull-requests.

Patches should comply with the following format (note: summary and body must be separated by a blank line):

```
<component>: Change summary (limit to 50 characters)

More detailed explanation of your changes: Why and how.
Wrap it to 72 characters.

Signed-off-by: <contributor@foo.com>
```

See [here](http://chris.beams.io/posts/git-commit/) for some more good advice about writing commit messages.

## Reporting a Security Issue:

Please visit http://intel.com/security for security issue report.
