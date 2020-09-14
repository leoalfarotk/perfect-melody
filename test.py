import collections

test = {
    'test': 980.42,
    'test2': 179.12,
    'test3': 413.42,
}

result = collections.OrderedDict({k: v for k, v in sorted(test.items(), key=lambda item: item[1])})

print(test)

for key, value in result.items():
    print(value, key)
