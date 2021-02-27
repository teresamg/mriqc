from os import path as op

import nibabel as nib
import numpy as np
from mriqc import config, messages
from mriqc.interfaces import data_types
from nipype.interfaces.base import (
    BaseInterfaceInputSpec,
    File,
    SimpleInterface,
    TraitedSpec,
    traits,
)

OUT_FILE = "{prefix}_conformed{ext}"
NUMPY_DTYPE = {
    1: np.uint8,
    2: np.uint8,
    4: np.uint16,
    8: np.uint32,
    64: np.float32,
    256: np.uint8,
    1024: np.uint32,
    1280: np.uint32,
    1536: np.float32,
}


class ConformImageInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc="input image")
    check_ras = traits.Bool(True, usedefault=True, desc="check that orientation is RAS")
    check_dtype = traits.Bool(True, usedefault=True, desc="check data type")


class ConformImageOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc="output conformed file")


class ConformImage(SimpleInterface):
    f"""
    Conforms an input image.

    List of nifti datatypes:

    .. note: Original Analyze 7.5 types

       {data_types.ANALYZE_75}

    .. note: Added names for the same data types

       {data_types.ADDED}

    .. note: New codes for NIFTI

       {data_types.NEW_CODES}

    """

    input_spec = ConformImageInputSpec
    output_spec = ConformImageOutputSpec

    def _warn_suspicious_dtype(self, dtype: int) -> None:
        if dtype == 1:
            dtype_message = messages.SUSPICIOUS_DATA_TYPE.format(
                in_file=self.inputs.in_file, dtype=dtype
            )
            config.loggers.interface.warning(dtype_message)

    def _check_dtype(self, nii: nib.Nifti1Image) -> nib.Nifti1Image:
        header = nii.header.copy()
        datatype = int(header["datatype"])
        self._warn_suspicious_dtype(datatype)
        try:
            dtype = NUMPY_DTYPE[datatype]
        except KeyError:
            return nii
        else:
            header.set_data_dtype(dtype)
            converted = nii.get_data().astype(dtype)
            return nib.Nifti1Image(converted, nii.affine, header)

    def _run_interface(self, runtime):
        # Squeeze 4th dimension if possible (#660)
        nii = nib.squeeze_image(nib.load(self.inputs.in_file))

        if self.inputs.check_ras:
            nii = nib.as_closest_canonical(nii)

        if self.inputs.check_dtype:
            nii = self._check_dtype(nii)

        # Generate name
        out_file, ext = op.splitext(op.basename(self.inputs.in_file))
        if ext == ".gz":
            out_file, ext2 = op.splitext(out_file)
            ext = ext2 + ext
        out_file_name = OUT_FILE.format(prefix=out_file, ext=ext)
        self._results["out_file"] = op.abspath(out_file_name)
        nii.to_filename(self._results["out_file"])

        return runtime
