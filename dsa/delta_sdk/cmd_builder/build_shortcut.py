from delta_sdk.cmd_builder.git_clone import GitCloneCommand
import re
from typing import Union
from delta_sdk.connectors.cloud.gcp.storage import GCSStorageConnector

class Infra:
    GCP = "gcp"
    ONPREM = "onprem"


class BuildComponents:
    FILES = 'files'
    MODULES = 'modules'

GIT_REPO_FORMAT = {
    'lmn': "https://tools.lowes.com/stash/scm/e-mnp/<repo_name>.git"  
}

class BuildShortcut:

    def __init__(
        self,
        storage_conn: GCSStorageConnector = None,
        gcs_base_path: str = '',
        relative_gcs_path: str = ''
        ):

        self.storage_conn = storage_conn

        if gcs_base_path:
            self.gcs_base_path = gcs_base_path
        elif self.storage_conn:
            if relative_gcs_path.startswith('/'):
                relative_gcs_path = relative_gcs_path[1:]
            self.gcs_base_path = self.storage_conn.get_absolute_gsutil_path(file_path=relative_gcs_path)
        else:
            raise ValueError("gcs_base_path or storage_conn must be provided")

        self.gcs_base_path = self.filter_gcs_base_path(self.gcs_base_path)
        self.cmds_list: list[str] = []

    def filter_gcs_base_path(self, gcs_base_path: str):
        if gcs_base_path.endswith("/"):
            gcs_base_path = gcs_base_path[:-1]
        if gcs_base_path.startswith("/"):
            gcs_base_path = gcs_base_path[1:]
        return gcs_base_path

    @staticmethod
    def extract_repo_name(repo_url: str) -> str:
        """
        Expected formats:
        - https://<domain>/<path>/<repo_name>.git
        - https://<domain>/<path>/<repo_name>.x
        """
        if not isinstance(repo_url, str) or not repo_url:
            raise ValueError("repo_url must be a non-empty string")

        pattern = r"^https?://[^/]+/([^/]+)/([^/]+)(?:\.git)?/?$"
        m = re.match(pattern, repo_url)
        if not m:
            raise ValueError(f"Invalid repo URL format: {repo_url}")
        return m.group(2)

    @staticmethod
    def build_repo_url(
        repo_name: str,
        project_type: str
        ) -> str:

        repo_url = ''
        if project_type == 'lmn':
            repo_url = GIT_REPO_FORMAT['lmn'].replace('<repo_name>', repo_name)
        return repo_url

    def clone_repo(
        self,
        bearer_auth_header,
        repo_url='',
        repo_name = '',
        repo_branch='',
        project_type = 'lmn',
        ):


        if repo_url:
            self.repo_url = repo_url
        else:
            self.repo_url = BuildShortcut.build_repo_url(repo_name=repo_name, project_type=project_type)
        if repo_name:
            self.repo_name = repo_name
        else:
            self.repo_name = BuildShortcut.extract_repo_name(self.repo_url)

        git_clone_command = GitCloneCommand(
            git_repo_url=self.repo_url,
            git_repo_branch=repo_branch,
            bearer_auth_header=bearer_auth_header,
        ).build()

        self.cmds_list.append(git_clone_command)
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
        files_path_list: list[str]
        ):

        for file_path in files_path_list:
            file_name = file_path.split("/")[-1].replace("/", "")
            command = f"gsutil cp {file_path} {self.gcs_base_path}/{file_name}"
            self.cmds_list.append(command)

    def _zip_module(
        self,
        module_path: str,
        ):

        if module_path.endswith("/"):
            module_path = module_path[:-1]
        module_name = module_path.split("/")[-1]
        zip_module_path = f"{module_name}.zip"

        command = f"echo '=== Zipping module: {module_path} ==='"
        self.cmds_list.append(command)
        command = f"realpath {module_path}"
        self.cmds_list.append(command)
        command = f"ls -la {module_path}"
        self.cmds_list.append(command)
        command = f"git archive --format=zip --output={zip_module_path} --prefix={module_name}/ HEAD:{module_path}"
        self.cmds_list.append(command)
        command = f"echo '=== Zipping module: {module_name} complete ==='"
        self.cmds_list.append(command)

        return zip_module_path

    def _add_entities(
        self,
        entities: str,
        ):
        file_extension_pattern = r'\.(py|json)$'
        py_file_pattern = r'^(?:/)?(?:[^/]+/)*[^/]+' + file_extension_pattern
        folder_structure_pattern = r'^(?:/)?(?:[^/]+(?:/[^/]+)*/?)$'

        raw_entities_list = entities.split(",")
        files_path_list = []

        for entity in raw_entities_list:

            if entity.startswith('/'):
                entity = entity[1:]
            
            if re.match(py_file_pattern, entity):
                files_path_list.append(entity)
            elif re.match(folder_structure_pattern, entity):
                entity = self._zip_module(module_path=entity)
                files_path_list.append(entity)
            else:
                print(f"Invalid entity: {entity}")

        if not files_path_list:
            return self

        self.cmds_list.append("echo '=== Copying the files to GCP location. ==='")

        self._add_files(
            files_path_list=files_path_list,
        )

        self.cmds_list.append("echo '=== Copying the job files and folders to GCP location complete ==='")

        return self

    def add(
        self,
        entities: str="",
        ):

        self.cmds_list.append(f"cd {self.repo_name}")

        self._add_entities(
            entities=entities,
        )
        self.cmds_list.append("cd ..")
        return self

    def build(self):

        self.cmds_list.append("echo '=== Ending logs for build shortcut. ==='")
        cmd_list_str = "\n".join(self.cmds_list)
        return cmd_list_str