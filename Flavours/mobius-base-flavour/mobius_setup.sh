#!/bin/bash

rm conf.json

echo '{"csebaseport":"7579","dbpass":"fed4iot"}' > conf.json

sed -i 's/Mobius2/Mobius/g' mobius.js

sed -i '21s/^/CREATE DATABASE IF NOT EXISTS mobiusdb;\nUSE mobiusdb\n/' mobius/mobiusdb.sql
