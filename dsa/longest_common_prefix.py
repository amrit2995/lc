from typing import List
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        
        common_prefix = strs[0]

        for i in range(1, len(strs)):

            min_str_len = min(len(common_prefix), len(strs[i]))
            new_prefix = ''
            j=0
            for j in range(min_str_len):
                if common_prefix[j] == strs[i][j]:
                    new_prefix += common_prefix[j]
                    j += 1
                else:
                    break
            common_prefix = new_prefix

        return common_prefix

strs = ["flower","flow","flight"]
print(Solution.longestCommonPrefix(strs))
