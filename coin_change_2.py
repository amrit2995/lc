class Solution:
    def change(self, amount, coins):
        dp = [[0 if i > 0 else 1 for j in range(len(coins)+1)] for i in range(amount+1)]

        for amount in range(1, amount+1):
            for j in range(len(coins)-1, -1 , -1):
                count = coins[j]
                dp[amount][j] = dp[amount][j+1] + (0 if amount-coins[j]<0 else dp[amount-coins[j]][j])

        return dp[amount][0]



s = Solution()
coins = [1,2,5]
amount = 5
out = s.change(amount, coins)
print(out)