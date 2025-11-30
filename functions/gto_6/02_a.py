n = 10

while n < 20:

    print(n)
    if n % 3 == 0:
        n += 3
        continue

    elif n % 2 == 1:
        n += 2
        break

    print(n)
    n -= 1

print(n)