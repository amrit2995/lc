import sys
import re
from typing import Union

from martech_sdk.cmd_builder.git_clone_cmd import GitCloneCommand

class BuildComponents:
    MARTECK_SDK = "martech_sdk"
    JOBS = "jobs"
    CONFIG = "config"
    UTILS = "utils"


class BuildShortcut:
    def __init__(
        self,
        source_dir_path,
        ):
        self.cmds_list: list[str] = []

        self.source_dir_path = source_dir_path
        self.gcs_base_path = f"{source_dir_path}/main"
        self.local_base_path = "src/main"
        self.cmds_list.append("set -ex")

    def clone_repo(
        self,
        git_repo_url,
        git_repo_branch,
        bearer_auth_header,
        ):
        git_clone_command = GitCloneCommand(
            git_repo_url=git_repo_url,
            git_repo_branch=git_repo_branch,
            bearer_auth_header=bearer_auth_header,
        ).build()

        self.cmds_list.append(git_clone_command)
        return self

    def add_martech_sdk(
        self,
        ):
        
        local_sdk_location = "src/main/martech_sdk"

        self.cmds_list.append("echo '=== Cleaning old instance of the martech-sdk. ==='")
        self.cmds_list.append(f"gsutil rm -rf {self.source_dir_path}/martech_sdk.zip")
        self.cmds_list.append("echo '=== Copying Martech SDK to GCP location. ==='")
        self.cmds_list.append("git config user.email \"martech_user@example.com\" && git config user.name \"Martech User\"")
        self.cmds_list.append("echo '=== Zipping Martech SDK. ==='")
        self.cmds_list.append(f"git archive --format=zip --output=martech_sdk.zip --prefix=martech_sdk/ HEAD:{local_sdk_location}")
        self.cmds_list.append("echo '=== Copying Martech SDK to GCP location. ==='")
        self.cmds_list.append(f"gsutil cp -r martech_sdk.zip {self.source_dir_path}/martech_sdk.zip")

        return self
        

    def allowed_envs(
        self,
        curr_env: str,
        allowed_env_list: str,
        ):

        base_check_cmd = f"""
echo '=== Checking allowed envs ==='
case <curr_env> in <allowed_envs_list>)
    echo "Running commands to clone ..."
    ;;
*)
    echo "Not a matching env, skipping."
    exit 0
    ;;
esac
"""

        all_envs_set = set(("dev", "stage", "prod"))

        provided_env_set = set(allowed_env_list.split(","))
        allowed_envs_list_str = "|".join(all_envs_set.intersection(provided_env_set))

        final_command = (
            base_check_cmd
            .replace("<curr_env>", curr_env)
            .replace("<allowed_envs_list>", allowed_envs_list_str)
        )

        self.cmds_list.append(final_command)

        return self

    def _add_files(
        self,
        files_path_list: list[str],
        component: str
        ):

        local_base_component_path = f"{self.local_base_path}/{component}"
        gcs_base_component_path = f"{self.gcs_base_path}/{component}"
        
        for file_path in files_path_list:
            file_name = file_path.split("/")[-1]
            relative_path = "/".join(file_path.split("/")[:-1])
            command = f"gsutil cp {local_base_component_path}/{relative_path}/{file_name} {gcs_base_component_path}/{relative_path}/"
            self.cmds_list.append(command)

    def _add_modules(
        self,
        modules_path_list: list[str],
        component: str,
        ):

        local_base_component_path = f"{self.local_base_path}/{component}"
        gcs_base_component_path = f"{self.gcs_base_path}/{component}"

        for module_path in modules_path_list:
            if module_path.endswith("/"):
                module_path = module_path[:-1]
            # module_name = module_path.split("/")[-1]
            # relative_module_path = "/".join(module_path.split("/")[:-1])
            command = f"gsutil cp -r {local_base_component_path}/{module_path}/ {gcs_base_component_path}/{module_path}/"
            self.cmds_list.append(command)

    def _add_home(
        self,
        component: str,
        ):
        
        local_base_component_path = f"{self.local_base_path}/{component}"
        gcs_base_component_path = f"{self.gcs_base_path}/{component}"
        
        if gcs_base_component_path.endswith('/'):
            gcs_base_component_path = gcs_base_component_path[:-1]
        command = f"gsutil cp -r {local_base_component_path} {gcs_base_component_path}/"
        self.cmds_list.append(command)

    def _add_entities(
        self,
        entities: str,
        component: str,
        ):
        
        file_extension_pattern = r'\.(py|json)$'
        py_file_pattern = r'^(?:/)?(?:[^/]+/)*[^/]+' + file_extension_pattern
        folder_structure_pattern = r'^(?:/)?(?:[^/]+(?:/[^/]+)*/?)$'

        raw_entities_list = entities.split(",")
        files_path_list = []
        modules_path_list = []
        home_path = False

        for entity in raw_entities_list:

            if entity.startswith('/'):
                entity = entity[1:]

            if entity=='.':
                home_path = True
            
            elif re.match(py_file_pattern, entity):
                files_path_list.append(entity)
            elif re.match(folder_structure_pattern, entity):
                modules_path_list.append(entity)
            else:
                print(f"Invalid entity: {entity}")

        if not files_path_list and not modules_path_list and not home_path:
            return self

        self.cmds_list.append("echo '=== Copying the files to GCP location. ==='")

        self._add_files(
            files_path_list=files_path_list,
            component=component,
        )

        self._add_modules(
            modules_path_list=modules_path_list,
            component=component,
        )

        if home_path:
            self._add_home(
                component=component,
            )

        self.cmds_list.append("echo '=== Copying the job files and folders to GCP location complete ==='")

        return self

    def add(
        self,
        component: Union[BuildComponents, str],
        entities: str="",
        ):
        
        self.cmds_list.append("echo '=== Adding component: {} ==='".format(component))
        self.cmds_list.append("cd martech-media-market-gcp")
        if component == BuildComponents.MARTECK_SDK:
            self.add_martech_sdk()
        elif component in [BuildComponents.JOBS, BuildComponents.CONFIG, BuildComponents.UTILS]:
            self._add_entities(
                component=component,
                entities=entities,
            )
        else:
            raise ValueError(f"Invalid component: {component}")
        self.cmds_list.append("cd ..")
        return self

    def build(self):

        self.cmds_list.append("echo '=== Ending logs for build shortcut. ==='")
        cmd_list_str = "\n".join(self.cmds_list)
        return cmd_list_str
