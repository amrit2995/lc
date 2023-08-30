class Solution:
    def missingNumber(self, nums):
        l = len(nums)
        ans = 0
        for i in range(len(nums)):
            ans ^= (i+1)^nums[i] 
        return ans

nums = [0,1,3]
s = Solution()
out = s.missingNumber(nums)
print(out)