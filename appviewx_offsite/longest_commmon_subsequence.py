class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        dp = [[0 if (i == len(text1) or j == len(text2)) else None for j in range((len(text2))+1)] for i in range((len(text1)+1))]

        def dfs(i,j,text1,text2):
            if dp[i][j] != None:
                pass
            elif text1[i] == text2[j]:
                dp[i][j] = dfs(i+1, j+1, text1, text2) + 1
            else:
                dp[i][j] = max(dfs(i+1, j, text1, text2), dfs(i, j+1, text1, text2))  
            return dp[i][j]
            
        dfs(0,0,text1, text2)
        return dp[0][0]


text1 = "abc"
text2 = "abcde"
s = Solution()
out = s.longestCommonSubsequence(text1, text2)
print(out)