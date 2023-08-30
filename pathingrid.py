class Solution:
    def countPaths(self, grid):
        mod = 10**9+7
        dp = [[-1 for _ in range(len(grid))] for _ in range(len(grid[0]))]
        visited = set()
        def dfs(i,j):
            visited.add((i,j))
            ds = [[1, 0], [-1, 0], [0, -1], [0, 1]]
            if i not in range(len(grid)) or j not in range(len(grid)):
                return 2
            if dp[i][j] != -1:
                return dp[i][j] 
            for d in ds:
                row = i + d[0]
                col = j + d[1]
                if (i, j) != (row, col):
                    dp[i][j] += dfs(row, col)
            return dp[i][j]
        dfs(0,0)
        print(dp[0][0])
        return dp[0][0]

grid = [[1,1],[3,4]]
s = Solution()
s.countPaths(grid)