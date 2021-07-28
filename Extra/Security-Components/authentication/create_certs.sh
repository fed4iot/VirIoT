#
#Copyright Odin Solutions S.L. All Rights Reserved.
#
#SPDX-License-Identifier: Apache-2.0
#

#!/bin/bash

rm -Rf certs;
rm -Rf fiware-idm;
git clone https://github.com/ging/fiware-idm.git;
cd fiware-idm; ./generate_openssl_keys.sh;
mv certs/ ../;
rm -Rf fiware-idm;
cd ../
