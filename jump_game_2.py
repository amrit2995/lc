class Solution:
    def jump(self, nums):
        nums = nums
        import sys
        def jg(pos, count):
            if nums[pos] == 0:
                return sys.maxsize
            if pos + nums[pos] >= len(nums)-1:
                return count + 1
            return min(jg(i,count+1) for i in range(pos+1, pos+nums[pos]+1))
        return jg(0, 0)

nums = [2,3,1,1,4]
nums = [2,3,0,1,4]
s = Solution()
out = s.jump(nums)
print(out)