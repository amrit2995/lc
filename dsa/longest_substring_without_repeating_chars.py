class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        
        start = 0
        curr_set = set()
        max_len = 0
        for end in range(len(s)):
            while s[end] in curr_set:
                curr_set.remove(s[start])
                start += 1
            curr_set.add(s[end])
            max_len = max(max_len, len(curr_set))
        return max_len