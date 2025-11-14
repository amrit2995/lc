class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        
        directions = [(-1, 0), (1, 0), (0,1), (0,-1)]
        an_island = [False]
        island_count = 0
        visited = set()

        def dfs(r, c):

            if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or (r, c) in visited:
                return          
            visited.add((r,c))
            if grid[r][c] != "1":
                return

            an_island[0] = True 
            for d in directions:
                dfs(r+d[0], c+d[1])

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                dfs(i,j)
                # print(i, j , an_island, visited)
                if an_island[0]: island_count += 1
                an_island[0] = False
        return island_count
    




