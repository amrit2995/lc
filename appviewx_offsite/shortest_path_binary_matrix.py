import sys
class Solution:
    def shortestPathBinaryMatrix(self, grid):
        dp = [[None for _ in range(len(grid[0]))] for _ in range(len(grid))]
        if grid[0][0] == 1:
            return -1
        
        dp[0][0] = 1
        
        def dfs(i,j):
            if i not in range(len(grid)) or j not in range(len(grid[0])):
                return sys.maxsize
            elif dp[i][j]:
                return dp[i][j]
            elif grid[i][j] == 1:
                dp[i][j] = sys.maxsize
                return dp[i][j]
            else:
                dp[i][j] = sys.maxsize
                d = ((-1,0),(-1,-1),(0,-1),(1,1),(0,1),(1,1),(1,0),(1,-1))
                
                for di,dj in d:
                    ni, nj = i+di, j+dj
                    dp[i][j] = min(dp[i][j], dfs(ni, nj)+1)
                return dp[i][j]
                        
        out = dfs(len(grid)-1, len(grid[0])-1)
        return out if out <= len(grid)*len(grid[0]) else -1
        


s = Solution()
# grid = [[0,1,1,0,0,0],[0,1,0,1,1,0],[0,1,1,0,1,0],[0,0,0,1,1,0],[1,1,1,1,1,0],[1,1,1,1,1,0]]
grid = [[0,1,0,0,0,0],[0,1,1,1,1,1],[0,0,0,0,1,1],[0,1,0,0,0,1],[1,0,0,1,0,1],[0,0,1,0,1,0]]
out = s.shortestPathBinaryMatrix(grid)

print(out)