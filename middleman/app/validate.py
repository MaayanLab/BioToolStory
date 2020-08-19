import requests
from jsonschema import Draft4Validator, RefResolver
import json
import re
from collections import deque

cached = {}


def resolve_validator(val):
    regex = "^\/@?dcic\/signature-commons-schema(\/v\d+)?(.*)$"
    if val in cached:
        return cached[val]
    url = val
    m = re.search(regex,url)
    if m:
        m = m.groups()
        url = "https://raw.githubusercontent.com/dcic/signature-commons-schema%s%s"%(m[0],m[1])
    res = requests.get(url)
    if not res.ok:
        raise Exception(res.text)
    else:
        cached[val] = res.json()
        return cached[val]


def initialize_resolver():
    validator = resolve_validator("/dcic/signature-commons-schema/v5/core/signature.json")
    return RefResolver("https://raw.githubusercontent.com/MaayanLab/signature-commons-schema",
                       validator,
                       cache_remote=True)


def jsonify_error(error):
    return json.dumps(error.__dict__, default=lambda o: list(o) if type(o)==deque else str(o))


def validate(entry, validator_url, resolver):
    try:
        validator = resolver.resolve(validator_url)
    except Exception as e:
        return json.dumps({"error": "Cannot resolve validator %s"%validator})
    validator = Draft4Validator(validator[1], resolver=resolver)
    errors = validator.iter_errors(entry)
    try:
        error = next(errors)
        return jsonify_error(error)
    except StopIteration as e:
        return


def validate_entry(entry, resolver):
    # core
    validator = entry.get("$validator", "")
    error = validate(entry, validator, resolver)
    if error:
        return error
    # meta
    entry = entry["meta"]
    validator = entry.get("$validator", "")
    error = validate(entry, entry["$validator"], resolver)
    if error:
        return error
    return