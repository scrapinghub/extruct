import json
import sys

_json_decoder = json.loads
_json_decoder_raises = tuple()  # Better not to catch built-in errors at all!
def set_json_decoder(loader_func=_json_decoder,
                     loader_raises=_json_decoder_raises):
    """
    Sets extruct's preferred JSON decoder function.

    You should provide a function that accepts strings, and returns decoded
    native objects, as loader_func.

    When your preferred decoder encounters non-JSON strings, or malformed JSON,
    typically it will raise Exceptions. Extruct expects json.JSONDecodeError
    in such cases. If your preferred decoder does something else (such as the
    ValueErrors raised by ujson), provide a tuple of all Exception classes
    raised on bad JSON or non-JSON.
    """
    global _json_decoder
    global _json_decoder_raises
    _json_decoder = loader_func
    _json_decoder_raises = loader_raises


def json_loads(json_string):
    """
    Uses the preferred JSON decoder (default is stdlib json) to decode a string,
    converting any idiosyncratic exceptions to json.JSONDecodeError.

    Using this utility function allows one to swap in different decoders with
    utils.set_json_decoder, for example to use `ujson`, without requiring
    extruct to directly handle and support the weirdnesses of each third-party
    json library.
    """
    # Does this need `global _json_decoder` to prevent reference capture and failure-to-switch?
    try:
        data = _json_decoder(json_string)
    except _json_decoder_raises as E:
        # TODO: Deprecate with Python 2. Reason: Prefer exception chaining with `raise from`
        _, _, traceback = sys.exc_info()
        if sys.version_info < (3,):
            if isinstance(E, ValueError):
                raise
            else:
                raise ValueError("Error decoding document: {}".format(traceback))
        else:
            if isinstance(E, json.JSONDecodeError):
                raise
            else:
                raise json.JSONDecodeError(
                    msg="Error decoding document (error index unknown, see preceding traceback)",
                    doc=json_string,
                    pos=0,
                    ).with_traceback(traceback)
    return data
