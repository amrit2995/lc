class Solution:
    def minWindow(self, s: str, t: str) -> str:
        from collections import Counter
        import heapq
        import sys

        min_window_length = sys.maxsize
        min_window = ''

        t_freq = Counter(t)

        s_freq = {}
        start_heap = []

        def is_substring():
            return all([ t_freq[char] < 1 for char in t_freq ])

        for i in range(len(s)):
            a = s[i]
            if s[i] in t_freq:
                heapq.heappush(start_heap, i)
                t_freq[s[i]] -= 1
            
                while t_freq[s[start_heap[0]]] < 0:
                    pop_index = heapq.heappop(start_heap)
                    t_freq[s[pop_index]] += 1

                if is_substring():
                    if (i-start_heap[0]+1) < min_window_length:
                        min_window_length = (i-start_heap[0]+1)
                        min_window = s[start_heap[0]:i+1]
                
        return min_window

# s = "ADOBECODEBANC"
# t = "ABC"
s="cabwefgewcwaefgcf"
t="cae"
sol = Solution()
out = sol.minWindow(s,t)
print(out)