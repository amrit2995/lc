class Solution:
    def partition(self, s):
        def palindromes(s):
            tlen = len(s)
            dp = [[False for _ in range(tlen)] for _ in range(tlen)]
            for i in range(len(s)):
                dp[i][i] = True
            for l in range(2,len(s)+1):
                for i in range(tlen-l+1):
                    j = i+l-1
                    if s[i] == s[j]:
                        if l == 2 or dp[i+1][j-1]:
                            dp[i][j] = True
            return dp

        def dfs(row,col,s, path):
            if row < len(s) and not dp[row][col]:
                return

            if row ==len(s):
                out.append(path)

            for j in range(row,len(s)):
                if dp[row][j]:
                    dfs(j+1, j+1,s,path+[s[row:j+1]])

        dp = palindromes(s)
        out = []
        dfs(0,0,s, [])
        return out

s = "bb"
sol = Solution()
out = sol.partition(s)
print(out)