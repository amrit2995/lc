class Solution:
    def minWindow(self, s: str, t: str) -> str:
        from collections import Counter

        td = Counter(t)
        w = len(t)
        match = 0
        target = len(td)
        l = 0
        min_window = len(s)
        ans = ""

        for r in range(len(s)):
            if s[r] in td:
                td[s[r]] -= 1

                if td[s[r]] == 0:
                    match += 1

            while match == target:
                if r-l+1 <= min_window:
                    min_window = r-l+1
                    ans = s[l:r+1]

                if s[l] in td:
                    td[s[l]] += 1

                    if td[s[l]] > 0:
                        match -= 1
                
                l += 1

        return ans

s = "ADOBECODEBANC"
t = "ABC"
# s = "a"
# t = "a"
sol = Solution()
out = sol.minWindow(s, t)
print(out)