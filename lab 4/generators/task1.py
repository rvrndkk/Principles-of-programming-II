def squr(N):
    for i in range(N + 1):
        yield i ** 2

N = int(input())
for square in squr(N):
    print(square, end=" ")
