class Solution:
    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        visited = set()
        max_area = 0

        def dfs(r,c):

            if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or (r,c) in visited or grid[r][c] != 1:
                return 0
            visited.add((r,c))
            return 1 + dfs(r+1, c) + dfs(r-1, c) + dfs(r, c-1) + dfs(r, c+1)

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                new_area = dfs(i, j)
                max_area = max(max_area, new_area)
        return max_area