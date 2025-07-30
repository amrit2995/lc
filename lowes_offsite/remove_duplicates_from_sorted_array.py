from typing import List

class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        traversed = set()

        o = 0
        i = 0
        visited = set()
        for i in range(len(nums)):
            if i == 0 or nums[i] not in visited:
                nums[o] = nums[i]
                o += 1
                visited.add(nums[i])
        
        return o

# Given an integer array nums sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once. The relative order of the elements should be kept the same. Then return the number of unique elements in nums.
# Consider the number of unique elements of nums to be k, to get accepted, you need to do the following things:
# Change the array nums such that the first k elements of nums contain the unique elements in the order they were present in nums initially. The remaining elements of nums are not important as well as the size of nums.
# Return k.

nums = [1,1,2]
Solution().removeDuplicates(nums=nums)