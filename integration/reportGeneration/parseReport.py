class parseReport():
    def __init__(self, reportJSON):
        # define instance variables
        self.reportJSON = reportJSON
        self.version = ""
        self.platform = ""
        self.createdAt = ""
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.percentagePassed = 0
        self.duration = 0
        self.testData = []

    def summary(self):
        if 'summary' in self.reportJSON['report']:
            summary = self.reportJSON['report']['summary']

            if 'created_at' in self.reportJSON['report']:
                self.createdAt = self.reportJSON['report']['created_at']

            # setting up summary fields
            if 'passed' in summary:
                self.passed = summary['passed']
            if 'failed' in summary:
                self.failed = summary['failed']
            if 'num_tests' in summary:
                self.total = summary['num_tests']
            if 'duration' in summary and type(summary['duration']) == float:
                self.duration = self.duration = round(summary['duration'], 5)
            if self.total > 0:
                try:
                    self.percentagePassed = int((self.passed / self.total) * 100)
                except ZeroDivisionError:
                    self.percentagePassed = 0

    def tests(self):
        if 'report' in self.reportJSON and 'tests' in self.reportJSON['report']:
            testList = self.reportJSON['report']['tests']

            for test in testList:
                failureMSG = ""
                if 'run_index' in test and 'name' in test and 'outcome' in test and 'duration' in test:
                    if test['outcome'] == 'passed':
                        test['outcome'] = "Pass"
                        testHighlight = "bg-success"
                    elif test['outcome'] == 'failed':
                        test['outcome'] = 'Fail'
                        testHighlight = "bg-danger"

                        if 'setup' in test and 'longrepr' in test['setup']: failureMSG = test['setup']['longrepr']
                        elif 'call' in test and 'longrepr' in test['call']: failureMSG = test['call']['longrepr']
                        elif 'teardown' in test and 'longrepr' in test['teardown']: failureMSG = test['teardown']['longrepr']

                        failureMSG = failureMSG.replace("`", r"\`")

                    else:
                        test['outcome'] = 'Other'
                        testHighlight = "bg-light"

                    self.testData.append({'id': str(test['run_index']+1), 'testName': test['name'], 'result': test['outcome'], 'duration': round(test['duration'], 5), 'highlight' : testHighlight, 'failureMSG' : failureMSG})


    def generate(self):
        self.summary()
        self.tests()