![Paper](https://img.shields.io/badge/Paper-ACM-blue)
![License](https://img.shields.io/badge/License-Research-green)

# Samsung NUAs
Official repository for the paper:

> D. Vázquez-Padín and F. Pérez-González, "Beyond Non-Unique Artifacts: SVD-Based PRNU Recovery for Samsung Device Identification," in ACM Workshop on Information Hiding and Multimedia Security (IH&MMSec '26), June 17–19, 2026, Firenze, Italy. ACM, New York, NY, USA,
12 pages. https://doi.org/10.1145/3785353.3815090

Paper available at:  
https://dl.acm.org/doi/10.1145/3785353.3815090  


[![Paper PDF](https://img.shields.io/badge/Paper-PDF-blue?style=for-the-badge)](https://gpsc.uvigo.es/wp-content/uploads/2026/06/ihmmsec26_dvazquez_fperez.pdf)
[![NUA Patterns](https://img.shields.io/badge/Samsung%20NUA%20Patterns-ZIP-green?style=for-the-badge)](https://ggl.link/Sl7fNQJ)
[![Samsung Image Dataset](https://img.shields.io/badge/Samsung%20Image%20Dataset-ZIP-orange?style=for-the-badge)](https://ggl.link/zkg2SDR)

### Citation

If you use this repository in your research, please cite:

```
@inproceedings{SAMSUNG_NUAS_2026,
  author = {V\'{a}zquez-Pad\'{\i}n, David and P\'{e}rez-Gonz\'{a}lez, Fernando},
  title = {Beyond Non-Unique Artifacts: SVD-Based PRNU Recovery for Samsung Device Identification},
  year = {2026},
  isbn = {9798400723766},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  url = {https://doi.org/10.1145/3785353.3815090},
  doi = {10.1145/3785353.3815090},
  booktitle = {Proceedings of the 2026 ACM Workshop on Information Hiding and Multimedia Security},
  pages = {52–63},
  numpages = {12},
  location = {Firenze, Italy},
  series = {IH&MMSec '26}
}
```
---

# Overview

This repository provides the **reference Python implementation** and **characterization data** detailed in our study of Samsung NUAs (Non-Unique Artifacts).

<img src="figs/Samsung_NUA_patterns_timeline.svg" width="100%" alt="Samsung NUA patterns timeline">

**Key Resources Provided:**

- **NUA Patterns:** A dataset of 7 NUA patterns extracted from various Samsung devices (where Pattern 7 is a resized version of Pattern 6, denoted as $6^\dagger$).
- **Analysis Tools:** Python code encompassing:
  - Samsung NUAs autocorrelation mapping
  - SVD-based PRNU recovery algorithm
  - HDR-aware PRNU framework

Together, these resources facilitate the **reproduction of our experiments**, **evaluation of new image data**, and **analysis of Samsung NUA characteristics**.

***

*Implementation Note: Baseline PRNU-based source camera verification was executed using the Python port of the [Camera Fingerprint Program](https://dde.binghamton.edu/download/camera_fingerprint/).*

---

# Repository Structure
````
.
├── figs
│   ├── 01.svg
│   ├── 01_pattern_acorr_map.png
│   ├── 02.svg
│   ├── 03.svg
│   ├── 04.svg
│   ├── 05.svg
│   ├── 06.svg
│   ├── 06_dagger.svg
│   ├── quiver_plot.png
│   ├── Samsung_NUA_patterns_timeline.svg
├── LICENSE
├── README.md
├── requirements.txt
└── src
    └── SamsungNUAs_utils.py
````

---

# Samsung NUA patterns

The following **NUA patterns** were extracted from Samsung devices as described in the paper.

You can download individual patterns from the table below, or download the entire collection (including source images) as a ZIP archive [here](https://ggl.link/Sl7fNQJ).

|                           Pattern                            |  Resolution  |  Device   | Source Images                                                                     | Link                                 |
|:------------------------------------------------------------:|:------------:|:---------:|-----------------------------------------------------------------------------------|--------------------------------------|
|         <img src="figs/01.svg" width="50%" alt="01">         |  3024x4032   |    S10    | [D44 - Baracchi *et al.*, 2023](https://doi.org/10.1109/ACCESS.2023.3321991)      | [Download](https://ggl.link/UNpscLk) |
|         <img src="figs/02.svg" width="50%" alt="02">         |  3000x4000   |  vivoX60  | [D095 - Du *et al.*, 2025](https://doi.org/10.1109/ICASSP49660.2025.10890764)     | [Download](https://ggl.link/pRjB8h2) |
|         <img src="figs/03.svg" width="50%" alt="03">         |  3000x4000   |  A33 5G   | [A33 5G review](https://www.gsmarena.com/samsung_galaxy_a33_5g-review-2424p5.php) | Not publicly redistributable         |
|         <img src="figs/04.svg" width="50%" alt="04">         |  3468x4624   |  A53 5G   | Flickr references                                                                 | Not publicly redistributable         |
|         <img src="figs/05.svg" width="50%" alt="05">         |  3060x4080   |    A25    | [A25 review](https://www.gsmarena.com/samsung_galaxy_a25-review-2661p5.php)       | Not publicly redistributable         |
|         <img src="figs/06.svg" width="50%" alt="06">         |  3060x4080   |    A54    | [ZIP](https://ggl.link/zfC5ioV)                                                   | [Download](https://ggl.link/oNB9dV1) |
| <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |  3000x4000   |    A56    | [ZIP](https://ggl.link/1h3DsFm)                                                   | [Download](https://ggl.link/owOItL2) |

**Notes:** 

- Flickr images and the corresponding NUA pattern for the A53 5G are not redistributed due to licensing restrictions, as the images used are marked as "All rights reserved." We will attempt to collect redistributable images and, once available, will also share the corresponding NUA pattern.
- Images collected from [GSMArena](https://www.gsmarena.com/) are not redistributed due to copyright and licensing restrictions. Researchers interested in these images should obtain them directly from the corresponding links to the original website, in accordance with its terms of use.

All patterns are stored as **MATLAB (`.mat`)** files.

Example of loading an NUA pattern in Python:

```python
from scipy.io import loadmat

data = loadmat("/path/to/01_pattern_S10.mat")
F = data["Fingerprint"]
````

---
# Samsung NUA Patterns Autocorrelation

Example usage:
> **Note:** You can modify the `min_val` parameter. The paper uses a value of `400`, but it is set to `100` here to make the peaks easier to spot.
```python
from src.SamsungNUAs_utils import plot_autocorrelation

fingerprint_path = "/path/to/01_pattern_S10.mat"
plot_autocorrelation(fingerprint_path, min_val=100)
```

Expected Output:

<img src="figs/01_pattern_acorr_map.png" width="50%" alt="Autocorrelation of Pattern 1 (S10)">

---

# SVD-based PRNU recovery algorithm

Below is the high-level pseudocode of the recovery process:

```text
INPUT: 
    F           : Original NUA-affected Fingerprint matrix
    block_shape : Dimensions of the processing blocks (bH, bW)
    r           : Number of dominant singular values to suppress

OUTPUT:
    PRNU        : Recovered PRNU fingerprint matrix

BEGIN
    Initialize PRNU matrix with NaN values
    Identify unique block anchors along the top and left edges (k=0 or l=0)

    FOR EACH anchor point DO
        // 1. Trace diagonal blocks and construct observation matrix B
        Find valid non-overlapping blocks along the diagonal, then flatten them into columns of matrix B
        
        // 2. Apply SVD
        Compute SVD of B: [U, s, Vt] = SVD(B)
        
        // 3. Remove NUAs subspace
        Set the first r singular values in s to 0
        
        // 4. Reconstruct cleaned observation matrix
        Compute B_clean = U * s * Vt
        
        // 5. Construct the recovered PRNU
        Reshape the columns of B_clean back into 2D blocks
        Insert blocks into their original positions in the PRNU matrix
    END FOR

    Replace any remaining NaN elements in PRNU with 0
    RETURN PRNU
END
```

Example usage:
```python
from src.SamsungNUAs_utils import recover_prnu_svd

fingerprint_path = "/path/to/01_pattern_S10.mat"
PRNU = recover_prnu_svd(fingerprint_path, block_shape = (65, 60), r=9, b_save=True, save_dir='/tmp/')
```

Expected Output:
```text
[info]: Saved recovered PRNU fingerprint to /tmp/01_pattern_S10_SVD_9.mat
```

---

# HDR-aware PRNU framework

This module demonstrates how to integrate the SVD-based PRNU recovery algorithm with the HDR-aware framework for PRNU-based source camera verification.

Example usage:
> **Note:** To ensure this example runs out of the box, we include a custom Python implementation of the wavelet-based denoising filter. You may observe minor numerical differences compared to the figures reported in the original paper; recall that the paper's experiments were conducted using the Python port of the [Camera Fingerprint Program](https://dde.binghamton.edu/download/camera_fingerprint/).  
```python
import os
from src.SamsungNUAs_utils import recover_prnu_svd, HDR_aware_PRNU_verification

# ---- Parameters PRNU Recovery ----
fingerprint_path   = '/path/to/01_pattern_S10.mat'
block_shape        = (65, 60)
r                  = 9
b_save             = True
save_dir           = '/tmp'
b_verbose          = False

# ---- Run ----
PRNU = recover_prnu_svd(
    fingerprint_path   = fingerprint_path,
    block_shape        = block_shape,
    r                  = r,
    b_save             = b_save,
    save_dir           = save_dir,
    b_verbose          = b_verbose
)

# ---- Parameters HDR-aware framework ----
testImage_path   = '/path/to/D44_L1S6C2.jpg'
blockSize_HDR    = 256
b_plot_shifts    = True

HDR_aware_PRNU_verification(
    fingerprint_path   = fingerprint_path,
    PRNU_path          = os.path.join(save_dir,'01_pattern_S10_SVD_' + str(r) + '.mat'),
    image_path         = testImage_path,
    block_size         = blockSize_HDR,
    plot_shifts        = b_plot_shifts
)
```

Expected Output:
```text
[info]: Saved recovered PRNU fingerprint to /tmp/01_pattern_S10_SVD_9.mat
[info]: PCE w/o HDR synchronization 12.477 vs. PCE w/ HDR synchronization 3992.030 (reference: 01_pattern_S10_SVD_9).
```
<img src="figs/quiver_plot.png" width="100%" alt="Quiver plot">

---

# Requirements

Python ≥ 3.12

Required packages:
```
numpy
scipy
matplotlib
scikit-image
PyWavelets
pillow
```

Install:

```
pip install -r requirements.txt
```

---

# Image Dataset
The complete dataset, including released images from 5 devices, is available as a ZIP archive [here](https://ggl.link/zkg2SDR). The table below summarizes the availability and source of the images associated with each analyzed device. Note that the paper only includes devices up to SD20 and AD13; additional devices were added afterward. Cases where `Released Images < Total Images` indicate that some images were excluded due to privacy constraints (e.g., identifiable human faces) or licensing restrictions, as detailed below.

* **USA Version (Galaxy S Series)**

|  ID  | Model        | Version  |                           Pattern                            |   Reference <br> (Released / Total)   |     Test <br> (Released / Total)      | Availability        | Source                                                                                                |
|:----:|--------------|:--------:|:------------------------------------------------------------:|:-------------------------------------:|:-------------------------------------:|---------------------|-------------------------------------------------------------------------------------------------------|
|  —   | S9           | SM-G960U |                              —                               |                   —                   |                0 / 245                | Upon request        | [Iuliani *et al.*, 2021](https://doi.org/10.1109/ACCESS.2021.3070478)                                 |
|  —   | S9+          | SM-G965U |                              —                               |                   —                   |                0 / 257                | Upon request        | [Iuliani *et al.*, 2021](https://doi.org/10.1109/ACCESS.2021.3070478)                                 |
|  —   | S10          | SM-G973U |                              —                               |                   —                   |                0 / 133                | Upon request        | [Iuliani *et al.*, 2021](https://doi.org/10.1109/ACCESS.2021.3070478)                                 |
|  —   | S10+         | SM-G975U |                              —                               |                   —                   |                0 / 228                | Upon request        | [Iuliani *et al.*, 2021](https://doi.org/10.1109/ACCESS.2021.3070478)                                 |

* **Global Version (Galaxy S Series)**

|  ID  | Model        | Version  |                           Pattern                            |   Reference <br> (Released / Total)   |     Test <br> (Released / Total)      | Availability        | Source                                                                                                   |
|:----:|--------------|:--------:|:------------------------------------------------------------:|:-------------------------------------:|:-------------------------------------:|---------------------|----------------------------------------------------------------------------------------------------------|
| SD01 | S9           | SM-G960F |         <img src="figs/01.svg" width="50%" alt="01">         |                 0 / 5                 |                0 / 10                 | External            | [C14 - Albisani *et al.*, 2021](https://lesc.dinfo.unifi.it/PrnuModernDevices/C14/)                      |
| SD02 | S9           | SM-G960F |         <img src="figs/01.svg" width="50%" alt="01">         |                   —                   |                 0 / 9                 | External (GSMArena) | [S9 review](https://www.gsmarena.com/samsung_galaxy_s9-review-1734p7.php)                                |
| SD03 | S9+          | SM-G965F |         <img src="figs/01.svg" width="50%" alt="01">         |                 0 / 5                 |                0 / 10                 | External            | [C15 - Albisani *et al.*, 2021](https://lesc.dinfo.unifi.it/PrnuModernDevices/C15/)                      |
| SD04 | S9+          | SM-G965F |         <img src="figs/01.svg" width="50%" alt="01">         |                   —                   |                 0 / 9                 | External (GSMArena) | [S9+ review](https://www.gsmarena.com/samsung_galaxy_s9_plus-review-1736p7.php)                          |
| SD05 | S10          | SM-G973F |         <img src="figs/01.svg" width="50%" alt="01">         |                0 / 54                 |                0 / 108                | External            | [D44 - Baracchi *et al.*, 2023](https://lesc.dinfo.unifi.it/FloreView/Dataset/D44_Samsung_GalaxyS10/)    |
| SD06 | S10          | SM-G973F |         <img src="figs/01.svg" width="50%" alt="01">         | wide: 40 / 40 <br> telephoto: 20 / 20 | wide: 55 / 71 <br> telephoto: 34 / 41 | Direct download     | [ZIP](https://ggl.link/05vTXNl)                                                                          |
| SD07 | S10          | SM-G973F |         <img src="figs/01.svg" width="50%" alt="01">         |                   —                   |  wide: 0 / 10 <br> telephoto: 0 / 6   | External (GSMArena) | [S10 review](https://www.gsmarena.com/samsung_galaxy_s10-review-1903p7.php)                              |
| SD08 | S10+         | SM-G975F |         <img src="figs/01.svg" width="50%" alt="01">         |                0 / 32                 |                0 / 108                | External            | [D30 - Baracchi *et al.*, 2023](https://lesc.dinfo.unifi.it/FloreView/Dataset/D30_Samsung_GalaxyS10%2B/) |
| SD09 | S20          | SM-G980F |         <img src="figs/01.svg" width="50%" alt="01">         |                   —                   |                0 / 11                 | External (GSMArena) | [S20 review](https://www.gsmarena.com/samsung_galaxy_s20-review-2083p6.php)                              |
| SD10 | S20+         | SM-G985F |         <img src="figs/01.svg" width="50%" alt="01">         |                   —                   |                 0 / 8                 | External (GSMArena) | [S20+ review](https://www.gsmarena.com/samsung_galaxy_s20_plus-review-2088p6.php)                        |
| SD11 | S20 Ultra 5G | SM-G988B |         <img src="figs/02.svg" width="50%" alt="02">         |                   —                   |                0 / 18                 | External (GSMArena) | [S20 Ultra 5G review](https://www.gsmarena.com/samsung_galaxy_s20_ultra_5g-review-2074p6.php)            |
| SD12 | S21 5G       | SM-G991B |    <img src="figs/01.svg" width="50%" alt="01"><br>(HDR)     |                   —                   |                 0 / 6                 | External (GSMArena) | [S21 5G review](https://www.gsmarena.com/samsung_galaxy_s21-review-2218p5.php)                           |
| SD13 | S21+ 5G      | SM-G996B |    <img src="figs/01.svg" width="50%" alt="01"><br>(HDR)     |                   —                   |                 0 / 8                 | External (GSMArena) | [S21+ 5G review](https://www.gsmarena.com/samsung_galaxy_s21_plus_5g-review-2224p5.php)                  |
| SD14 | S22 Ultra 5G | SM-S908B |         <img src="figs/02.svg" width="50%" alt="02">         |                   —                   |                0 / 12                 | External (GSMArena) | [S22 Ultra 5G review](https://www.gsmarena.com/samsung_galaxy_s22_ultra-review-2382p6.php)               |
| SD15 | S24          | SM-G921B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                20 / 20                |                20 / 20                | Direct download     | [ZIP](https://ggl.link/3u9SDPx)                                                                          |
| SD16 | S24          | SM-G921B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                21 / 21                |                37 / 37                | Direct download     | [ZIP](https://ggl.link/krPtIx6)                                                                          |
| SD17 | S24          | SM-S921B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 12                 | External (GSMArena) | [S24 review](https://www.gsmarena.com/samsung_galaxy_s24-review-2663p5.php)                              |
| SD18 | S24+         | SM-S926B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 16                 | External (GSMArena) | [S24+ review](https://www.gsmarena.com/samsung_galaxy_s24_plus-review-2664p5.php)                        |
| SD19 | S24 FE       | SM-S721B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 15                 | External (GSMArena) | [S24 FE review](https://www.gsmarena.com/samsung_galaxy_s24_fe-review-2755p5.php)                        |
| SD20 | S25 FE       | SM-S731B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 18                 | External (GSMArena) | [S25 FE review](https://www.gsmarena.com/samsung_galaxy_s25_fe-review-2880p5.php)                        |
| SD21 | S26          | SM-S942B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 15                 | External (GSMArena) | [S26 review](https://www.gsmarena.com/samsung_galaxy_s26-review-2942p5.php)                              |
| SD22 | S26+         | SM-S947B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                   —                   |                0 / 15                 | External (GSMArena) | [S26+ review](https://www.gsmarena.com/samsung_galaxy_s26_plus-review-2941p5.php)                        |

* **Chinese Market Version (vivo X60 Series)**

|  ID  | Model        | Version |                   Pattern                    | Reference <br> (Released / Total) | Test <br> (Released / Total) | Availability | Source                                                                        |
|:----:|--------------|:-------:|:--------------------------------------------:|:---------------------------------:|:----------------------------:|--------------|-------------------------------------------------------------------------------|
| VD01 | vivo X60     |  China  | <img src="figs/02.svg" width="50%" alt="02"> |              0 / 170              |            0 / 82            | External     | [D095 - Du *et al.*, 2025](https://doi.org/10.1109/ICASSP49660.2025.10890764) |
| VD02 | vivo X60 Pro |  China  | <img src="figs/02.svg" width="50%" alt="02"> |              0 / 85               |            0 / 81            | External     | [D024 - Du *et al.*, 2025](https://doi.org/10.1109/ICASSP49660.2025.10890764) |

* **Galaxy Note Series**

|  ID  | Model       | Version  |                   Pattern                    | Reference <br> (Released / Total) | Test <br> (Released / Total) | Availability        | Source                                                                                      |
|:----:|-------------|:--------:|:--------------------------------------------:|:---------------------------------:|:----------------------------:|---------------------|---------------------------------------------------------------------------------------------|
| ND01 | Note9       | SM-N960F | <img src="figs/01.svg" width="50%" alt="01"> |                 —                 |            0 / 9             | External (GSMArena) | [Note9 review](https://www.gsmarena.com/samsung_galaxy_note9-review-1805p7.php)             |
| ND02 | Note10      | SM-N970F | <img src="figs/01.svg" width="50%" alt="01"> |                 —                 |            0 / 12            | External (GSMArena) | [Note10 review](https://www.gsmarena.com/samsung_galaxy_note10-review-1976p7.php)           |
| ND03 | Note10+     | SM-N975F | <img src="figs/01.svg" width="50%" alt="01"> |                 —                 |            0 / 12            | External (GSMArena) | [Note10+ review](https://www.gsmarena.com/samsung_galaxy_note10_plus-review-1972p7.php)     |
| ND04 | Note10 Lite | SM-N770F | <img src="figs/01.svg" width="50%" alt="01"> |                 —                 |            0 / 6             | External (GSMArena) | [Note10 Lite review](https://www.gsmarena.com/samsung_galaxy_note10_lite-review-2063p5.php) |

* **Galaxy A Series**

|  ID  | Model  | Version  |                           Pattern                            | Reference <br> (Released / Total) | Test <br> (Released / Total) | Availability        | Source                                                                            |
|:----:|--------|:--------:|:------------------------------------------------------------:|:---------------------------------:|:----------------------------:|---------------------|-----------------------------------------------------------------------------------|
| AD01 | A25    | SM-A256B |         <img src="figs/05.svg" width="50%" alt="05">         |                 —                 |            0 / 10            | External (GSMArena) | [A25 review](https://www.gsmarena.com/samsung_galaxy_a25-review-2661p5.php)       |
| AD02 | A26    | SM-A266B |         <img src="figs/06.svg" width="50%" alt="06">         |                 —                 |            0 / 10            | External (GSMArena) | [A26 review](https://www.gsmarena.com/samsung_galaxy_a26-review-2816p5.php)       |
| AD03 | A33 5G | SM-A336B |         <img src="figs/03.svg" width="50%" alt="03">         |                 —                 |            0 / 15            | External (GSMArena) | [A33 5G review](https://www.gsmarena.com/samsung_galaxy_a33_5g-review-2424p5.php) |
| AD04 | A35    | SM-A356B |         <img src="figs/06.svg" width="50%" alt="06">         |                 —                 |            0 / 9             | External (GSMArena) | [A35 review](https://www.gsmarena.com/samsung_galaxy_a35-review-2682p5.php)       |
| AD05 | A51 5G | SM-A516B |         <img src="figs/02.svg" width="50%" alt="02">         |                 —                 |            0 / 12            | External (GSMArena) | [A51 5G review](https://www.gsmarena.com/samsung_galaxy_a51_5g-review-2128p5.php) |
| AD06 | A53 5G | SM-A536B |         <img src="figs/04.svg" width="50%" alt="04">         |              0 / 12               |            0 / 14            | Flickr references   | Not publicly redistributable                                                      |
| AD07 | A53 5G | SM-A536B |         <img src="figs/04.svg" width="50%" alt="04">         |                 —                 |            0 / 9             | External (GSMArena) | [A53 5G review](https://www.gsmarena.com/samsung_galaxy_a53_5g-review-2406p5.php) |
| AD08 | A54    | SM-A546B |         <img src="figs/06.svg" width="50%" alt="06">         |               9 / 9               |           17 / 17            | Direct download     | [ZIP](https://ggl.link/cJEw9DS)                                                   |
| AD09 | A54    | SM-A546B |         <img src="figs/06.svg" width="50%" alt="06">         |                 —                 |            0 / 18            | External (GSMArena) | [A54 review](https://www.gsmarena.com/samsung_galaxy_a54-review-2546p5.php)       |
| AD10 | A55    | SM-A556B |         <img src="figs/06.svg" width="50%" alt="06">         |              0 / 22               |            0 / 19            | Flickr references   | Not publicly redistributable                                                      |
| AD11 | A55    | SM-A556B |         <img src="figs/06.svg" width="50%" alt="06">         |                 —                 |            0 / 25            | External (GSMArena) | [A55 review](https://www.gsmarena.com/samsung_galaxy_a55-review-2684p5.php)       |
| AD12 | A56    | SM-A566B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |              20 / 20              |           62 / 62            | Direct download     | [ZIP](https://ggl.link/6U7Chfu)                                                   |
| AD13 | A56    | SM-A566B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                 —                 |            0 / 13            | External (GSMArena) | [A56 review](https://www.gsmarena.com/samsung_galaxy_a56-review-2812p5.php)       |
| AD14 | A37    | SM-A376B |         <img src="figs/06.svg" width="50%" alt="06">         |                 —                 |            0 / 12            | External (GSMArena) | [A37 review](https://www.gsmarena.com/samsung_galaxy_a37-review-2952p5.php)       |
| AD15 | A57    | SM-A576B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                 —                 |            0 / 12            | External (GSMArena) | [A57 review](https://www.gsmarena.com/samsung_galaxy_a57-review-2950p5.php)       |

* **Galaxy Z Flip Series**

|  ID  | Model      | Version  |                           Pattern                            | Reference <br> (Released / Total) | Test <br> (Released / Total) | Availability        | Source                                                                                    |
|:----:|------------|:--------:|:------------------------------------------------------------:|:---------------------------------:|:----------------------------:|---------------------|-------------------------------------------------------------------------------------------|
| ZD01 | Z Flip7 FE | SM-F761B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                 —                 |            0 / 11            | External (GSMArena) | [Z Flip7 FE review](https://www.gsmarena.com/samsung_galaxy_z_flip7_fe-review-2861p5.php) |
| ZD02 | Z Flip7    | SM-F766B | <img src="figs/06_dagger.svg" width="50%" alt="06 (dagger)"> |                 —                 |            0 / 12            | External (GSMArena) | [Z Flip7 review](https://www.gsmarena.com/samsung_galaxy_z_flip7-review-2857p5.php)       |

**Notes**

- To comply with privacy and data protection regulations, including the [General Data Protection Regulation (GDPR)](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02016R0679-20160504), images containing identifiable human faces are excluded from the public release. As a result, the number of released images may differ from the values reported in Table 2 of the [paper](https://gpsc.uvigo.es/wp-content/uploads/2026/06/ihmmsec26_dvazquez_fperez.pdf).

- Flickr images are not redistributed due to licensing restrictions. All collected images are marked as "All rights reserved" and thus are excluded. In accordance with Flickr licensing terms, only images with permissive licenses (e.g., Creative Commons) can be redistributed.

- Images collected from [GSMArena](https://www.gsmarena.com/) are not redistributed due to copyright and licensing restrictions. Researchers interested in these images should obtain them directly from the corresponding links to the original website, in accordance with its terms of use.
 
- All GPS metadata was removed from the released images using [ExifTool](https://exiftool.org/) before publication.

---

# License

This project is licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0). See the `LICENSE` file for more details.

---

# Contact

For questions regarding the repository or the paper, please contact: David Vázquez-Padín ([dvazquez@gts.uvigo.es](mailto:dvazquez@gts.uvigo.es))