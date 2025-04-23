import pytest


class TestPasteCapture:
    @pytest.fixture
    def pastebinlist(self, monkeypatch, request):
        pastebinlist = []
        plugin = request.config.pluginmanager.getplugin("pastebin")
        monkeypatch.setattr(plugin, "create_new_paste", pastebinlist.append)
        return pastebinlist

    def test_failed(self, testdir, pastebinlist):
        """
        This function runs a test suite using pytest and captures the pastebin link for failed tests.
        
        Parameters:
        testdir (pytest.Testdir): A pytest Testdir object used to create and run test files.
        pastebinlist (list): A list to store the pastebin links for failed tests.
        
        Returns:
        None: The function does not return anything. It modifies the `pastebinlist` parameter in place.
        
        Key Steps:
        1. Creates a test file with three test functions: `test
        """

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
        Tests the inline execution of a test file with the `--pastebin=all` option.
        
        Args:
        testdir (pytest.Testdir): A pytest Testdir instance used to create and run test files.
        pastebinlist (list): A list that will store the generated pastebin URLs.
        
        Returns:
        None: This function does not return any value. It modifies the `pastebinlist` parameter to store the generated pastebin URLs.
        
        This function creates a test file with three test cases:
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
