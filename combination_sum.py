class Solution:
    def combinationSum(self, candidates, target):
        candidates = candidates
        l = len(candidates)
        target = target
        ans = []
        def cs(index,com, tsum):
            if tsum >=  target:
                if tsum == target:
                    ans.append(com)
                return
            for i in range(index,l):
                cs(i,com+[candidates[i]],tsum+candidates[i])
        cs(0,[],0)
        return ans

candidates = [2,3,6,7]
target = 7
s = Solution()
out = s.combinationSum(candidates, target)
print(out)