def function11(n = 5):

    i = 6

    while i > n:

        if i % 2 == 0:
            i += 1
        else:
            i += 3

        print(f"i: {i}")

        if i > 3 and i <= 12:
            continue

        if i == 10:
            break

        if i == 15:
            return i

    return n

print(function11())