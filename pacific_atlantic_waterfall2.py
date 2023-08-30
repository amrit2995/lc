class Solution:
    def pacificAtlantic(self, heights):
        rlen = len(heights)
        clen = len(heights[0])
        pacific_reach = set([(0,j) for j in range(clen)])|set([(i,0) for i in range(rlen)])
        atlantic_reach = set([(rlen-1, j) for j in range(clen)])|set([(i,clen-1) for i in range(rlen)])
        from collections import deque
        q = deque(pacific_reach)

        def bfs(river_reach):

            q = deque(river_reach)
            dirs = [(-1,0),(1,0),(0,-1),(0,1)]
            while q:
                r,c = q.popleft()

                for dr,dc in dirs:
                    nr, nc = r+dr, c+dc

                    if nr in range(len(heights)) and nc in range(len(heights[0])):
                        if (nr,nc) not in river_reach and heights[nr][nc] >= heights[r][c]:
                            river_reach.add((nr, nc))
                            q.append((nr,nc))

        bfs(pacific_reach)
        bfs(atlantic_reach)

        return list(pacific_reach & atlantic_reach)


s = Solution()
heights = [[1,2,3],[8,9,4],[7,6,5]]
out = s.pacificAtlantic(heights) 
print(out)