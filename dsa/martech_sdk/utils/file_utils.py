from martech_sdk.utils import logging
import os
import subprocess
import json

class FileUtilities:

    @staticmethod
    def unzip(source, destination):
        logging.info("Inside unzipping function")
        if not source or not destination:
            raise ValueError("Both 'source' and 'destination' must be provided")

        logging.info("Ensure the zip file path's directory exists")
        if not os.path.exists(destination):
            os.makedirs(destination)

        logging.info(f"source: {source}")
        logging.info(f"destination: {destination}")

        try:

            logging.info(f"Verify Content fo {source}:")
            command = ['unzip', '-l', source]
            logging.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(command, check=True, text=True, capture_output=True, timeout=60)
            logging.info(f"Listing successful:\n{result.stdout}")

            logging.info(f"Unzipping from {source} to {destination}")

            command = ['unzip', '-o', source, '-d', destination]
            logging.info(command)
            result = subprocess.run(command, check=True, text=True, capture_output=True, timeout=60, cwd=destination)
            logging.info(f"Unzip successful:\n{result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Unzip failed:\n{e.stderr}")
            return False

    @staticmethod
    def zip(source, destination):
        logging.info("Inside zipping function")
        if not source or not destination:
            raise ValueError("Both 'source' and 'destination' must be provided")

        logging.info("Ensure the zip file path's directory exists")
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Zipping logic
        command = ['zip', '-r', destination, os.path.basename(source)]
        logging.info(f"Running command: {' '.join(command)}")
        logging.info(f"source: {source}")
        logging.info(f"destination: {destination}")
        logging.info(command)

        try:
            logging.info(f"Zipping from {source} to {destination}")
            result = subprocess.run(
                command,
                cwd=os.path.dirname(source),
                text=True,
                capture_output=True
            )
            logging.info(f"Zipping successful:\n{result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Zipping failed:\n{e.stderr}")
            return False

    @staticmethod
    def gzip(source, destination):
        logging.info("Inside unzipping function")
        if not source or not destination:
            raise ValueError("Both 'source' and 'destination' must be provided")

        # Ensure destination directory exists
        destination_dir = os.path.dirname(destination)
        if destination_dir and not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        logging.info(f"source: {source}")
        logging.info(f"destination: {destination}")

        try:

            logging.info(f"Unzipping from {source} to {destination}")

            command = ['gzip', '-c', source]
            logging.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command, 
                check=True, 
                text=True, 
                stdout=open(destination, 'wb'),
                timeout=60
                )
            logging.info(f"gzip successful:\n{result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"gzip failed:\n{e.stderr}")
            return False

    @staticmethod
    def gunzip(source, destination):
        logging.info("Inside unzipping function")
        if not source or not destination:
            raise ValueError("Both 'source' and 'destination' must be provided")

        # Ensure destination directory exists
        destination_dir = os.path.dirname(destination)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        logging.info(f"source: {source}")
        logging.info(f"destination: {destination}")

        try:
            with open(destination, "wb") as f_out:
                command = ["gunzip", "-c", source]
                logging.info(f"Running command: {' '.join(command)}")
                result = subprocess.run(
                    command, 
                    check=True, 
                    stdout=f_out, 
                    stderr=subprocess.PIPE, 
                    timeout=60
                )

            logging.info("Gunzip successful.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Gunzip failed:\n{e.stderr}")
            return False

    @staticmethod
    def list_directory_contents(dir_path):
        logging.info(f"Directory path: {dir_path}")
        try:
            command = ['ls', '-la']
            result = subprocess.run(
                command,
                cwd=dir_path,
                text=True,
                capture_output=True
            )
            
            output = f"Listing Directories:\n{result.stdout}"
            logging.info(output)
            return output
        
        except subprocess.CalledProcessError as e:
            logging.error("Error: {e.stderr.strip()}")
            return False

    @staticmethod
    def run_python_script(py_file='', params={}, env_vars={}, paths=[]):
        """To Run python3 scripts via subprocess.
            Args::
                py_file: File to be triggered.
                params: params to send to triggered file.
                env_vars: If env_vars to be set during running script.
                paths: To use additional packages while triggering the script. Provide the parent dirs of the packages to be used.
            Response::
                Returns output in the form :- 
                    {'status':<status>, 'output':<output>} 
                    <output> is the response printed from the script or the error while running the script.
        """

        result = {
            'status': 'unprocessed',
            'output': 'no output'
            }

        try:
            command = ["python3", py_file]
            logging.info(f"Running command: {' '.join(command)}")
            for key,value in params.items():
                command.append(f"-{key}")
                command.append(value)

            final_env_vars = os.environ.copy()
            logging.info(f"Environment Vars: {env_vars}")

            if paths:
                if final_env_vars.get("PYTHONPATH", ''):
                    paths.append(final_env_vars.get("PYTHONPATH"))
                final_env_vars["PYTHONPATH"] = ":".join(paths)
            final_env_vars.update(env_vars)

            logging.info(f"command:- {command}")
            process = subprocess.run(command, capture_output=True, text=True, check=True, env=final_env_vars)

            # logging.info("Print the whole process:-")
            # logging.info(process)

            logs = process.stderr
            logging.info("Printing Logs")
            logging.info(logs)

            logging.info('Print Output:-')
            result_string = process.stdout
            logging.info(result_string)

            logging.info('Loading JSON result')
            result = json.loads(result_string)
            result['status'] = result.get('status')
            result['output'] = result.get('output').replace("<No Output>", '')
            logging.info(f"Result after loading json :- {result}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error: Command failed with return code {e.returncode}")

            error_message = (
                f"{type(e).__name__} : \n"
                f"Command failed with return code {e.returncode} \n"
                f"Stderr: {e.stderr} \n"
                f" Stdoutput: {e.output}"
                )

            result['status'] = 'error'
            result['output'] = error_message

        except Exception as e:
            error_message = (
                f"{type(e).__name__} : \n"
                f"Stderr: {e.stderr} \n"
                f" Stdoutput: {e.output}"
            )
            result['status'] = 'error'
            result['output'] = error_message
        finally:
            logging.info(f"Result :- \n {result}")
            return result