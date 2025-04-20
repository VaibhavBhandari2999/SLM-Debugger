import os
import subprocess
import sys

from . import PostgreSQLSimpleTestCase


class PostgresIntegrationTests(PostgreSQLSimpleTestCase):
    def test_check(self):
        """
        Tests the Django check command with specific settings and environment modifications.
        
        This function runs the Django check command with the specified settings and environment modifications. It ensures that the command completes without errors.
        
        Parameters:
        None
        
        Returns:
        None
        
        Key Steps:
        1. Creates a copy of the current environment.
        2. Removes the 'DJANGO_SETTINGS_MODULE' from the environment if it exists.
        3. Sets the 'PYTHONPATH' to include the parent directory of the current file.
        4. Executes the Django check
        """

        test_environ = os.environ.copy()
        if "DJANGO_SETTINGS_MODULE" in test_environ:
            del test_environ["DJANGO_SETTINGS_MODULE"]
        test_environ["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "../../")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "django",
                "check",
                "--settings",
                "integration_settings",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__),
            env=test_environ,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
