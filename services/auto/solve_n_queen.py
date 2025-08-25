def solve_n_queens(n):
    def is_valid(board, row, col):
        for i in range(row):
            if board[i] == col or \
               board[i] - i == col - row or \
               board[i] + i == col + row:
                return False
        return True

    def solve(board, row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                solve(board, row + 1)
                board[row] = -1

    solutions = []
    solve([-1] * n, 0)
    return solutions

# Example: Solve 4-Queens problem
n = 6
solutions = solve_n_queens(n)
for solution in solutions:
    print(solution)
print('Number of solutions:', len(solutions))
