ERR_INPUT_NBACK_OVERMAX = "'N' is too many value (> 100)."
ERR_INPUT_NBACK_NO_INPUT = "'N' has no value."
ERR_INPUT_NBACK_NOT_INT = "'N' should be inteagers."
ERR_INPUT_NBACK_INVALID = "'N' is invalid."
ERR_INPUT_NBACK_LESS_THEN_NBACK = "'T' should be greater than 'N' value."


class InputError(BaseException):
    pass


class SignalAlarmTimeOut(BaseException):
    pass

