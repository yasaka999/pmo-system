# -*- coding: utf-8 -*-
# coding=utf-8
import base64
import rsa

__all__ = ['rsa_encrypt']


def _str2key(s):
    # 对字符串解码
    b_str = base64.b64decode(s)

    if len(b_str) < 162:
        return False

    hex_str = ''

    # 按位转换成16进制
    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h

    # 找到模数和指数的开头结束位置
    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2

    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]

    return modulus, exponent


def rsa_encrypt(s, pubkey_str):
    '''
    rsa加密
    :param s:
    :param pubkey_str:公钥
    :return:
    '''
    key = _str2key(pubkey_str)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    pubkey = rsa.PublicKey(modulus, exponent)
    return base64.b64encode(rsa.encrypt(s.encode(), pubkey)).decode()


key = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCAcWAd4QD8DLPc3Txrf/oSVB93tSR0EHvFZjT5H8ehaI7jsOQ7F60GaG3BRKOKFKZ46wipp8UFzIg84walJcj7jRHAKx8cUtPB8d8ghwsRQF9UjKO/drdghfoERfOhd9hYpvjFasMyT+54EtoIG8rysKxrCe4tBYeP5VSzhaAtCwIDAQAB'
password = rsa_encrypt('admin', key)
print(password)
