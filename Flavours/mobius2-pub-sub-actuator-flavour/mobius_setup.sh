#!/bin/bash

rm conf.json

echo '{"csebaseport":"7579","dbpass":"fed4iot"}' > conf.json

sed -i 's/Mobius2/Mobius/g' mobius.js

sed -i '21s/^/CREATE DATABASE IF NOT EXISTS mobiusdb;\nUSE mobiusdb\n/' mobius/mobiusdb.sql

sed -i 's/Sponde/Superman/g' app.js  

sed -e 's/utf8mb4_0900_ai_ci/utf8mb4_unicode_ci/g' -i mobius/mobiusdb.sql

sed -i '250s/./\/\/&/' mobius/sgn.js

rm mobius/sql_action.js
cp /app/sql_action.js mobius/

service mysql start
mysql -u root -pfed4iot < /app/fixroot.sql
service mysql stop
