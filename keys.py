from bitvector_demo import Sbox
import copy


def generate_keys() -> list:
    # read the key from the file
    file = open('key.txt', 'r')
    key = file.read()
    file.close()
    key = key.encode('utf-8')

    if len(key) < 16:
        for i in range(16 - len(key)):
            key += ' '.encode('utf-8')

    if len(key) > 16:
        key = key[:16]

    # print(len(key))

    words = []
    for i in range(0, len(key), 4):
        temp = []
        for j in range(4):
            temp.append((hex(key[i + j])[2:]))
        words.append(temp)

    roc = 0
    for i in range(4, 44):
        temp = []
        for j in range(4):
            temp.append(words[i - 1][j])
        if i % 4 == 0:
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
    # print(len(roundkeys))
    return roundkeys
