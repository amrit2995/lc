class Solution:
    def coinChange(self, coins, amount):
        import sys
        dp = [sys.maxsize for _ in range(amount+1)]
        dp[0] = 0
        for pa in range(1,amount+1):    
            for coin in coins:
                if pa - coin < 0:
                    break
                else:
                    dp[pa] = min(dp[pa],dp[pa-coin]+1)
        return dp[amount] if dp[amount] != sys.maxsize else -1


coins = [1,2,5]
amount = 11
coins = [1]
amount = 0
s = Solution()
out = s.coinChange(coins, amount)
print(out)