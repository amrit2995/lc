class Solution:
    def search(self, nums, target):
        start, end = 0, len(nums)-1
        while start < end:
            mid = (start + end)//2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                start = mid
            else:
                end = mid
        return -1
    
s = Solution()
nums = [-1,0,3,5,9,12]
target = 8
out = s.search(nums, target)
print(out)