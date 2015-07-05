class NoMatch(Exception):
    def __init__(self, got, expected='', caused_by=None, passthrough=False):
        msg = "Input: %s" % (got)
        if expected:
            msg += ", Expected: %s" % (expected)
        if caused_by is not None and str(caused_by) != msg:
            msg += "\n\tCaused by: %s" % (caused_by)
        Exception.__init__(self, msg)
        self.got = got
        self.expected = expected
        self.caused_by = caused_by
        self.passthrough = passthrough
