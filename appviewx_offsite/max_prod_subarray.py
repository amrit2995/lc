class Solution:
    def wordBreak(self, s, wordDict):
        # wordDict = set(wordDict)
        dp = [False for _ in range(len(s)+1)]
        dp[0] = True
        for end in range(1,len(s)+1):
            for word in wordDict:
                if end >= len(word) and (s[end-len(word):end] == word) and dp[end-len(word)]:
                    dp[end] = True
                    break
        return dp[-1]

nums = [2,3,-2,4]
nums = [-4,-3,-2]
s = Solution()
out =  s.wordBreak(nums)
print(out)