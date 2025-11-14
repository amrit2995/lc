class Solution:
    def characterReplacement(self, s: str, k: int) -> int:

        char_freqs  = {}
        start = 0
        max_streak = 0
        max_freq = 0
        for end in range(len(s)):

            char_freqs[s[end]] = char_freqs.get(s[end], 0) + 1
            max_freq = max(max_freq, char_freqs[s[end]])

            while (end-start+1) - max_freq > k:
                char_freqs[s[end]] -= 1
                start += 1

            max_streak = max(max_streak, (end-start+1))

        return max_streak