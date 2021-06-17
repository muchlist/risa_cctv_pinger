def output_error(err_msg: str) -> bool:
    if err_msg == "b''":
        return False
    return True


def output_success(msg: str, err_msg: str) -> int:

    if output_error(err_msg):
        return -1

    if "100%" in msg:
        return 0
    elif "87%" in msg:
        return 1
    elif "75%" in msg:
        return 1
    elif "62%" in msg:
        return 1
    elif "50%" in msg:
        return 1
    elif "37%" in msg:
        return 2
    elif "25%" in msg:
        return 2
    elif "12%" in msg:
        return 2
    elif "0%" in msg:
        return 2
    return 0
