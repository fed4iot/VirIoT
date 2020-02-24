git clone https://github.com/IoTKETI/Mobius.git

git checkout tags/2.4.0

vim conf.json
```bash
{
    "csebaseport": "7579",
    "dbpass": "fed4iot"
}
```

vim mobius/mobiusdb.sql

```bash

CREATE DATABASE IF NOT EXISTS mobiusdb;
USE mobiusdb

... 
```

vim mobius.json

replace global.usecseid variable from:
```bash
from
global.usecseid             = '/Mobius2';

to
global.usecseid             = '/Mobius';
```