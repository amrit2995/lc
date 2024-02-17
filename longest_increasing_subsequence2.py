class Solution:
    def lengthOfLIS(self, nums):
        dp = {}
        
        def ls(curr):

            if curr in dp.keys():
                return dp[curr]
            
            base = [nums[curr]] if curr > -1 else []
            max_seq = base
            for i in range(curr+1,len(nums)):
                if nums[curr] < nums[i] or curr<0:
                    new_seq = base + ls(i)
                    max_seq = new_seq if len(new_seq) > len(max_seq) else max_seq

            dp[curr] = max_seq
            return dp[curr]
        
        return ls(-1)


# get the longest subsequence
nums = [10,9,2,5,3,7,101,18]
#out = [2, 5, 7, 101]
nums = [0,1,0,3,2,3]
# out = [0, 1, 2, 3]
nums = [7,7,7,7,7,7,7]
out = [7]
s = Solution()
out = s.lengthOfLIS(nums)
print(out)