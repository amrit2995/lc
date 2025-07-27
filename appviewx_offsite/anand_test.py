# TYUV  AWS  TYU
# TYUVTYU
# AWSUTYHGAWSERTASW
# UTYHG
# AWS
# reg : "AWS"



# def gs(s,sub):
#     out = []
#     match_counter = 0
#     for i in range(len(s)):
#         if s[i] == sub[match_counter]:
            
#             match_counter += 1
            
#             if match_counter >= len(sub):
                
#                 while match_counter > 0:
#                     match_counter -= 1
#                     print(out)
#                     out.pop()
#         else:
            
#             match_counter = 0
            
#         out.append(s[i])
#         print(i,match_counter, out)
        
#     return "".join(out)
            
            
def gs(s,sub):
    
    match = 0
    gap = 0
    i = 0
    while i < len(s):
        print(i,match, gap)
        if s[i-gap] == sub[match]:
            match += 1
            if match == len(sub):
                gap += match
                match = 0
            i += 1
        else:
            if match == 0:
                i+=1
            else :
                match = 0
        s[i-gap] = s[i]
    return "".join(s[:-gap])


# match = 0
# gap = 0
s = "TYUVAWAWSASAWS"
sub = "AWS"
out = gs(list(s), list(sub))
print(out)








# [1]
# [1, 1]
# [1,2,1]
# [1,3,3,1]
# [1,4,6,4,1]
# [1,5,10,10,5,1]

# n = 3


# [i][j] = [i-1][j-1]+[i-1][j]