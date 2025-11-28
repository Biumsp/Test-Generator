def function11(i = 2, n = 15):

    while i <= n:

        if i % 2 == 0:
            i += 1
        else:
            i += 3

        print(f"i: {i}")

        if i > 3 and i <= 12:
            continue

        if i == 10:
            break

        if i == 16:
            return i

    return n

print(function11(-3, 18))