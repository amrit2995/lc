
from typing import List
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        
        i = 0
        j = len(nums) - 1

        while i <= j:
            if nums[j] == val:
                j -= 1
            elif nums[i] == val:
                nums[i] = nums[j]
                j -= 1
            else:
                i += 1
        return j+1

nums = [3,2,2,3]
val = 3

nums = [0,1,2,2,3,0,4,2]
val = 2

Solution().removeElement(nums= nums, val=val)