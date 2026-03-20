import time

# 🔁 Recursivo com contador de chamadas
calls_recursive = 0

def fib_recursive(n):
    global calls_recursive
    calls_recursive += 1

    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


# 🧠 Dinâmico (memoization) com contador
calls_dynamic = 0

def fib_dynamic(n, memo=None):
    global calls_dynamic

    if memo is None:
        memo = {}

    calls_dynamic += 1

    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fib_dynamic(n - 1, memo) + fib_dynamic(n - 2, memo)
    return memo[n]


# 🚀 Teste
n = 35

# Recursivo
start = time.time()
result_recursive = fib_recursive(n)
time_recursive = time.time() - start

# Dinâmico
start = time.time()
result_dynamic = fib_dynamic(n)
time_dynamic = time.time() - start


# 📊 Resultado
print("Resultado:", result_recursive)
print("\n--- Recursivo ---")
print("Tempo:", time_recursive)
print("Chamadas:", calls_recursive)

print("\n--- Dinâmico ---")
print("Tempo:", time_dynamic)
print("Chamadas:", calls_dynamic)