class Solution:
    def orangesRotting(self, grid):
        import sys
        def bfs(q, fresh_count):
            if not fresh_count:
                return 0
            if not q:
                return -1
            qlen = len(q)
            for _ in range(qlen):
                r,c = q.popleft()
                for dr,dc in d:
                    nr,nc = r+dr, c+dc
                    if nr in range(len(grid)) and nc in range(len(grid[0])) and grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        q.append((nr,nc))

            out = bfs(q, fresh_count-qlen)
            return out+1 if out > -1 else -1

        from collections import deque


        d = [(-1,0),(1,0),(0,-1),(0,1)]
        q = deque()
        fresh_count = 0
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    fresh_count += 1
                if grid[i][j] == 2:
                    q.append((i,j))

        qlen = len(q)
        # if not fresh_count:
        #     return 0
        freq = bfs(q, fresh_count)

        return freq if freq > -1 else -1

grid = [[2,1,1],[1,1,0],[0,1,1]]
# grid = [[0,2]]
# grid = [[1]]
grid = [[2,1,1],[0,1,1],[1,0,1]]
s =  Solution()
out = s.orangesRotting(grid)
print(out)