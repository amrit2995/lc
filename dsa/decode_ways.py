class Solution:
    def numDecodings(self, s: str) -> int:
        dp = {len(s): 1}

        def dfs(i):

            if i in dp:
                return dp[i]

            if s[i] == "0":
                return 0

            # Take 1 digit
            res = dfs(i + 1)

            # Take 2 digits if valid (10–26)
            if i + 1 < len(s) and 10 <= int(s[i:i+2]) <= 26:
                res += dfs(i + 2)

            dp[i] = res
            return res

        return dfs(0)
