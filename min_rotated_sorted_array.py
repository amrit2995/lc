class Solution:
    def findMin(self, nums):
        l = 0
        r = len(nums)-1
        while l<r:
            m = (l+r)//2
            if nums[m] > nums[r]:
                l = m+1
            else:
                r = m
        return nums[l]

nums = [2,1]
s = Solution()
out = s.findMin(nums)
print(out)
