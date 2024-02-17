

def longest_unique_substring(s):
    unique_subset = {}
    start = 0
    max_unique_len = 0
    max_unique_sub = ''
    for i in range(len(s)):
        if s[i] not in unique_subset.keys():
            unique_subset[s[i]] = i
            substr = s[start:i+1]
            if max_unique_len < (i-start+1):
                max_unique_len = (i-start+1)
                max_unique_sub = s[start:i+1]
                
        else:
            last_index = unique_subset[s[i]]
            for j in range(start,last_index+1):
                unique_subset.pop(s[j])
            start = last_index + 1
            unique_subset[s[i]] = i
            
    return max_unique_sub


# {'a':3,
#  'b':1
#  }

s ='bcdaefsagersgerty'


# aaaaaaaaaaaaaa


# abcedfgh
out = longest_unique_substring(s)