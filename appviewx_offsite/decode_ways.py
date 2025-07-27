class Solution:
    def numDecodings(self, s):
        n = len(s)
        if n < 1:
            return 0
        dp = [0]
        for i in range(n):
            add = (i == 0) or int(s[i-1:i+1]) in range(10,27)
            sub = (s[i] == '0')
            old = dp[-2] if i > 0 else 0
            dp.append(old+add-sub)

        return dp[-1] if dp[-1] > 0 else 0

a = "13346"
# a = "12"
# a = "06"
a = "2101"
s = Solution()
out = s.numDecodings(a)
print(out)

(dp[i - 1] if int(s[i-1]>0) else 0 + (dp[i - 2] if 10 <= int(s[i - 2:i]) <= 26 else 0))



class Solution:
    def numDecodings(self, s: str) -> int:
        if not s:
            return 0

        dp = [0 for x in range(len(s) + 1)] 

        # base case initialization
        dp[0] = 1 
        dp[1] = 0 if s[0] == "0" else 1   #(1)

        for i in range(2, len(s) + 1): 
            # One step jump
            if 0 < int(s[i-1:i]) <= 9:    #(2)
                dp[i] += dp[i - 1]
            # Two step jump
            if 10 <= int(s[i-2:i]) <= 26: #(3)
                dp[i] += dp[i - 2]
        return dp[len(s)]


        dp[i] = (dp[i-1] if int(s[i])>0 else 0) + (dp[i-2] if 10<=int(s[i-1:i])<=26 else 0) 