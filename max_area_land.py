from collections import deque
class Solution:
    def maxAreaOfIsland(self, grid):
        grid = grid
        def bfs(r,c):
            directions = [(0,-1),(0,1), (1,0), (-1,0)]
            q = deque()
            q.append((r,c))
            grid[r][c] = -1
            count = 0
            while q:
                r,c = q.popleft()
                count += 1
                for dr,dc in directions:
                    fr,fc = r+dr, c+dc
                    if fr in range(ROW) and fc in range(COL) and grid[fr][fc] == 1:
                        grid[fr][fc] = -1
                        q.append((fr,fc))
            return count

        ROW = len(grid)
        COL = len(grid[0])
        max_area = 0

        for i in range(ROW):
            for j in range(COL):
                if grid[i][j] == 1:
                    max_area = max(max_area, bfs(i,j))
        return max_area


grid = [[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]
grid = [[1,1,0,0,0],[1,1,0,0,0],[0,0,0,1,1],[0,0,0,1,1]]
s = Solution()
out = s.maxAreaOfIsland(grid)
print(out)