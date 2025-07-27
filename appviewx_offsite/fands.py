class Solution:
    def searchRange(self, nums, target):
        start = 0
        end = len(nums) - 1
        m = 0
        ts = te = None

        while(start<end):
            m = (end + start)//2
            if nums[m] < target:
                start = m + 1
            elif nums[m] > target:
                end = m - 1
            else:
                break

        st = start
        et = m - 1
        se = m+1
        ee = end
        m = 0


        while(st<et):
            m = (et+st)//2
            if nums[m] == target:
                if m == 0 or nums[m-1] < target:
                    ts = m
                    break
                else:
                    et = m-1
            else:
                st = m+1

        while(se<ee):
            m = (ee + se)//2
            if nums[m] == target:
                if m == len(nums)-1 or num[m+1]>target:
                    te = m
                    break
                else:
                    se = m + 1
            else:
                ee = m - 1
        return [ts, te]    

s = Solution()
nums = [5,7,7,8,8,10]
target = 8
# import pdb;pdb.set_trace()
out = s.searchRange(nums, target)
print(out)