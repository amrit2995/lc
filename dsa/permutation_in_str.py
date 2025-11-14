class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:

        s1_dict = {}
        curr_dict = {}
        start = 0
        for s in s1:
            s1_dict[s] = s1_dict.get(s, 0) + 1

        for end in range(len(s2)):

            curr_dict[s2[end]] = curr_dict.get(s2[end], 0) + 1

            while curr_dict.get(s2[end], 0) > s1_dict.get(s2[end], 0):
                curr_dict[s2[start]] -= 1
                if curr_dict[s2[start]] <= 0:
                    curr_dict.pop(s2[start])
                start += 1
            print(start, end, curr_dict)
            if s1_dict == curr_dict:
                return True

        return False