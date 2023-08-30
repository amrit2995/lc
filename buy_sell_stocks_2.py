class Solution:
    def maxProfit(self, prices):
        dp = {}

        def dfs(i, bought):
            if i >=len(prices):
                return 0
            if (i,bought) in dp:
                return dp[(i,bought)]

            if bought:
                sell = dfs(i+2,not bought)+prices[i]
                cooldown = dfs(i+1, bought)
                dp[(i, bought)] = max(sell, cooldown)
            else:
                buy = dfs(i+1, not bought) - prices[i]
                cooldown = dfs(i+1,bought)
                dp[(i,bought)] = max(buy,cooldown) 
            return dp[(i,bought)]

        return dfs(0, False)

prices = [1,2,3,0,2]
s = Solution()
out = s.maxProfit(prices)
print(out)

