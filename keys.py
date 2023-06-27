import binascii
import time

from bitvector_demo import Sbox
import copy


def generate_keys(bits=128) -> list:
    cur_time = time.time()
    # read the key from the file
    file = open('key.txt', 'r', encoding="utf-8")
    key = file.read()
    print("\nKey:")
    print("In ASCII:", key)
    file.close()
    key = key.encode('utf-8')
    print("In HEX:", binascii.hexlify(key))
    keylen = (bits // 8)
    columns = keylen // 4
    if len(key) < keylen:
        for i in range(keylen - len(key)):
            key += ' '.encode('utf-8')

    if len(key) > keylen:
        key = key[:keylen]

    # print(len(key))

    words = []
    for i in range(0, keylen, 4):
        temp = []
        for j in range(4):
            temp.append((hex(key[i + j])[2:]))
        words.append(temp)

    roc = 0
    if columns == 4:
        total = 44
    elif columns == 6:
        total = 52
    else:
        total = 60

    for i in range(columns, total):
        temp = []
        for j in range(4):
            temp.append(words[i - 1][j])
        if columns == 8 and i % columns == 4:
            for j in range(4):
                temp[j] = Sbox[int(temp[j], 16)]
                temp[j] = hex(temp[j] ^ int(words[i - columns][j], 16))[2:]
        elif i % columns == 0:
            # print(temp)
            temp = temp[1:] + temp[:1]

            # find the rounding constant
            d = i // 4
            if d <= 8:
                const = 2 ** roc
            else:
                if d == 9:
                    const = 0x1B
                else:
                    const = 0x36
            Roc = [const, 0, 0, 0]
            roc += 1

            # print(temp)
            for j in range(4):
                temp[j] = Sbox[int(temp[j], 16)]
                temp[j] = int(temp[j]) ^ Roc[j]
                # print(hex(temp[j]))
                temp[j] = hex(temp[j] ^ int(words[i - columns][j], 16))[2:]

            # print(temp)
        else:
            for j in range(4):
                temp[j] = hex(int(temp[j], 16) ^ int(words[i - columns][j], 16))[2:]
            # print(temp)
        words.append(temp)

    # print(words[:4])

    roundkeys = []
    if columns == 4:
        key_num = 11
    elif columns == 6:
        key_num = 13
    else:
        key_num = 15

    for i in range(key_num):
        temp = [[], [], [], []]
        for j in range(4):
            for k in range(4):
                temp[k].append(words[4 * i + j][k])
        roundkeys.append(temp)

    print('Total number of round keys:', len(roundkeys))
    elapsed_time = time.time() - cur_time
    print("\nTime taken to generate keys:", elapsed_time, "seconds")
    return roundkeys
