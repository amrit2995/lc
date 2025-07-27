class Solution:
    def longestPalindrome(self, s):
        dp = [[0 for _ in range(len(s))] for _ in range(len(s))]
        for i in range(len(s)):
            dp[i][i] = 1
        max_substr = s[0]
        for l in range(2, len(s)+1):
            for i in range(len(s)-l+1):
                j = i + l-1
                if l == 2 and s[i] == s[i+1]:
                    dp[i][i+1] = 1
                    max_substr = s[i:i+2]
                if l > 2 and s[i] == s[j] and dp[i+1][j-1]:
                    dp[i][j] = 1
                    max_substr = s[i:j+1]
        return max_substr



s = Solution()
input = 'bb'
print(s.longestPalindrome(input))