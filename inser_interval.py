class Solution:
    def insert(self, intervals, newInterval):
        inserted = False
        j = 0
        ni = newInterval
        out = [[-2,-1]]
        while((not inserted) or j < len(intervals)):
            i = intervals[j] if j < len(intervals) else None

            if not inserted:

                if not i or (ni[1] < i[0]):
                    new = ni
                elif i[1] < ni[0]:
                    new = i
                    j += 1
                else:
                    new = [min(ni[0], i[0]), max(ni[0], i[1])]
                    j += 1
                print(new)
            else:
                new = i
                j += 1
            if out[-1][1] < new[0]:
                out.append(new)
            elif out[-1][1] in range(new[0], new[1]+1):
                out[-1] = [out[-1][0], max(out[-1][1], new[1])]
            if out[-1][1] >= ni[1]:
                inserted = True
        return out[1:]


s = Solution()
intervals = [[3,5],[12,15]]
newInterval = [6,6]
out = s.insert(intervals, newInterval)
print(out)