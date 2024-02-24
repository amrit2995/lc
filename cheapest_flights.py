import sys

class Solution:
    def findCheapestPrice(self, n, flights, src, dst, k):
        
        s2d = {}
        dp = {}
        dst = [dst]
        
        def dfs(curr,hops_left):
            if (curr,hops_left) in dp.keys():
                return dp[(curr,hops_left)]
            dp[(curr, hops_left)] = sys.maxsize
            if curr == dst[0]:
                dp[(curr, hops_left)] = 0
            elif hops_left <= 0:
                dp[(curr,hops_left)] = sys.maxsize
            elif curr not in s2d.keys():
                dp[(curr, hops_left)] = sys.maxsize
            else:
                for next_hop in s2d[curr].keys():
                    dp[(curr,hops_left)] = min(dp[(curr,hops_left)], dfs(next_hop, hops_left-1)+s2d[curr][next_hop])
            return dp[(curr,hops_left)]
        
        for p1, p2, price in flights:
            if p1 not in s2d.keys():
                s2d[p1] = {}
            s2d[p1][p2] = price
        
        dp[(src,k+1)] = dfs(src,k+1)
        return dp[(src,k+1)] if dp[(src,k+1)] < 100000 else -1


s = Solution()
n = 3
flights = [[0,1,2],[1,2,1],[2,0,10]]
src = 1
dst = 2
k = 1
out = s.findCheapestPrice(n, flights,src, dst, k)
print(out)