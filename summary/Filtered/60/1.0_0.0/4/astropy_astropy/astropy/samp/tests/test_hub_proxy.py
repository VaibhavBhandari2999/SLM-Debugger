from ..hub_proxy import SAMPHubProxy
from ..hub import SAMPHubServer

from .. import conf


def setup_module(module):
    conf.use_internet = False


class TestHubProxy:

    def setup_method(self, method):
        """
        Setup method for initializing the SAMPHubServer and SAMPHubProxy instances.
        
        This method is intended to be called as part of a test suite setup. It starts a SAMPHubServer with the specified parameters and connects a SAMPHubProxy to it. The server runs in 'multiple' mode with a single worker process, and the proxy is configured to connect to the server with a single worker process as well.
        
        Parameters:
        method (function): The test method that this setup is associated with
        """


        self.hub = SAMPHubServer(web_profile=False, mode='multiple', pool_size=1)
        self.hub.start()

        self.proxy = SAMPHubProxy()
        self.proxy.connect(hub=self.hub, pool_size=1)

    def teardown_method(self, method):
        """
        Teardown method for cleaning up resources after tests.
        
        This method is called after each test method to ensure that all resources are properly cleaned up.
        
        Parameters:
        method (function): The test method that has just been executed.
        
        Returns:
        None: This method does not return any value. It is used to perform cleanup actions such as disconnecting from a proxy and stopping a hub.
        
        Notes:
        - If the proxy is connected, it will be disconnected.
        - The hub will be stopped.
        """


        if self.proxy.is_connected:
            self.proxy.disconnect()

        self.hub.stop()

    def test_is_connected(self):
        assert self.proxy.is_connected

    def test_disconnect(self):
        self.proxy.disconnect()

    def test_ping(self):
        self.proxy.ping()

    def test_registration(self):
        result = self.proxy.register(self.proxy.lockfile["samp.secret"])
        self.proxy.unregister(result['samp.private-key'])


def test_custom_lockfile(tmpdir):

    lockfile = tmpdir.join('.samptest').realpath().strpath

    hub = SAMPHubServer(web_profile=False, lockfile=lockfile, pool_size=1)
    hub.start()

    proxy = SAMPHubProxy()
    proxy.connect(hub=hub, pool_size=1)

    hub.stop()
