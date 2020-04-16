def encrypt(data, code):
    data = bytearray(data)
    for index, value in enumerate(data):
        data[index] = value ^ code
    return data


def decrypt(data, code):
    return encrypt(data, code)
