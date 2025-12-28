
NUCLEUS={
    "host": {
        "east":{
            "dev": "https://internal-east4.carbon-dev.gcp.lowes.com",
            "stage": "https://internal-east4.carbon-stage.gcp.lowes.com",
            "prod": "https://internal-east4.carbon.gcp.lowes.com"
        },
        "central":{
            "dev": "https://internal-central1.carbon-dev.gcp.lowes.com",
            "stage": "https://internal-central1.carbon-stage.gcp.lowes.com",
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