import pytest


class TestPasteCapture:
    @pytest.fixture
    def pastebinlist(self, monkeypatch, request):
        """
        Generate a list of pastes from a pastebin plugin.
        
        This function sets up a pastebin plugin and configures it to append new pastes to a list. It returns the list of pastes.
        
        Parameters:
        monkeypatch (pytest.MonkeyPatch): A pytest fixture used to monkeypatch the 'create_new_paste' method of the pastebin plugin.
        request (pytest.FixtureRequest): A pytest fixture that provides access to the test request context.
        
        Returns:
        list: A list
        """

        pastebinlist = []
        plugin = request.config.pluginmanager.getplugin("pastebin")
        monkeypatch.setattr(plugin, "create_new_paste", pastebinlist.append)
        return pastebinlist

    def test_failed(self, testdir, pastebinlist):
        testpath = testdir.makepyfile(
            """
            import pytest
            def test_pass():
                pass
            def test_fail():
                assert 0
            def test_skip():
                pytest.skip("")
        """
        )
        reprec = testdir.inline_run(testpath, "--pastebin=failed")
        assert len(pastebinlist) == 1
        s = pastebinlist[0]
        assert s.find("def test_fail") != -1
        assert reprec.countoutcomes() == [1, 1, 1]

    def test_all(self, testdir, pastebinlist):
        """
        Tests the functionality of running a set of test cases with the `--pastebin=all` option.
        
        Args:
        testdir (pytest.Testdir): A pytest test directory object used to create and run test files.
        pastebinlist (list): A list to store the generated pastebin links.
        
        Returns:
        None: This function does not return anything. It generates pastebin links for the test results and stores them in the provided list.
        
        Example:
        >>> test_all(testdir, pastebin
        """

        from _pytest.pytester import LineMatcher

        testpath = testdir.makepyfile(
            """
            import pytest
            def test_pass():
                pass
            def test_fail():
                assert 0
            def test_skip():
                pytest.skip("")
        """
        )
        reprec = testdir.inline_run(testpath, "--pastebin=all", "-v")
        assert reprec.countoutcomes() == [1, 1, 1]
        assert len(pastebinlist) == 1
        contents = pastebinlist[0].decode("utf-8")
        matcher = LineMatcher(contents.splitlines())
        matcher.fnmatch_lines(
            [
                "*test_pass PASSED*",
                "*test_fail FAILED*",
                "*test_skip SKIPPED*",
                "*== 1 failed, 1 passed, 1 skipped in *",
            ]
        )

    def test_non_ascii_paste_text(self, testdir):
        """Make sure that text which contains non-ascii characters is pasted
        correctly. See #1219.
        """
        testdir.makepyfile(
            test_unicode="""\
            def test():
                assert '☺' == 1
            """
        )
        result = testdir.runpytest("--pastebin=all")
        expected_msg = "*assert '☺' == 1*"
        result.stdout.fnmatch_lines(
            [
                expected_msg,
                "*== 1 failed in *",
                "*Sending information to Paste Service*",
            ]
        )


class TestPaste:
    @pytest.fixture
    def pastebin(self, request):
        return request.config.pluginmanager.getplugin("pastebin")

    @pytest.fixture
    def mocked_urlopen(self, monkeypatch):
        """
        monkeypatch the actual urlopen calls done by the internal plugin
        function that connects to bpaste service.
        """
        calls = []

        def mocked(url, data):
            calls.append((url, data))

            class DummyFile:
                def read(self):
                    # part of html of a normal response
                    return b'View <a href="/raw/3c0c6750bd">raw</a>.'

            return DummyFile()

        import urllib.request

        monkeypatch.setattr(urllib.request, "urlopen", mocked)
        return calls

    def test_create_new_paste(self, pastebin, mocked_urlopen):
        result = pastebin.create_new_paste(b"full-paste-contents")
        assert result == "https://bpaste.net/show/3c0c6750bd"
        assert len(mocked_urlopen) == 1
        url, data = mocked_urlopen[0]
        assert type(data) is bytes
        lexer = "python3"
        assert url == "https://bpaste.net"
        assert "lexer=%s" % lexer in data.decode()
        assert "code=full-paste-contents" in data.decode()
        assert "expiry=1week" in data.decode()
