class Solution:
    def search(self, nums: List[int], target: int) -> int:
        
        def bsearch(start, end, nums, target):
            print(start, end, target)
            mid = (end + start)//2
            if start > end:
                return -1
            if target == nums[mid]:
                return mid
            elif nums[mid] < target:
                return bsearch(mid+1, end, nums, target)
            else:
                return bsearch(start, mid-1, nums, target)

        return bsearch(0, len(nums) - 1, nums, target)