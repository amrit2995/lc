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

string = "leetcode"
wordDict = ["leet","code"]

s = Solution()
out = s.wordBreak(string, wordDict)
print(out)