class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        visited = {}
        start = 0 
        max_length = 0
        for end in range(len(s)):
            if s[end] not in visited:
                visited[s[end]] = end
            else:
                max_length = max(max_length, end-start)
                print(start, end, max_length)
                if visited[s[end]] >= start:
                    start = visited[s[end]] + 1
                    visited[s[end]] = end
        return max_length + (1 if end == len(s)-1 and start < end else 0)

input = "aabaab!bb"
s = Solution()
out = s.lengthOfLongestSubstring(input)
