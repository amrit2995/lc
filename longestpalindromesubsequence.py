# class Solution(object):
#     def longestPalindrome(self, s):
#         n = len(s)
#         dp = [[False for i in range(n)] for j in range(n)]
#         ans = ""
#         maxLength = 0
        
#         # Base case: all substrings of length 1 are palindromes
#         for i in range(n):
#             dp[i][i] = True
#             ans = s[i]
#             maxLength = 1
        
#         # Fill in the dp table for substrings of length 2 and greater
#         for length in range(2, n+1):
#             for i in range(n-length+1):
#                 j = i+length-1
#                 if s[i] == s[j]:
#                     if length == 2 or dp[i+1][j-1]:
#                         dp[i][j] = True
#                         if length > maxLength:
#                             ans = s[i:i+length]
#                             maxLength = length
        
#         return ans
class Solution:
    def countSubstrings(self, s: str) -> int:
        n = len(s)
        dp = [[False for j in range(n)] for j in range(n)]
        for i in range(n):
            dp[i][i] = True
        max_length = 1
        max_string = s[0]
        for l in range(2, n+1):
            for i in range(n-l+1):
                j = i + l - 1

                if s[i] == s[j]:
                    if l==2 or dp[i+1][j-1]:
                        dp[i][j] = True
                        if l > max_length:
                            max_length = max(max_length, l)
                            max_string = s[i:j+1]
        return max_string




string = "babad"
s = Solution()
s.longestPalindrome(string)