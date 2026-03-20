def fib_dynamic(n, memo=None):
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fib_dynamic(n - 1, memo) + fib_dynamic(n - 2, memo)
    return memo[n]