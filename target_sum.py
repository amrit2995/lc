class Solution:
    def findTargetSumWays(self, nums, target):
        def dfs(tsum, nums,index):
            if tsum == 0 and index == -1:
                return 1
            elif index < 0:
                return 0
            
            dp[(index,tsum)] = dp[(index+1, tsum)]


nums = [1,1,1,1,1]
target = 3
s = Solution()
out = s.findTargetSumWays(nums,target)
print(out)

