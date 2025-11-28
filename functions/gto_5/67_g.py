i = 0

print(i)
while i < 100:
    print(i)
    for j in range(4):
        if j % 2 != 0:
            i += j

print(i)