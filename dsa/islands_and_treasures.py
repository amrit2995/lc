from collections import deque, List


class Solution:
    def islandsAndTreasure(self, grid: List[List[int]]) -> None:
        
        visited = set()
        q = deque()

        def add_paths(r,c):

            if r<0 or c<0 or r>=len(grid) or c>=len(grid[0]) or grid[r][c] == -1 or (r,c) in visited:
                return

            visited.add((r,c))
            q.append((r,c))

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 0:
                    q.append((i,j))
                    visited.add((i,j))

        dist = 0
        while q:
            for i in range(len(q)):
                r,c = q.popleft()
                grid[r][c] = dist
                add_paths(r+1, c)
                add_paths(r-1, c)
                add_paths(r, c+1)
                add_paths(r, c-1)
            dist += 1