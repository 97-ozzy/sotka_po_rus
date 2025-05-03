def blur_username(username):
    encode = username[1:-1]
    encode = [encode[i] if i%2==0 else '*' for i in range(len(encode))]
    encode = ''.join(encode)
    encode = username[0]+encode+username[-1]
    return encode

print('f4030319', blur_username('f4030319'))
