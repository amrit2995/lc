import logging

class GitCloneCommand:
    bash_command = ""
    base_git_repo_clone_command = "git -c \"<bearer-auth-header>\" clone --single-branch --branch <git-repo-branch> \"<git-repo-url>\""

    base_final_clone_command: str = """
        
        <git-clone-command>
        ls -la
        echo "=== Ending logs for cloning. ==="
    """

    def __init__(
        self,
        git_repo_url,
        git_repo_branch,
        bearer_auth_header,
        ):

        self.git_repo_url = git_repo_url
        self.git_repo_branch = git_repo_branch
        self.bearer_auth_header = bearer_auth_header

        self.cmds_list = []
        self.cmds_list.append("echo '=== Starting logs for cloning. ==='")
        self.cmds_list.append(self.git_clone_command())
        self.cmds_list.append("ls -la")
        self.cmds_list.append("echo '=== Ending logs for cloning. ==='")

    def git_clone_command(self):

        self.git_repo_clone_command = (
            self.base_git_repo_clone_command
            .replace("<git-repo-url>", self.git_repo_url)
            .replace("<git-repo-branch>", self.git_repo_branch)
            .replace("<bearer-auth-header>", self.bearer_auth_header)
        )
        return self.git_repo_clone_command

    def build(self):

        cmd_list_str = "\n".join(self.cmds_list)
        return cmd_list_str

