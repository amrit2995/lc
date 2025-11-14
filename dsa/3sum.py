class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        
        left = 0
        nums = sorted(nums)
        out = set()
        for left in range(len(nums) - 2):
            mid = left + 1
            right = len(nums) - 1
            while mid < right:
                tsum = nums[left] + nums[mid] + nums[right]
                if tsum == 0:
                    out.add((nums[left], nums[mid], nums[right]))
                    mid += 1
                    right -= 1
                elif tsum < 0:
                    mid += 1
                else:
                    right -= 1
        return list(out)