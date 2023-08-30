class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        dp = [[0 for i in range(n)] for j in range(m)]
        dirs = [(0,-1),(-1,0)]
        dp[0][0] = 1
        for r in range(m):
            for c in range(n):
                for dr, dc in dirs:
                    fr, fc = r+dr, c+dc
                    dp[r][c] += 0 if fr < 0 or fc < 0 else dp[fr][fc]
        return dp[-1][-1]

m,n = 3,7
s = Solution()
out = s.uniquePaths(m,n)
print(out)