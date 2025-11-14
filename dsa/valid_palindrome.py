from typing import List

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        import sys
        buy = 0
        max_profit = - sys.maxsize
        for sell in range(len(prices)):
            if prices[sell] < prices[buy]:
                buy = sell
            else:
                max_profit = max(max_profit, (prices[sell] - prices[buy]))
        return max_profit 
    
prices = [7,1,5,3,6,4]
ans = Solution().maxProfit(prices=prices)
print(ans)