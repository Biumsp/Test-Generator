def function11(n):

    i = 6

    while i <= n:

        i += 3
        print(f"i: {i}")

        if i > 5 and i <= 10:
            continue

        if i == 15:
            break

    return n

print(function11(18))