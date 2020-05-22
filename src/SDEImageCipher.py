def encrypt(data, code):
    code = int(code)
    data = bytearray(data)
    for index, value in enumerate(data):
        data[index] = value ^ 10
    return data


def decrypt(data, code):
    return encrypt(data, code)
