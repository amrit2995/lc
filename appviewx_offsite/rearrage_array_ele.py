


class Solution:
    def rearrangeArray(self, nums):
        def get_next_positive(nums):
            i= -1
            while True:
                i+=1
                while nums[i] < 0:
                    i+= 1
                yield nums[i]

        def get_next_negative(nums):
            i = -1
            while True:
                i+=1
                while nums[i] > 0:
                    i += 1
                yield nums[i]

        out = []
        pos_val = get_next_positive(nums)
        neg_val = get_next_negative(nums)
        return [next(pos_val) if i%2 == 0 else next(neg_val) for i in range(len(nums))]


s = Solution()
nums = [3,1,-2,-5,2,-4]
out = s.rearrangeArray(nums)
print(out)