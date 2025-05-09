# Copyright 2023-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
from typing import List

# Common utilities for model generation scripts
import numpy as np

np_dtype_string = np.dtype(object)

# Numpy does not support the BF16 datatype natively.
# We use this dummy dtype as a representative for BF16.
np_dtype_bfloat16 = np.dtype([("bf16", object)])


def np_to_onnx_dtype(np_dtype):
    import onnx

    if np_dtype == bool:
        return onnx.TensorProto.BOOL
    elif np_dtype == np.int8:
        return onnx.TensorProto.INT8
    elif np_dtype == np.int16:
        return onnx.TensorProto.INT16
    elif np_dtype == np.int32:
        return onnx.TensorProto.INT32
    elif np_dtype == np.int64:
        return onnx.TensorProto.INT64
    elif np_dtype == np.uint8:
        return onnx.TensorProto.UINT8
    elif np_dtype == np.uint16:
        return onnx.TensorProto.UINT16
    elif np_dtype == np.float16:
        return onnx.TensorProto.FLOAT16
    elif np_dtype == np.float32:
        return onnx.TensorProto.FLOAT
    elif np_dtype == np.float64:
        return onnx.TensorProto.DOUBLE
    elif np_dtype == np_dtype_string:
        return onnx.TensorProto.STRING
    return None


def np_to_model_dtype(np_dtype):
    if np_dtype == bool:
        return "TYPE_BOOL"
    elif np_dtype == np.int8:
        return "TYPE_INT8"
    elif np_dtype == np.int16:
        return "TYPE_INT16"
    elif np_dtype == np.int32:
        return "TYPE_INT32"
    elif np_dtype == np.int64:
        return "TYPE_INT64"
    elif np_dtype == np.uint8:
        return "TYPE_UINT8"
    elif np_dtype == np.uint16:
        return "TYPE_UINT16"
    elif np_dtype == np.float16:
        return "TYPE_FP16"
    elif np_dtype == np.float32:
        return "TYPE_FP32"
    elif np_dtype == np.float64:
        return "TYPE_FP64"
    elif np_dtype == np_dtype_string:
        return "TYPE_STRING"
    elif np_dtype == np_dtype_bfloat16:
        return "TYPE_BF16"
    return None


def np_to_trt_dtype(np_dtype):
    import tensorrt as trt

    if np_dtype == bool:
        return trt.bool
    elif np_dtype == np.int8:
        return trt.int8
    elif np_dtype == np.int32:
        return trt.int32
    elif np_dtype == np.int64:
        return trt.int64
    elif np_dtype == np.uint8:
        return trt.uint8
    elif np_dtype == np.float16:
        return trt.float16
    elif np_dtype == np.float32:
        return trt.float32
    elif np_dtype == np_dtype_bfloat16:
        return trt.bfloat16
    return None


def np_to_torch_dtype(np_dtype):
    import torch

    if np_dtype == bool:
        return torch.bool
    elif np_dtype == np.int8:
        return torch.int8
    elif np_dtype == np.int16:
        return torch.int16
    elif np_dtype == np.int32:
        return torch.int
    elif np_dtype == np.int64:
        return torch.long
    elif np_dtype == np.uint8:
        return torch.uint8
    elif np_dtype == np.uint16:
        return None  # Not supported in Torch
    elif np_dtype == np.float16:
        return None
    elif np_dtype == np.float32:
        return torch.float
    elif np_dtype == np.float64:
        return torch.double
    elif np_dtype == np_dtype_string:
        return List[str]
    return None


def openvino_save_model(model_version_dir, model):
    import openvino as ov

    # W/A for error moving to OpenVINO new APIs "Attempt to get a name for a Tensor without names".
    # For more details, check https://github.com/triton-inference-server/openvino_backend/issues/89
    if len(model.outputs) == 0:
        model.outputs[0].get_tensor().set_names({"OUTPUT"})
    else:
        for idx, out in enumerate(model.outputs):
            out.get_tensor().set_names({f"OUTPUT{idx}"})

    os.makedirs(model_version_dir, exist_ok=True)
    ov.serialize(
        model, model_version_dir + "/model.xml", model_version_dir + "/model.bin"
    )
