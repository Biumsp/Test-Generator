n = 0

while n < 20:

    print(n)
    n += 2

    if n % 3 != 0:
        continue

    elif n == 15:
        n += 3
        break

    n += 1

print(n)