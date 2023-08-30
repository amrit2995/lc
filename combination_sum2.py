class Solution:
    def combinationSum2(self, candidates, target):
        out = []
        def cs_2(target, start,tsum, comb):
            if tsum >= target:
                if tsum == target:
                    out.append(comb)
                return
            for i in range(start, len(candidates)):
                if i > start and candidates[i] == candidates[i-1]:
                    continue
                cs_2(target, i+1, tsum+candidates[i], comb+[candidates[i]])              

        candidates.sort()
        cs_2(target, 0,0,[])
        return out


candidates = [10,1,2,7,6,1,5]
target = 8
s = Solution()
out = s.combinationSum2(candidates, target)
print(out)