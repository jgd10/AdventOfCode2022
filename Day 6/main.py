def find_first_marker(message):
    for i in range(len(message)-4):
        packet = {j for j in message[i:i+4]}
        if len(packet) == 4:
            return i + 4


def find_first_message(message):
    for i in range(len(message)-14):
        packet = {j for j in message[i:i+14]}
        if len(packet) == 14:
            return i + 14


with open('input.txt', 'r') as f:
    m = f.read()

print(find_first_marker(m))
print(find_first_message(m))

