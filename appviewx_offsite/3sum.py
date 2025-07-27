class Solution:
    def threeSum(self, nums):
        nums = sorted(nums)
        out = []
        # import pdb;pdb.set_trace()
        i = 0
        while i < len(nums) - 2 :
            s = i+1
            e = len(nums) - 1
            
            while s<e:

                while nums[s] == nums[s+1]:s += 1
                while nums[e] == nums[e-1]:e -= 1

                pair_sum = nums[s] + nums[e] + nums[i]

                if pair_sum == 0:

                    out.append([nums[i], nums[s], nums[e]])
                    s += 1
                    e -= 1

                elif pair_sum < 0:

                    s += 1

                else:

                    e -= 1

            while nums[i] == nums[i+1]:
                i += 1
            i += 1

        return out

s = Solution()
nums = [0,0,0]
[-4, -1, -1, 0, 1, 2]
print(s.threeSum(nums))