class Solution:
    def subsets(self, nums):
        end = 0
        subsets = []
        nums = nums
        def get_subset(start, subset):
            subsets.append(subset)
            for i in range(start+1,len(nums)):
                get_subset(i,subset + [nums[i]])
        get_subset(-1,[])
        return subsets
nums = [1,2,3]
s = Solution()
out = s.subsets(nums)
print(out)