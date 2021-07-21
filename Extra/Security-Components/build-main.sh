#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

cd authentication; ./create_certs.sh; cd ../
cd authorisation/Py_CapabilityManagerWebService; ./build.sh; cd ../../
cd authorisation/XACML_PAP_PDP; ./build.sh; cd ../../
cd authorisation/Py_PEP-Proxy; ./build.sh; cd ../../
