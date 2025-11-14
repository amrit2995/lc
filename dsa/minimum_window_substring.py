class Solution:
    def minWindow(self, s: str, t: str) -> str:

        t_freq = {}
        found_keys = set()

        shortest_sub_str = s + '0'
        for c in t:
            t_freq[c] = t_freq.get(c,0) + 1
        
        start = 0
        
        for end in range(len(s)):

            if s[end] in t_freq.keys():
                t_freq[s[end]] -= 1

                if t_freq[s[end]] <= 0:
                    found_keys.add(s[end])
                
            while start<= end and t_freq.keys() == found_keys:

                if end - start + 1 < len(shortest_sub_str):
                    shortest_sub_str = s[start:end+1]

                if s[start] in t_freq:
                    t_freq[s[start]] += 1
                    if t_freq[s[start]] > 0:
                        found_keys.remove(s[start])
                start += 1
        
        return shortest_sub_str if len(shortest_sub_str)<=len(s) else ""

        