import subprocess
import os
from delta_sdk.utils import logging
from delta_sdk.configs.common import CommonConfig

class SwitchBranchMode:
    DEVELOP = ''
    LATEST_COMMIT = ''

class GitUtilities:
    
    @staticmethod
    def clone( repo_name: str, token: str, branch: str='master', dest_dir=None, repo_url=None):
        """
            Args::
                repo_name :
                repo_url : | Optional | Default: Generates url with repo-name in mnp-project
                branch : | Optional | Default: master
                token : 
                destination | Optional | Default: CWD
        """
        
        try:
            if not token:
                raise ValueError('Token not provided.')
            
            # Ensure destination directory exists
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            repo_url = repo_url if repo_url else CommonConfig.GIT_HTTP_MNP_REPO_URL.replace('<REPO-NAME>', repo_name)
            dest_dir = dest_dir if dest_dir else os.path.join(os.getcwd(), repo_name)

            cmd = [
                "git",
                "-c", CommonConfig.GIT_HTTP_TOKEN_HEADER.replace('<TOKEN>', token),
                "clone",
                "-b", branch,
                repo_url,
                dest_dir
                ]
            
            logging.info(f"command:- {cmd}")
            logging.info(f"command :- {" ".join(cmd)}")
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)

            logging.info(f"Output: {process.stdout}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error: Command failed with return code {e.returncode}")

            error_message = (
                f"{type(e).__name__} : \n"
                f"Command failed with return code {e.returncode} \n"
                f"Stderr: {e.stderr} \n"
                f" Stdoutput: {e.output}"
                )
            logging.error(error_message)

        except Exception as e:
            logging.error(f"{type(e).__name__}:{e}")