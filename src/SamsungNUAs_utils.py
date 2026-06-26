# Copyright 2026 David Vázquez-Padín
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
====================================================================
Samsung Non-Unique Artifacts (Samsung NUAs Utils)
====================================================================

Author:
    David Vázquez-Padín
    atlanTTic, Universidade de Vigo

Contact:
    dvazquez@gts.uvigo.es

Description:
    Utility functions for removing the Non-Unique Artifacts (NUAs)
    present in default Samsung PRNU (Photo Response Non-Uniformity)
    patterns using block-wise SVD suppression, as described in the
    paper:

    D. Vázquez-Padín and F. Pérez-González, "Beyond Non-Unique
    Artifacts: SVD-Based PRNU Recovery for Samsung Device
    Identification," in ACM Workshop on Information Hiding and
    Multimedia Security (IH&MMSec '26), June 17–19, 2026, Firenze,
    Italy. ACM, New York, NY, USA, 12 pages.
    https://doi.org/10.1145/3785353.3815090

====================================================================
"""
import os
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from PIL import Image
import pywt
from scipy.ndimage import uniform_filter
from skimage.util import view_as_blocks
from mpl_toolkits.axes_grid1 import make_axes_locatable

def recover_prnu_svd(
    fingerprint_path: str,
    block_shape: tuple = (65, 60),
    r: int = 9,
    b_save: bool = False,
    save_dir: str = None,
    b_verbose: bool = False
) -> np.ndarray:
    """ SVD-based PRNU recovery algorithm

    This function loads a Fingerprint and suppresses its dominant NUA components
    using block-wise SVD, returning a recovered PRNU fingerprint.

    Parameters
    ----------
    fingerprint_path: str   Path to the .mat file containing a 'Fingerprint' variable.
    block_shape     : tuple (height, width) of each processing block. Default (65, 60).
    r               : int   Number of leading singular values to suppress. Default 9.
    b_save          : bool  If True, save the recovered PRNU fingerprint to a .mat file.
    save_dir        : str   Directory for the output .mat file (required if b_save=True).
    b_verbose       : bool  If True, verbosity level is increased.

    Returns
    -------
    PRNU: np.ndarray Recovered PRNU fingerprint (same shape as input).
    """

    # ---- Load fingerprint ----
    prnu_name = os.path.splitext(os.path.basename(fingerprint_path))[0]
    F = sio.loadmat(fingerprint_path)['Fingerprint']   # original Fingerprint (containing NUAs)
    PRNU  = np.full(F.shape, np.nan)            # output Recovered PRNU

    bH, bW = block_shape
    H = F.shape[0] - bH + 1    # valid region height for block placement
    W = F.shape[1] - bW + 1    # valid region width  for block placement

    # ---- Generate block grid positions ----
    # Only the first row (k=0) and first column (l=0) are processed;
    # all other (k, l) pairs are redundant due to the diagonal tiling.
    k_vals = np.arange(0, F.shape[0] // bH - 14)
    l_vals = np.arange(0, F.shape[1] // bW - 15)

    L_grid, K_grid = np.meshgrid(l_vals, k_vals)
    mask   = (K_grid == 0) | (L_grid == 0)
    k_list = K_grid[mask]
    l_list = L_grid[mask]

    # ---- Process each (k, l) block origin ----
    for k, l in zip(k_list, l_list):
        if b_verbose:
            print(f'[info]: Processing block [{k}, {l}].')

        # Anchor point (0-based)
        p0_col = l * bW
        p0_row = k * bH

        # Build a diagonal grid of block positions from the anchor in both
        # directions, stepping by one block width/height at a time.
        n_left  = p0_col // bW
        n_right = (3 * W - p0_col) // bW
        steps   = np.arange(-n_left, n_right + 1)

        x1 = p0_col + steps * bW    # column positions
        y1 = p0_row + steps * bH    # row positions

        # Keep only positions within the valid image region
        pts   = np.column_stack([x1, y1])
        valid = (pts[:, 0] >= 0) & (pts[:, 0] < W) & \
                (pts[:, 1] >= 0) & (pts[:, 1] < H)
        pts   = pts[valid]

        cols      = pts[:, 0]
        rows      = pts[:, 1]
        numBlocks = len(rows)

        # Extract each block as a column of B
        B = np.zeros((bH * bW, numBlocks))
        for kk in range(numBlocks):
            block      = F[rows[kk]:rows[kk]+bH, cols[kk]:cols[kk]+bW]
            B[:, kk]   = block.ravel(order='F')

        # SVD: zero out the r dominant singular values to remove NUAs
        U, s, Vt = np.linalg.svd(B, full_matrices=False)
        s[:r] = 0
        B_clean  = U * s @ Vt

        # Write cleaned blocks back into the output pattern
        for kk in range(numBlocks):
            PRNU[rows[kk]:rows[kk]+bH, cols[kk]:cols[kk]+bW] = \
                B_clean[:, kk].reshape(block_shape, order='F')

    # ---- Diagnostics ----
    nan_fraction = np.isnan(PRNU).sum() / PRNU.size
    if b_verbose:
        print(f'[info]: NaN fraction after processing: {nan_fraction:.4f}')
    PRNU[np.isnan(PRNU)] = 0

    # ---- Optional save ----
    if b_save:
        if save_dir is None:
            raise ValueError('save_dir must be specified when b_save=True.')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f'{prnu_name}_SVD_{r}.mat')
        sio.savemat(save_path, {'Fingerprint': PRNU})
        print(f'[info]: Saved recovered PRNU fingerprint to {save_path}')

    return PRNU

def plot_autocorrelation(fingerprint_path, min_val):
    """Compute and visualize the 2D circular autocorrelation of a camera fingerprint.

    This function loads a computed camera reference PRNU fingerprint from a
    MATLAB file, evaluates its spatial autocorrelation plane using the
    Fourier convolution theorem.

    Parameters
    ----------
    fingerprint_path : str
        The file path to the source .mat file containing the extracted
        fingerprint matrix.
    min_val : int or float
        The symmetric viewport coordinate limit (in pixels) to crop the
        visualization around the zero-shift center peak.
    """
    # Load the structured data array from the MATLAB workspace file format.
    x = sio.loadmat(fingerprint_path)
    fingerprint = x["Fingerprint"]
    M, N = fingerprint.shape

    # Evaluate the 2D circular autocorrelation via the frequency domain.
    acorr = np.fft.fftshift(
        np.fft.ifft2(np.fft.fft2(fingerprint) * np.conj(np.fft.fft2(fingerprint)))
    ).real

    # Map linear index arrays to physical pixel-shift coordinate vectors.
    x_ax = np.arange(-N // 2, N // 2)
    y_ax = np.arange(-M // 2, M // 2)

    # Initialize the matplotlib plotting canvas, axes geometry, and the overlay grid
    fig, ax = plt.subplots()
    im = ax.pcolormesh(x_ax, y_ax, acorr, cmap="turbo")
    plt.colorbar(im, ax=ax)
    ax.grid(True, color="white", alpha=0.3, linewidth=0.5, linestyle="--")
    ax.set_aspect("equal")

    # Constrain the visualization boundaries to the localized window of interest.
    ax.set_xlim(-min_val, min_val)
    ax.set_ylim(-min_val, min_val)
    ax.invert_yaxis()

    # Render the figure
    plt.show()

def block_corrcoef(arr, block_size=(21, 21)):

    # Extract image dimensions and number of channels
    h, w, _ = arr.shape

    # Block height and width
    bh, bw = block_size

    # Block height and width
    H, W = h // bh, w // bw

    # Split image into non-overlapping blocks
    # Each block contains 2 channels (pattern and reference)
    blocks = np.squeeze(view_as_blocks(arr, block_shape=(bh, bw, 2)))  # shape: (H, W, bh, bw, 2)

    # Initialize correlation map
    cc = np.zeros((H, W), dtype=float)

    # Loop over blocks
    for i in range(H):
        for j in range(W):
            block = blocks[i, j, :, :, :]  # shape (bh, bw, 2)
            ch1 = block[:, :, 0].ravel()
            ch2 = block[:, :, 1].ravel()

            # Compute Pearson correlation coefficient
            r = np.corrcoef(ch1, ch2)[0, 1]

            cc[i, j] = r

    return cc


def denoise(image_path):
    """Extract the PRNU noise residual from a color image file.

    This function reads an image, processes each RGB channel individually
    using a spatially-adaptive wavelet filter, and combines the resulting
    channel-wise noise residuals into a single grayscale 2D array using
    standard linear luminance weights.

    Parameters
    ----------
    image_path : str
        The file path to the source image.

    Returns
    -------
    W : np.ndarray
        The 2D grayscale noise residual matrix of shape (H, W).
    """

    # Keep image in RGB [0, 255] for denoising
    image = np.array(Image.open(image_path).convert('RGB')).astype(np.float64)

    # Apply filter channel by channel (or convert to Grayscale/Y-channel if required)
    denoised = np.zeros_like(image)
    for c in range(image.shape[-1]):
        denoised[..., c] = denoise_channel(image[..., c], sigma=3.0, levels=4)

    # Extract the PRNU Noise Residual (W)
    W_rgb = image - denoised

    # Convert to Grayscale Residue
    weights = np.array([0.299, 0.587, 0.114])

    # Dot product across the last axis (channels) to get a 2D spatial matrix
    W = np.dot(W_rgb, weights)
    return W

def denoise_channel(image_channel, sigma=3.0, levels=4, window_size=9):
    """Apply a spatially-adaptive wavelet filter to a single image channel.

    The algorithm implements a Minimum Mean Square Error (MMSE) adaptive
    filter in the wavelet domain (Mihcak PRNU-based filter style). It models
    the subband coefficients as conditionally independent zero-mean Gaussian
    variables with a slowly varying spatial variance, allowing excellent
    decoupling of the high-frequency scene details from the sensor noise.

    Parameters
    ----------
    image_channel : np.ndarray
        A 2D matrix representing a single color channel, scaled to [0, 255].
    sigma : float, optional
        The assumed standard deviation of the additive white Gaussian noise.
        Default is 3.0.
    levels : int, optional
        The decomposition depth for the Discrete Wavelet Transform.
        Default is 4.
    window_size : int, optional
        The dimensions of the square moving window used to estimate local
        coefficient variance. Default is 9.

    Returns
    -------
    denoised_channel : np.ndarray
        The reconstructed, scene-retaining 2D matrix matching the input shape.
    """

    # 1. 2D Discrete Wavelet Transform using Symmlet 8
    coeffs = pywt.wavedec2(image_channel, wavelet='sym8', level=levels)

    # Global noise variance calculation
    sigma_sq = sigma ** 2

    # Processed coefficients container
    processed_coeffs = [coeffs[0]]  # Keep approximation (LL) coefficients as-is

    # 2. Iterate through detail subbands (LH, HL, HH) at each level
    for level_coeffs in coeffs[1:]:
        processed_level = []
        for subband in level_coeffs:
            # Estimate local variance of the subband using a moving window
            # Local mean of squares
            local_mean_sq = uniform_filter(subband ** 2, size=window_size, mode='reflect')

            # Estimated local signal variance: max(0, Var(Y) - Var(Noise))
            local_var = np.maximum(0, local_mean_sq - sigma_sq)

            # Wiener-like adaptive scaling factor
            # Where local_var is high (edges/texture), scaling approaches 1 (keeps detail)
            # Where local_var is low (smooth areas), scaling drops, zeroing out the signal
            scaling_factor = local_var / (local_var + sigma_sq + 1e-10)

            # Denoised coefficients
            denoised_subband = subband * scaling_factor
            processed_level.append(denoised_subband)

        processed_coeffs.append(tuple(processed_level))

    # 3. Inverse DWT to get the clean host image estimate
    denoised_channel = pywt.waverec2(processed_coeffs, wavelet='sym8')

    # Match exact dimensions if padding/cropping occurred in waverec2
    denoised_channel = denoised_channel[:image_channel.shape[0], :image_channel.shape[1]]

    return denoised_channel

def pce_own(X1, X2):
    """
    Compute the Peak-to-Correlation Energy (PCE) between two 2D arrays
    using normalized cross-correlation in the frequency domain.

    The PCE quantifies how strongly the correlation energy is
    concentrated at the zero-shift position (origin) relative to the
    surrounding noise floor, and is a standard metric for PRNU-based
    source camera identification.

    Note: this variant evaluates the peak strictly at the zero-shift
    location (index 0 of the un-shifted correlation), without searching
    for the global maximum. It is primarily intended as a quick
    zero-shift PCE check.

    Parameters
    ----------
    X1 : np.ndarray
        First 2D input array (e.g. image noise residual).
    X2 : np.ndarray
        Second 2D input array (e.g. predicted PRNU contribution).

    Returns
    -------
    pce : float
        Peak-to-Correlation Energy evaluated at zero shift. Returns 0 if
        the noise energy is negligible.
    """

    # Cross-correlation via the Fourier convolution theorem:
    # IFFT(FFT(X1) * conj(FFT(X2))) gives the circular cross-correlation.
    # The fftshift version centers the zero-shift peak in the array.
    numerator = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(X1) * np.conj(np.fft.fft2(X2))))
    # Un-shifted version: index (0, 0) corresponds to zero shift.
    num = np.fft.ifft2(np.fft.fft2(X1) * np.conj(np.fft.fft2(X2)))

    # Normalization factor (equivalent to sum(X(:).^2) in MATLAB).
    denom = np.sqrt(np.sum(X1 ** 2) * np.sum(X2 ** 2))

    # Avoid division by zero when either input is all-zero.
    if denom == 0:
        C = np.zeros_like(numerator)
    else:
        C = (1 / denom) * numerator

    # Magnitude of the normalized correlation surface (fftshift-centered),
    # used for the noise-energy estimate.
    C_abs = np.abs(C)
    # Magnitude of the normalized correlation surface (un-shifted),
    # used to evaluate the peak at zero shift.
    C2 = np.abs((1 / denom) * num)

    # The "peak" is taken at the zero-shift location, i.e. element (0, 0)
    # of the un-shifted correlation surface.
    peak_idx = 0
    max_val = C2.flat[peak_idx]

    # Convert the linear peak index to (row, col) coordinates in the
    # fftshift-centered correlation surface.
    ypeak, xpeak = np.unravel_index(peak_idx, C.shape)
    radius = 5
    h, w = C.shape

    # Build a mask covering the whole correlation plane (True = used for
    # noise statistics), then exclude a (2*radius+1) x (2*radius+1)
    # neighborhood around the peak from the noise estimate.
    mask = np.ones((h, w), dtype=bool)

    y_min = max(0, ypeak - radius)
    y_max = min(h, ypeak + radius + 1)  # +1: Python ranges are end-exclusive
    x_min = max(0, xpeak - radius)
    x_max = min(w, xpeak + radius + 1)

    mask[y_min:y_max, x_min:x_max] = False

    # Energy of the correlation peak.
    peak_energy = max_val ** 2

    # Average energy of the correlation surface outside the peak
    # neighborhood, used as the noise floor estimate.
    noise_energy = np.mean(C_abs[mask] ** 2)

    # PCE = peak energy / noise energy, signed by the sign of the peak.
    pce = 0
    if noise_energy >= 1e-10:
        pce = (peak_energy / noise_energy) * np.sign(max_val)

    return pce


def return_shift(X1, X2):
    """
    Estimate the PCE and the spatial shift between two 2D arrays using
    normalized cross-correlation in the frequency domain.

    Unlike `pce_own`, this function searches for the global maximum of
    the cross-correlation surface and, if the resulting PCE is high
    enough (>= 30, the standard PRNU detection threshold), returns the
    corresponding (row, col) shift between the two inputs.

    Parameters
    ----------
    X1 : np.ndarray
        First 2D input array (e.g. image noise residual).
    X2 : np.ndarray
        Second 2D input array (e.g. predicted PRNU contribution).

    Returns
    -------
    pce : float
        Peak-to-Correlation Energy at the detected peak. Returns 0 if
        the noise energy is negligible.
    ind : np.ndarray or None
        Estimated (row, col) shift between X1 and X2 if `pce >= 30`,
        otherwise None.
    """

    # Cross-correlation via the Fourier convolution theorem, centered
    # with fftshift so that zero shift corresponds to the array center.
    numerator = np.fft.fftshift(np.fft.ifft2(np.fft.fft2(X1) * np.conj(np.fft.fft2(X2))))

    # Normalization factor (equivalent to sum(X(:).^2) in MATLAB).
    denom = np.sqrt(np.sum(X1 ** 2) * np.sum(X2 ** 2))

    # Avoid division by zero when either input is all-zero.
    if denom == 0:
        C = np.zeros_like(numerator)
    else:
        C = (1 / denom) * numerator

    # Work with the magnitude to handle small complex residuals when
    # locating the peak.
    C_abs = np.abs(C)

    # Locate the global maximum of the (un-normalized) cross-correlation
    # magnitude.
    peak_idx = np.argmax(np.abs(numerator))
    max_val = C_abs.flat[peak_idx]

    # Convert the linear peak index to (row, col) coordinates.
    ypeak, xpeak = np.unravel_index(peak_idx, C.shape)
    radius = 5
    h, w = C.shape

    # Build a mask covering the whole correlation plane (True = used for
    # noise statistics), then exclude a (2*radius+1) x (2*radius+1)
    # neighborhood around the peak from the noise estimate.
    mask = np.ones((h, w), dtype=bool)

    y_min = max(0, ypeak - radius)
    y_max = min(h, ypeak + radius + 1)  # +1: Python ranges are end-exclusive
    x_min = max(0, xpeak - radius)
    x_max = min(w, xpeak + radius + 1)

    mask[y_min:y_max, x_min:x_max] = False

    # Energy of the correlation peak.
    peak_energy = max_val ** 2

    # Average energy of the correlation surface outside the peak
    # neighborhood, used as the noise floor estimate.
    noise_energy = np.mean(C_abs[mask] ** 2)

    # PCE = peak energy / noise energy, signed by the sign of the peak.
    pce = 0
    if noise_energy >= 1e-10:
        pce = (peak_energy / noise_energy) * np.sign(max_val)

    # Only report a shift if the detection is statistically significant
    # (PCE >= 30 is the conventional PRNU detection threshold).
    if pce >= 30:
        ind = np.array([(C.shape[0] / 2) - ypeak, (C.shape[1] / 2) - xpeak]).astype(np.int64)
    else:
        ind = None

    return pce, ind


def process_block(block1, block2, block3):
    """
    Estimate the PCE and spatial shift for a single image block.

    Parameters
    ----------
    block1 : np.ndarray
        Block of the query image's noise residual.
    block2 : np.ndarray
        Corresponding block of the query image (grayscale intensities).
    block3 : np.ndarray
        Corresponding block of the reference camera fingerprint/pattern.

    Returns
    -------
    pce : float
        Peak-to-Correlation Energy for this block.
    shift : np.ndarray or None
        Estimated (row, col) shift for this block if `pce >= 30`,
        otherwise None.
    """
    # Correlate the noise residual against the fingerprint scaled by the
    # image intensity (the expected PRNU contribution).
    pce, shift = return_shift(block1, np.multiply(block2, block3))

    return pce, shift


def process_array_in_blocks(arr, Ix, pattern, PRNU, block_size):
    """
    Re-align a camera fingerprint to a query image on a per-block basis.

    The query image's noise residual `arr` is divided into non-overlapping
    `block_size` x `block_size` blocks. For each block, the local shift
    between the residual and the reference fingerprint `pattern` is
    estimated via `process_block`. If the block-level detection is
    significant (PCE >= 30), the corresponding region of `PRNU` is
    re-sampled according to the estimated shift, producing a spatially
    realigned fingerprint `PRNU_rec`. Blocks without a significant
    detection are left unchanged (copied from `PRNU`).

    This compensates for local geometric misalignments between the
    camera fingerprint and the query image (e.g. due to HDR fusion,
    cropping, or other content-dependent warping).

    Parameters
    ----------
    arr : np.ndarray
        2D noise residual of the query image (e.g. from wavelet
        denoising).
    Ix : np.ndarray
        2D grayscale intensity array of the query image, same shape as
        `arr`.
    pattern : np.ndarray
        2D reference camera fingerprint used to estimate local shifts,
        same shape as `arr`.
    PRNU : np.ndarray
        2D fingerprint to be spatially realigned (e.g. a candidate
        device fingerprint), same shape as `arr`.
    block_size : int
        Side length (in pixels) of the square blocks used for local
        shift estimation.

    Returns
    -------
    PRNU_rec : np.ndarray
        Copy of `PRNU` with regions corresponding to significant local
        detections re-sampled according to the estimated per-block
        shifts.
    shifts : dict
        Mapping from block top-left corner (i, j) to the estimated
        (row, col) shift `np.ndarray` for that block, or `None` if the
        block had no significant detection (PCE < 30), indicating an
        effective shift of (0, 0).
    """
    h, w = arr.shape
    N = block_size

    # Output starts as a copy of the input fingerprint; only blocks with
    # a significant detection are modified below.
    PRNU_rec = PRNU.copy()

    # Per-block shifts, keyed by the block's top-left corner (i, j).
    # Used later for visualization (see `plot_block_shifts`).
    shifts = {}

    # Iterate over non-overlapping NxN blocks covering the full image.
    for i in range(0, h, N):
        for j in range(0, w, N):
            block1 = arr[i:i + N, j:j + N]       # query noise residual block
            block2 = Ix[i:i + N, j:j + N]         # query intensity block
            block3 = pattern[i:i + N, j:j + N]    # reference fingerprint block

            block_PCE, shift = process_block(block1, block2, block3)

            if block_PCE >= 30.0:
                shifts[(i, j)] = shift

                # Compute the source region in PRNU corresponding to this
                # block, offset by the estimated shift, clipped to the
                # image bounds.
                i0 = max(0, i + shift[0])
                i1 = min(h, i + shift[0] + N)
                j0 = max(0, j + shift[1])
                j1 = min(w, j + shift[1] + N)

                # Adjust the source region size if it would exceed the
                # image bounds, so source and destination shapes match.
                if j + (j1 - j0) - w > 0:
                    j1 = w + j0 - j
                if i + (i1 - i0) - h > 0:
                    i1 = h + i0 - i

                # Copy the shifted fingerprint region into the output.
                PRNU_rec[i:i + (i1 - i0), j:j + (j1 - j0)] = PRNU[i0:i1, j0:j1]
            else:
                # No significant detection: record as None, indicating an
                # effective shift of (0, 0). Used later for visualization
                # (see `plot_block_shifts`).
                shifts[(i, j)] = None

    return PRNU_rec, shifts


def plot_block_shifts(image_path, W, pattern, shifts, block_size, arrow_length=None):
    """
    Visualize per-block estimated shifts as a quiver plot overlaid on the
    full-color query image and the local NCC map between its residue and
    the default fingerprint (containing NUAs).

    For each block:
      - If a shift was detected (PCE >= 30), a red arrow is drawn from the
        block center pointing in the direction of the estimated (row, col)
        shift, and the numeric shift value is annotated in black text as
        (col, row). Arrow directions are normalized to a fixed display
        length (only the direction is shown), so that small shifts remain
        visible.
      - If no shift was detected (`shifts[(i, j)] is None`), a red dot is
        drawn at the block center, indicating an effective shift of
        (0, 0).

    A grid with spacing `block_size` is also drawn to indicate block
    boundaries.

    Parameters
    ----------
    image_path : str
        Path to the query image file. The image is loaded in full color
        (RGB) and used as the background.
    W : np.ndarray
        2D noise residual of the query image (e.g. from wavelet
        denoising).
    pattern : np.ndarray
        2D reference camera fingerprint used to estimate local shifts,
        same shape as `W`.
    shifts : dict
        Mapping from block top-left corner (i, j) to the estimated
        (row, col) shift `np.ndarray`, or `None` for blocks with no
        significant detection, as returned by `process_array_in_blocks`.
    block_size : int
        Side length (in pixels) of the square blocks used for shift
        estimation. Used to draw the grid and to locate block centers.
    arrow_length : float, optional
        Fixed display length (in pixels) for all arrows, regardless of
        the magnitude of the estimated shift. Only the direction of the
        shift is preserved; this keeps small shifts visible. Defaults to
        `block_size * 0.6` if not provided.

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
        The created figure and axes, for further customization if needed.
    """
    # Load the query image in full color for the background.
    image = np.array(Image.open(image_path).convert('RGB'))

    h, w = image.shape[:2]
    N = block_size

    if arrow_length is None:
        arrow_length = N * 0.6

    # Compute and smooth local NCC map
    cc = block_corrcoef(np.stack((W, pattern), axis=-1))
    cc[np.isnan(cc)] = 0
    NCCmap = uniform_filter(cc, size=5, mode='reflect')

    # Choose figure size preserving aspect ratio
    max_dim = 10
    if w > h:
        # Horizontal
        figsize = (max_dim, max_dim * (h / w))
    else:
        # Vertical
        figsize = (max_dim * (w / h), max_dim)
    fig, ax = plt.subplots(figsize=figsize)

    # Full-color background image.
    ax.imshow(image)

    # Overlay NCC map
    im = ax.imshow(NCCmap, alpha=0.7, extent=(0, w, h, 0))

    # Draw a grid with spacing `block_size` to indicate block boundaries.
    for x in range(0, w + 1, N):
        ax.axvline(x=x, color='white', linewidth=0.5, alpha=0.5, linestyle='--')
    for y in range(0, h + 1, N):
        ax.axhline(y=y, color='white', linewidth=0.5, alpha=0.5, linestyle='--')

    # Draw an arrow (or dot) + text label for each block.
    for (i, j), shift in shifts.items():
        # Block center in (x, y) = (col, row) image coordinates.
        cx = j + N / 2
        cy = i + N / 2

        if shift is None:
            # No significant detection: mark the effective (0, 0) shift
            # with a red dot.
            ax.plot(cx, cy, marker='o', color='red', markersize=3)

            ax.text(
                cx, cy + N / 6,
                '(0, 0)',
                color='black',
                fontsize=8,
                ha='center',
                va='top',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.6, edgecolor='none'),
            )
            continue

        dy, dx = shift[0], shift[1]  # true (row, col) shift, for the label

        # Normalize the displayed arrow to a fixed length, preserving
        # only its direction, so small shifts stay visible. A zero
        # vector (dy == dx == 0) has no direction, so draw a dot instead.
        norm = np.hypot(dx, dy)
        if norm == 0:
            ax.plot(cx, cy, marker='o', color='xkcd:apple green', markersize=3)
        else:
            ux, uy = dx / norm, dy / norm  # unit direction
            ax.annotate(
                '',
                xy=(cx + ux * arrow_length, cy + uy * arrow_length),
                xytext=(cx, cy),
                arrowprops=dict(arrowstyle='->', color='red', linewidth=1.5),
            )

        # Black text label showing the true numeric shift (col, row).
        ax.text(
            cx, cy + N / 6,
            f'({dx}, {dy})',
            color='black',
            fontsize=8,
            ha='center',
            va='top',
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.6, edgecolor='none'),
        )

    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)  # keep image (row 0 at top) orientation
    ax.set_title('Per-block estimated translation parameters $(t_1, t_2)$')

    # Add colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.2)
    plt.colorbar(im, cax=cax, label='NCC')
    ax.set_axis_off()

    fig.tight_layout()
    fig.savefig("/tmp/quiver_plot.png", dpi=150, format="png", bbox_inches="tight")
    plt.show()

    return fig, ax

def HDR_aware_PRNU_verification(
    fingerprint_path,
    PRNU_path,
    image_path,
    block_size=256,
    plot_shifts=False
):
    """
    Run the full HDR-aware PRNU verification pipeline on a query image.

    The pipeline:
      1. Loads a reference camera fingerprint and a candidate device
         fingerprint from .mat files.
      2. Loads the query image and converts it to grayscale.
      3. Extracts the image's noise residual via wavelet denoising.
      4. Computes a baseline PCE using the candidate fingerprint as-is.
      5. Spatially realigns the candidate fingerprint on a per-block
         basis (to compensate for local misalignments such as those
         introduced by HDR processing) and recomputes the PCE using the
         realigned fingerprint.

    Parameters
    ----------
    fingerprint_path : str
        Path to a .mat file containing the reference camera fingerprint
        under the key 'Fingerprint'. Used to estimate local shifts.
    PRNU_path : str
        Path to a .mat file containing the candidate device fingerprint
        under the key 'Fingerprint'. This is the fingerprint that gets
        spatially realigned.
    image_path : str
        Path to the query image file.
    block_size : int, optional
        Side length (in pixels) of the square blocks used for local
        shift estimation (default: 256).
    plot_shifts : bool, optional
        If True, generate a quiver-style plot of the per-block estimated
        shifts overlaid on the query image (default: False).

    Returns
    -------
    pce_before : float
        PCE computed using the candidate fingerprint without spatial
        realignment.
    pce_after : float
        PCE computed using the candidate fingerprint after per-block
        spatial realignment.
    shifts : dict
        Mapping from block top-left corner (i, j) to the estimated
        (row, col) shift for blocks with a significant detection
        (PCE >= 30).
    """

    # Load the reference fingerprint, used to drive the local shift
    # estimation.
    reference_data = sio.loadmat(fingerprint_path)
    pattern = reference_data['Fingerprint']

    # Load the candidate device fingerprint, which will be realigned.
    candidate_data = sio.loadmat(PRNU_path)
    Fingerprint = candidate_data['Fingerprint']

    PRNU_ref = PRNU_path.split('/')[-1].split('.')[0]

    # Load the query image and convert to grayscale.
    Ix = np.array(Image.open(image_path).convert('L'))

    W = denoise(image_path)

    # Spatially realign the candidate fingerprint to compensate for local
    # misalignments (e.g. from HDR fusion), using the reference fingerprint
    # to estimate per-block shifts.
    PRNU_rec, shifts = process_array_in_blocks(W, Ix, pattern, Fingerprint, block_size)

    # Baseline PCE: candidate fingerprint without realignment.
    pce_before = pce_own(W, np.multiply(Ix, Fingerprint))

    # PCE after per-block spatial realignment of the candidate fingerprint.
    pce_after = pce_own(W, np.multiply(Ix, PRNU_rec))

    # Print information
    print(f'[info]: PCE w/o HDR synchronization {pce_before:.3f} vs. PCE w/ HDR synchronization {pce_after:.3f} (reference: {PRNU_ref}).')

    # Optionally visualize the estimated per-block shifts over the
    # full-color image.
    if plot_shifts:
        plot_block_shifts(image_path, W, pattern, shifts, block_size)

    return pce_before, pce_after, shifts


def main():
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

if __name__ == '__main__':
    main()
