class Solution:
    def generateParenthesis(self, n):
        ans = []
        def dfs(left, right, s, n):
            if len(s) == n*2:
                ans.append(s)
            if left < n:
                dfs(left+1, right, s + '(', n)
            if right < left:
                dfs(left, right+1, s +')', n)
        dfs(0,0,'', n)

n = 3
s = Solution()
out = s.generateParenthesis(n)
print(out)




