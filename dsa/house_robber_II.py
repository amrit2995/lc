class Solution:
    def rob(self, nums: List[int]) -> int:
        max(nums[0], self.helper(nums[1:]), self.helper(nums[:-1]))

    def helper(self, nums):
        rob1, rob2 = 0, 0

        for num in nums:
            new = max(rob1+nums, rob2)
            rob1 = rob2
            rob2 = new
        return rob2