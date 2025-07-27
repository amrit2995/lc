class Solution:
    def pacificAtlantic(self, heights):
        dp = [[None for _ in range(len(heights[0]))] for _ in range(len(heights))]

        out = []

        def both_flow(rr, rc):
            if dp[rr][rc]:
                return dp[rr][rc]
            if (rr in (0, len(heights))) or (rc in (0,len(heights))):
                if (rr,rc) in ((0,len(heights[0])-1),(len(heights)-1, 0)):
                    dp[rr][rc] =  [True, True]
                elif rr == 0 or rc == 0:
                    dp[rr][rc] =  [True, False]
                elif rr == len(heights)-1 or rc == len(heights[0])-1:
                    dp[rr][rc] =  [False, True]
                elif dp[rr][rc]:
                    dp[rr][rc] = dp[rr][rc]
                return dp[rr][rc]

            dp[rr][rc] = [False, False]

            dir_dict = [(-1,0), (1 ,0), (0,-1), (0,1)]

            for dr, dc in dir_dict:
                r, c = rr+dr, rc+dc
                if r in range(len(heights)) and c in range(len(heights[0])):
                    if not dp[r][c]:
                        dp[r][c] = both_flow(r,c)
                    dp[rr][rc][0] = dp[rr][rc][0] or (dp[r][c][0] and (heights[rr][rc]>heights[r][c]))
                    dp[rr][rc][1] = dp[rr][rc][1] or (dp[r][c][1] and (heights[rr][rc]>heights[r][c]))

            return dp[rr][rc]

        for i in range(len(heights)):
            for j in range(len(heights[0])):
                if all(both_flow(i,j)):
                    out.append((i,j))
        
        return out



s = Solution()
heights = [[1,2,3],[8,9,4],[7,6,5]]
out = s.pacificAtlantic(heights) 
print(out)