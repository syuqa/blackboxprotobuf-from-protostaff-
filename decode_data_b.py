# -*- coding: utf-8 -*-
import blackboxprotobuf
import struct
import json

from datetime import datetime



class PaserDataByterrayForMapping:
    def __init__(self, data_b) -> None:
        # #print(data_b)
        self.somebytes = data_b.replace(r'\xa', '')
        self.barray = bytearray.fromhex(self.somebytes)
        self.jsonpb = blackboxprotobuf.decode_message(self.barray)
        self.data = self.jsonpb[0]
        self.model = self.jsonpb[1]
        print(self.data)


    def group(self, group_typedef, data, _data_object={}):
        data_object = _data_object
        types = {}
        for index, propertyes in group_typedef.items():
            types[index] = propertyes.get("type")

        # Одноуровневые структуры
        if [*types.values()].count('bytes') == 2 or len([*types.values()]) == 2 and [*types.values()].count(
                'bytes') == 1 and [*types.values()].count('group') == 0:
            items = self.parse_data(data, [*types.keys()])
            data_object = {**data_object, **items}

        # Многоуровневые структуры
        if [*types.values()].count('group') == 1:
            group_index = [*types.values()].index('group')
            group_name = [*types.keys()][group_index]
            items_ = self.parse_data(data, [*types.keys()])
            for key, value in items_.items():
                if not isinstance(value, dict) and not isinstance(value, list):
                    data_object = {**data_object, **items_}
                else:
                    group = group_typedef.get(group_name)
                    group_typedef_ = group.get('group_typedef')
                    value_ = self.group(group_typedef_, value)
                    data_object[key] = value_
        elif [*types.values()].count('group') == 2:
            data_object = []
            for group in data:
                container_data_object = []
                for key, value in group.items():
                    _group_typedef = group_typedef.get(key)
                    container_data_object.append(self.group(_group_typedef.get('group_typedef'), value))
                data_object.append(container_data_object)

        return data_object

    def decode_date(self, data):
        try:
            if len(data) == 6:
                decode_data = struct.unpack_from('!iBB', data)
                return '.'.join([str(b) for b in decode_data])
            elif len(data) == 13:
                decode_data = struct.unpack_from('!iiBBBBB', data)
                return datetime(decode_data[0], decode_data[2], decode_data[3], decode_data[4], decode_data[5],
                                decode_data[6]).strftime("%Y-%m-%d, %H:%M:%S")
        except (struct.error, ValueError, IndexError) as e:
            return str(e)

    def data_decode(self, data):
        if isinstance(data, bytearray):
            try:
                return data.decode()
            except Exception as e:
                return self.decode_date(data)
        else:
            return data

    def parse_data(self, data, indexses):
        result = {}

        if isinstance(data, list):
            for line in data:
                if len(indexses) == 2:
                    l1 = self.data_decode(line.get(indexses[0]))
                    l2 = self.data_decode(line.get(indexses[1]))
                    if isinstance(l1, str):
                        result[l1] = l2
                    else:
                        result[l2] = l1
        elif isinstance(data, dict):
            d1 = self.data_decode(data.get(indexses[0]))
            d2 = self.data_decode(data.get(indexses[1]))
            if isinstance(d1, str):
                result[d1] = d2
            else:
                result[d2] = d1

        return result

    def parse(self):
        data = self.data
        data_object = {}
        for index, propertyes in self.model.items():
            if propertyes.get("type") == 'group':
                _data = self.group(propertyes.get('group_typedef'), data.get(index), data_object)
                data_object = {**data_object, **_data}
        return data_object

    def parse_to_json(self):
        return json.dumps(self.parse())
