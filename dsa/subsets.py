class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        
        res = []
        def dfs(subset, i):

            if i >= len(nums):
                res.append(subset.copy())
                return
            dfs(subset, i+1)
            dfs(subset + [nums[i]], i+1)

        dfs([], 0)

        return res