import numpy as np
from collections import namedtuple

csvdtype = np.dtype([('name', 'U16'), ('lat', 'f4'), ('filter', 'i4')])
x = np.array([('x', 3.4, 1), ('y', 1.2, 5)], dtype=csvdtype)
print(type(x['name']))


def load():
    MyData = namedtuple('MyData', ['name', 'lat', 'filter'])
    csvdata = [('x', 3.4, 1), ('y', 1.2, 5)]
    result = []
    for data in csvdata:
        x = MyData(*data)
        result.append(x)
    return result


typemap = {
    'real': float,
    'text': str,
    'int': int,
}


def load_file(filename):
    with open(filename, 'r') as f:
        names = next(f).strip().split(';')
        types = next(f).strip().split(';')
        converters = [typemap[typename] for typename in types]
        print(converters)
        MyData = namedtuple('MyData', names)
        result = []
        for line in f:
            textvalues = line.strip().split(';')
            values = []
            for converter, textvalue in zip(converters, textvalues):
                values.append(converter(textvalue))

            result.append(MyData(*values))
    return result


def name_index(mydata):
    return {data.name: data for data in mydata}


print('--- load')
mydata = load()
print(mydata[0].name)
print(mydata[0].lat)


print('--- load_file')
mydata = load_file('data.csv')
print(mydata[0].name)
print(mydata[0].lat)

name_indexed_data = name_index(mydata)
print(name_indexed_data['x'])

def name_filter(name):
    def func(data):
        return data.name == name
    return func

print(list(filter(lambda data: data.name == 'x', mydata)))
print([data for data in mydata if data.name == 'x'])
