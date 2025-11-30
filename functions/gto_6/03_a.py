n = 0

while n < 20:

    print(n)

    if n == 3:
        continue
        n += 2

    elif n == 5:
        n += 3
        continue

    n += 1

print(n)