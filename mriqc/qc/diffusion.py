# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright 2021 The NiPreps Developers <nipreps@gmail.com>
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
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#

import numpy as np


"""
Image quality metrics for diffusion MRI data
============================================
"""

import numpy as np
from dipy.core.gradients import gradient_table
from dipy.core.gradients import GradientTable
from dipy.reconst.dti import TensorModel
from dipy.denoise.noise_estimate import piesno

def get_spike_mask(data, grouping_vals, z_threshold=3):
    """
    Return binary mask of spike/no spike

def noise_func(img, gtab):
    pass



def noise_b0(data, gtab, mask=None):
    """
    Estimate noise in raw dMRI based on b0 variance.

    Parameters
    ----------
    """
    if mask is None:
        mask = np.ones(data.shape[:3], dtype=bool)
    b0 = data[..., ~gtab.b0s_mask]
    return np.percentile(np.var(b0[mask], -1), (25, 50, 75))


def noise_piesno(data, n_channels=4):
    """
    Estimate noise in raw dMRI data using the PIESNO [1]_ algorithm.


    Parameters
    ----------

    Returns
    -------


    Notes
    -----

    .. [1] Koay C.G., E. Ozarslan, C. Pierpaoli. Probabilistic Identification
           and Estimation of Noise (PIESNO): A self-consistent approach and
           its applications in MRI. JMR, 199(1):94-103, 2009.
    """
    sigma, mask = piesno(data, N=n_channels, return_mask=True)
    return sigma, mask


def cc_snr(data, gtab):
    """
    Calculate worse-/best-case signal-to-noise ratio in the corpus callosum

    Parameters
    ----------
    data : ndarray

    gtab : GradientTable class instance or tuple

    """
    if isinstance(gtab, GradientTable):
        pass

    # XXX Per-shell calculation
    tenmodel = TensorModel(gtab)
    tensorfit = tenmodel.fit(data, mask=mask)

    from dipy.segment.mask import segment_from_cfa
    from dipy.segment.mask import bounding_box

    threshold = (0.6, 1, 0, 0.1, 0, 0.1)
    CC_box = np.zeros_like(data[..., 0])

    mins, maxs = bounding_box(mask)
    mins = np.array(mins)
    maxs = np.array(maxs)
    diff = (maxs - mins) // 4
    bounds_min = mins + diff
    bounds_max = maxs - diff

    CC_box[bounds_min[0]:bounds_max[0],
        bounds_min[1]:bounds_max[1],
        bounds_min[2]:bounds_max[2]] = 1

    mask_cc_part, cfa = segment_from_cfa(tensorfit, CC_box, threshold,
                                        return_cfa=True)

    mean_signal = np.mean(data[mask_cc_part], axis=0)
