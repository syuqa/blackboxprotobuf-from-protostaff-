Скрипт раскодировки данных в формате protostaff без модели с помощью библиотеки blackboxprotobuf.
Необходимл Установить библиотеки blackboxprotobuf, struct (pip install struct blackboxprotobuf)

SQL
```sql
select encode(data_b::bytea, 'hex') from table limit 1;
```

Python

```python
import json
from decode_data_b import PaserDataByterrayForMapping
# простой пример
data = r'<hex>'

parser = PaserDataByterrayForMapping(data)
result = perser.parse()
print(json.dumps(result, indent=4))
```
