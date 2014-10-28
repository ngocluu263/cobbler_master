import inspect
import types

DEPRECATED_FIELDS = {
    "subnet": "netmask",
    "bonding": "interface_type",
    "bonding_master": "interface_master",
}

def replace_deprecate_field(data):
    """replace keys that cobbler deprecate in data

    :data: @todo
    :returns: @todo

    """
    f = inspect.stack()[0][3]
    for k, v in data.iteritems():
        if '-' in k:
            data[k.replace('-', '_')] = data[k]# No zuo, No die!
            del data[k]

        if k in DEPRECATED_FIELDS.keys():
            data[DEPRECATED_FIELDS[k]] = data[k]
            del data[k]

        if type(v) == types.DictionaryType:
            replace_deprecate_field(v)

def main():
    a = {
        "a-b": {
            "subnet": 1111
            }
        }
    replace_deprecate_field(a)
    print a


if __name__ == '__main__':
    main()
