def function11(n = 20):

    i = 6

    while i < n:

        i += 3
        print(f"i: {i}")

        if i > 5 and i <= 10:
            continue

        if i == 18:
            break

    return n

print(function11())