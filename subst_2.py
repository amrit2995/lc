class Solution:
    def subsetsWithDup(self, nums):
        def dfs(start, path, res):
            res.append(path)
            for i in range(start, len(nums)):
                if i > start and nums[i] == nums[i-1]:
                    continue
                dfs(i+1, path + [nums[i]], res)
        
        nums.sort()
        res = []
        dfs(0, [], res)
        return res

nums = [1,2,2,2,2,2,2,5,5,5,4,6,7]
s = Solution()
out = s.subsetsWithDup(nums)
print(out)