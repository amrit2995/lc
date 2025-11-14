class Solution:
    def rob(self, nums: List[int]) -> int:
        memo = [-1]*(len(nums))

        def dfs(i):
            if i >= len(nums):
                return 0
            if memo[i] != -1:
                return memo[i]
            memo[i] = max(nums[i]+dfs(i+2), dfs(i+1))
            return memo[i]
        return dfs(0)