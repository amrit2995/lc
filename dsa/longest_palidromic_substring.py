class Solution:
    def longestPalindrome(self, s: str) -> str:

        res_idx = 0
        res_len = 0

        for i in range(len(s)):
            
            l,r = i, i
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if (r - l + 1) > res_len:
                    res_len = r - l + 1
                    res_idx = l
                l -= 1
                r += 1

            l,r = i, i+1
            while l >= 0 and r < len(s) and s[l] == s[r]:
                if (r - l + 1) > res_len:
                    res_len = r - l + 1
                    res_idx = l
                l -= 1
                r += 1
        
        return s[res_idx : res_idx + res_len]