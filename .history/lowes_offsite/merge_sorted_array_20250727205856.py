# 88. Merge Sorted Array
# Solved
# Easy
# Topics
# premium lock icon
# Companies
# Hint
# You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of elements in nums1 and nums2 respectively.

# Merge nums1 and nums2 into a single array sorted in non-decreasing order.

# The final sorted array should not be returned by the function, but instead be stored inside the array nums1. To accommodate this, nums1 has a length of m + n, where the first m elements denote the elements that should be merged, and the last n elements are set to 0 and should be ignored. nums2 has a length of n.


from typing import List

class Solution:
    def merge(self, nums1: List[int], m: int, nums2: List[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.
        """

        i = m - 1
        j = n - 1
        k = m + n - 1 
        import pdb;pdb.set_trace()
        while k > -1:
            print(nums1, k, i, j)
            if j < 0:
                nums1[k] = nums1[i]
                i -= 1
            elif i < 0:
                nums1[k] = nums2[j]
                j -= 1
            elif nums1[i] > nums2[j]:
                nums1[k] = nums1[i]
                i -= 1
            else:
                nums1[k] = nums2[j]
                j -= 1
            k -= 1
        import pdb;pdb.set_trace()
        return nums1

nums1 = [0]
m = 0 
nums2 = [1]
n = 1

print(Solution().merge(nums1=nums1, m=m, nums2=nums2, n=n))