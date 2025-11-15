class Solution:
    def countSubstrings(self, s: str) -> int:
        n = len(s)
        no_of_pal = 0
        dp = [[False for _ in range(n)] for _ in range(n)]

        for i in range(n-1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and ((j-i+1)<=2 or dp[i+1][j-1]):
                    no_of_pal += 1
                    dp[i][j] = True

        return no_of_pal