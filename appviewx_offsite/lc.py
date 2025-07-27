import copy
class Solution:
    def subsetsWithDup(self, nums):
        out = []
        def ss(comb, start):
            for i in range(start,len(nums)+1):
                out.append(comb.copy())
                if i >= len(nums):
                    return
                if i < 1 or nums[i] != nums[i-1]:
                    ss(comb+[nums[i]],i+1)
                else:
                    comb.append(nums[i])
        ss([], 0)
        return out

nums = [1,2,2]
s = Solution()
out = s.subsetsWithDup(nums)
print(out)