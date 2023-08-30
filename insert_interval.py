class Solution:
    def insert(self, intervals, newInterval):
        out = []
        i = 0
        while intervals[i][-1]<newInterval[0]:
            out.append(intervals[i])
            i+=1
        
        out.append(newInterval)
        while newInterval[-1] >= intervals[i][0]:
            out[-1] = (min(out[-1][0],intervals[i][0]), max(out[-1][-1], intervals[i][-1]))
            i += 1

        while i<len(intervals):
            out.append(intervals[i])
            i+=1

        return out

intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]]
newInterval = [4,8] 
s = Solution()
out = s.insert(intervals, newInterval)
print(out)  