class Solution:
    def kSmallestPairs(self, nums1, nums2, k):
        index1 = 0
        index2 = 0
        out = []
        while len(out) < k:
            out.append([nums1[index1],nums2[index2]])
            print(out, index1, index2)
            if index1 >= len(nums1)-1:
                index2 += 1
                index1 = 0
            elif index2 >= len(nums2)-1:
                index1 += 1
                index2 = 0
            elif nums1[index1] <= nums2[index2]:
                index2 += 1
            else:
                index1 += 1

        return out

nums1 = [1,1,2]
nums2 = [1,2,3]
k = 2
s = Solution()
out  = s.kSmallestPairs(nums1, nums2, k)
print(out)