def lua_table_string(obj, indent=0):
    INDENT = "    "
    def is_lua_identifier(s):
        return isinstance(s, str) and s.replace('_', '').isalnum() and (s[0].isalpha() or s[0] == '_')

    def is_primitive(val):
        return isinstance(val, (str, int, float, bool)) or val is None

    def is_simple_dict(d):
        return isinstance(d, dict) and all(is_primitive(v) for v in d.values())

    def lua_key(k):
        if is_lua_identifier(k):
            return k
        else:
            return f'[{lua_table_string(str(k))}]'

    if isinstance(obj, dict):
        if is_simple_dict(obj):
            items = []
            for k, v in obj.items():
                # Skip empty lists or dicts
                if v == {} or v == []:
                    continue
                items.append(f'{lua_key(k)} = {lua_table_string(v, 0)}')
            return '{ ' + ', '.join(items) + ' }'
        else:
            items = []
            for k, v in obj.items():
                # Skip empty lists or dicts
                if v == {} or v == []:
                    continue
                items.append(f'{INDENT * (indent+1)}{lua_key(k)} = {lua_table_string(v, indent+1)}')
            if not items:
                return '{}'
            return '{\n' + (',\n'.join(items)) + f'\n{INDENT * indent}}}'
    elif isinstance(obj, list):
        # If all elements are simple dicts, put each on its own line, single-line style
        if all(is_simple_dict(v) for v in obj):
            items = [f'{INDENT * (indent+1)}{lua_table_string(v, 0)}' for v in obj]
            return '{\n' + (',\n'.join(items)) + f'\n{INDENT * indent}}}'
        else:
            items = [f'{INDENT * (indent+1)}{lua_table_string(v, indent+1)}' for v in obj]
            return '{\n' + (',\n'.join(items)) + f'\n{INDENT * indent}}}'
    elif isinstance(obj, str):
        s = obj.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{s}"'
    elif obj is None:
        return "nil"
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    else:
        return str(obj)
