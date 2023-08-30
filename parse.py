


input1 = "ltm virtual ForceDownCA_55233_CO_LTM_VirtualServer_IPV4_001 {\r\n    creation-time 2023-03-22:00:59:42\r\n    destination 153.254.236.100:http\r\n    last-modified-time 2023-03-22:01:00:00\r\n    mask 255.255.255.255\r\n    pool ForceDownCA_55233_CO_LTM_Pool_IPV4_001\r\n    profiles {\r\n        fastL4 { }\r\n    }\r\n    serverssl-use-sni disabled\r\n    source 0.0.0.0/0\r\n    translate-address enabled\r\n    translate-port enabled\r\n    vs-index 4655\r\n}\r"
input = "ltm virtual ForceDownCA_55233_CO_LTM_VirtualServer_IPV4_001 {\r\n    creation-time 2023-03-22:00:59:42\r\n    destination 153.254.236.100:http\r\n    last-modified-time 2023-03-22:01:00:00\r\n    mask 255.255.255.255\r\n    pool ForceDownCA_55233_CO_LTM_Pool_IPV4_001\r\n    profiles {\r\n   \r\n    }\r\n    serverssl-use-sni disabled\r\n    source 0.0.0.0/0\r\n    translate-address enabled\r\n    translate-port enabled\r\n    vs-index 4655\r\n}\r"

# input = [ele.strip() for ele in input.split()]
# print(input)

mapper = {
    "ltm":{
        "virtual":{
            "components":{"pool", "profiles"},
            "properties":{"mask", "source", "translate-port", "vs-index", "destination"}
        },
        "pool":{
            "components":{},
            "properties":{}
        }, 
        "node":{
            "components":{},
        },
        "monitor":{},
        "profiles":{
            "profile_type":{"fastl4"},
            "components":{"fastl4"},
        },
        "profile":{
            "properties":{"status"}
        }

    },
    "gtm":{
        "objects":{"wideip", "pool"}
    }
}

def main_parser():
    out = {}
    if input[0] == "ltm":
        out["ltm"] = main_object_parser("ltm", 1)
        return out

    if input[0] == "gtm":
        out["gtm"] = main_object_parser("gtm", 1)
        return out

    if input[0] in ltm_objects:
        out[input[0]] = {}
        out[input[0]]["name"] = input[1]
        if out[[input[2]]] == "{":
            out[input[0]]["components"] = parser(input[2:])
        return out
    # else:

    return out

def main_object_parser(tm_type, start):
    out = {}
    index = start
    if input[index] in mapper[tm_type]:
        out[input[index]] = eval(f"{input[index]}_parser")(tm_type,index+1)
        return out


    

def virtual_parser(tm_type, start):
    index = start
    out = {}
    out['name'] = input[index]
    index += 1

    while index < len(input):

        if input[index] == "}":
            return (out,index+1)

        if input[index] == "{":
            index += 1

        else:
            if input[index] in mapper[tm_type]["virtual"]["components"]:
                out[input[index]],index = eval(f"{input[index]}_parser")(tm_type, index+1)
                index += 1
            else:
                if input[index] in mapper[tm_type]["virtual"]["properties"]:
                    out[input[index]] = input[index+1]
                index += 2
    return out

def pool_parser(tm_type, start):
    index = start
    out = {}
    out['name'] = input[index]
    index += 1

    while index < len(input):

        if input[index] == "}":
            return (out,index+1)

        elif input[index] == "{":
            index += 1
        
        elif input[index] in mapper[tm_type]:
            if mapper[tm_type]["pool"].get("components") and input[index] in mapper[tm_type]["pool"]["components"]:
                out[input[index]], index = eval(f"{input[index]}_parser")(tm_type, index+1)
            else:
                return (out,index-1)
        else:
            if mapper[tm_type]["pool"].get("properties") and input[index] in mapper[tm_type]["pool"]["properties"]:
                out[input[index]] = input[index+1]
            index += 2
    return out

def profiles_parser(tm_type,start):
    index = start
    out = {}

    while index < len(input):

        if input[index] == "}":
            return (out,index+1)

        elif input[index] == "{":
            index += 1
        
        elif input[index] in mapper[tm_type]['profiles']['profile_type']:
            out[input[index]],index = profile_parser(tm_type, index+1)


def profile_parser(tm_type,start):
    index = start
    out = {}
    
    out['name'] = input[index]
    index += 1

    while index < len(input):

        if input[index] == "}":
            return (out,index+1)

        if input[index] == "{":
            index += 1
    
        if input[index] in mapper[tm_type]:
            return (out, index-1)

        else:
            out[input[index]] = input[index+1]
            index += 2            

    return out


input = [ele.strip() for ele in input.split()]
print(input)

out = main_parser()
print(out)

# for key in {"virtual", "pool", "monitor"}:
#     eval(f"{key}_parser")()