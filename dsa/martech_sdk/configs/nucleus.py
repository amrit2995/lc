
NUCLEUS_CONFIG={
    "host": {
        "east":{
            "dev": "<url>",
            "stage": "<url>",
            "prod": "<url>"
        },
        "central":{
            "dev": "<url>",
            "stage": "<url>",
            "prod": "https://internal-central1.carbon.gcp.lowes.com"
        }
    },
    "uri" : {
        "getConfig" : "/nucleus/config?scope={scopeName}&applicationName={applicationName}",
        "viewConfig" : "/nucleus/config/view?scope={scopeName}&applicationName={applicationName}",
        "saveConfig" : "/nucleus/config",
        "updateConfig" : "/nucleus/config/update"
    }
}