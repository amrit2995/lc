class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        sorted_nums = sorted(nums)
        consec_set = set()
        final_out = 0

        for n in sorted_nums:
            if n-1 not in sorted_nums:
                consec_set = set()
            consec_set.add(n)
            final_out = max(final_out, len(consec_set))

        return final_out
        