# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
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
# 
# Soft Rasterizer (SoftRas)
# 
# Copyright (c) 2017 Hiroharu Kato
# Copyright (c) 2018 Nikos Kolotouros
# Copyright (c) 2019 Shichen Liu
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import torch
import torch.nn.functional as F


def look_at(vertices, eye, at=[0, 0, 0], up=[0, 1, 0]):
    """
    "Look at" transformation of vertices.
    """
    if (vertices.ndimension() != 3):
        raise ValueError('vertices Tensor should have 3 dimensions')

    device = vertices.device

    # if list or tuple convert to numpy array
    if isinstance(at, list) or isinstance(at, tuple):
        at = torch.tensor(at, dtype=torch.float32, device=device)
    # if numpy array convert to tensor
    elif isinstance(at, np.ndarray):
        at = torch.from_numpy(at).to(device)
    elif torch.is_tensor(at):
        at.to(device)

    if isinstance(up, list) or isinstance(up, tuple):
        up = torch.tensor(up, dtype=torch.float32, device=device)
    elif isinstance(up, np.ndarray):
        up = torch.from_numpy(up).to(device)
    elif torch.is_tensor(up):
        up.to(device)

    if isinstance(eye, list) or isinstance(eye, tuple):
        eye = torch.tensor(eye, dtype=torch.float32, device=device)
    elif isinstance(eye, np.ndarray):
        eye = torch.from_numpy(eye).to(device)
    elif torch.is_tensor(eye):
        eye = eye.to(device)

    batch_size = vertices.shape[0]
    if eye.ndimension() == 1:
        eye = eye[None, :].repeat(batch_size, 1)
    if at.ndimension() == 1:
        at = at[None, :].repeat(batch_size, 1)
    if up.ndimension() == 1:
        up = up[None, :].repeat(batch_size, 1)

    # create new axes
    # eps is chosen as 1e-5 to match the chainer version
    z_axis = F.normalize(at - eye, eps=1e-5)
    x_axis = F.normalize(torch.cross(up, z_axis), eps=1e-5)
    y_axis = F.normalize(torch.cross(z_axis, x_axis), eps=1e-5)

    # create rotation matrix: [bs, 3, 3]
    r = torch.cat((x_axis[:, None, :], y_axis[:, None, :], z_axis[:, None, :]), dim=1)

    # apply
    # [bs, nv, 3] -> [bs, nv, 3] -> [bs, nv, 3]
    if vertices.shape != eye.shape:
        eye = eye[:, None, :]
    vertices = vertices - eye
    vertices = torch.matmul(vertices, r.transpose(1,2))

    return vertices
