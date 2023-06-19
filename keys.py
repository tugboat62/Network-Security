from bitvector_demo import Roc, Sbox
import copy


def generate_keys() -> list:
    # read the key from the file
    file = open('key.txt', 'r')
    key = file.read()
    file.close()
    key = 'Thats my Kung Fu'
    key = key.encode('utf-8')

    if len(key) < 16:
        for i in range(16 - len(key)):
            key += ' '.encode('utf-8')

    if len(key) > 16:
        key = key[:16]

    words = []
    for i in range(0, len(key), 4):
        temp = []
        for j in range(4):
            temp.append((hex(key[i + j])[2:]))
        words.append(temp)

    for i in range(4, 44):
        temp = []
        for j in range(4):
            temp.append(words[i - 1][j])
        if i % 4 == 0:
            # print(temp)
            temp = temp[1:] + temp[:1]
            # print(temp)
            for j in range(4):
                temp[j] = Sbox[int(temp[j], 16)]
                temp[j] = temp[j] ^ Roc[j]
                # print(hex(temp[j]))
                temp[j] = hex(temp[j] ^ int(words[i - 4][j], 16))[2:]

            # print(temp)
        else:
            for j in range(4):
                temp[j] = hex(int(temp[j], 16) ^ int(words[i - 4][j], 16))[2:]
            # print(temp)
        words.append(temp)

    # print(words[:4])

    roundkeys = []
    for i in range(11):
        temp = [[], [], [], []]
        for j in range(4):
            for k in range(4):
                temp[k].append(words[4 * i + j][k])
        roundkeys.append(temp)
    # print(roundkeys[0])
    return roundkeys
