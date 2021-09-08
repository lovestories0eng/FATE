#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from federatedml.param.base_param import BaseParam, deprecated_param
from federatedml.param.intersect_param import DHParam
from federatedml.util import consts, LOGGER


@deprecated_param("key_size")
class SecureInformationRetrievalParam(BaseParam):
    """
    security_level: float [0, 1]; if security_level == 0, then do raw data retrieval

    oblivious_transfer_protocol: OT type, only supports OT_Hauck

    commutative_encryption: the commutative encryption scheme used, only supports CommutativeEncryptionPohligHellman

    non_committing_encryption: the non-committing encryption scheme used, only supports aes

    dh_params: params for Pohlig-Hellman Encryption

    key_size: int, value >= 1024, the key length of the commutative cipher;
        note that this param will be deprecated in future, please specify key_length in PHParam instead.

    raw_retrieval: bool, perform raw retrieval if raw_retrieval

    target_cols: str or list of str, target cols to retrieve;
        any values not retrieved will be marked as "unretrieved",
        if target_cols is None, label will be retrieved, same behavior as in previous version
        default None

    """
    def __init__(self, security_level=0.5,
                 oblivious_transfer_protocol=consts.OT_HAUCK,
                 commutative_encryption=consts.CE_PH,
                 non_committing_encryption=consts.AES,
                 key_size=consts.DEFAULT_KEY_LENGTH,
                 dh_params=DHParam(),
                 raw_retrieval=False,
                 target_cols=None):
        super(SecureInformationRetrievalParam, self).__init__()
        self.security_level = security_level
        self.oblivious_transfer_protocol = oblivious_transfer_protocol
        self.commutative_encryption = commutative_encryption
        self.non_committing_encryption = non_committing_encryption
        self.dh_params = dh_params
        self.key_size = key_size
        self.raw_retrieval = raw_retrieval
        self.target_cols = [] if target_cols is None else target_cols

    def check(self):
        descr = "secure information retrieval param's "
        self.check_decimal_float(self.security_level, descr+"security_level")
        self.oblivious_transfer_protocol = self.check_and_change_lower(self.oblivious_transfer_protocol,
                                                                       [consts.OT_HAUCK.lower()],
                                                                       descr + "oblivious_transfer_protocol")
        self.commutative_encryption = self.check_and_change_lower(self.commutative_encryption,
                                                                  [consts.CE_PH.lower()],
                                                                  descr + "commutative_encryption")
        self.non_committing_encryption = self.check_and_change_lower(self.non_committing_encryption,
                                                                     [consts.AES.lower()],
                                                                     descr + "non_committing_encryption")
        if self._warn_to_deprecate_param("key_size", descr, "dh_param's key_length"):
            """
            self.check_positive_integer(self.key_size, descr+"key_size")
            if self.key_size < 1024:
                raise ValueError(f"key size must be >= 1024")
            """
            self.dh_params.key_length = self.key_size
        self.dh_params.check()
        self.check_boolean(self.raw_retrieval, descr)
        if self.raw_retrieval:
            LOGGER.warning(f"SIR param 'raw_retrieval' will be deprecated in future release, "
                           f"please set security_level = 0 to perform raw retrieval.")
        if not isinstance(self.target_cols, list):
            self.target_cols = [self.target_cols]
        for col in self.target_cols:
            self.check_string(col, descr+"target_cols")
        if len(self.target_cols) == 0:
            LOGGER.warning(f"Both 'target_cols' and 'target_indexes' are empty. Label will be retrieved.")
