class Solution:
    def lengthOfLIS(self, nums):
        dp = [1 for _ in range(len(nums))]
        max_val = 1
        for i in range(len(nums)): 
            for j in range(i-1,-1,-1):
                if nums[i] > nums[j]:
                    dp[i] = max(dp[i],dp[j]+1)
                    max_val = max(max_val, dp[i])
        return max_val

nums = [10,9,2,5,3,7,101,18]
s = Solution()
out = s.lengthOfLIS(nums)
print(out)