import pprint
import sys
import HTML
import file_utils as files
import time


# TODO this needs a lot of working, to print stuff in nice format
# TODO need to rename this since it will be used also for html


def report_testcase(test_name, result):
    '''
    Simple function that will print result at the end of the test in console
    :param test_name:
    :param result:
    :return:
    '''
    sys.stdout.write('We executed {0} tests for the {1} case with the following results: {2}\n'.format(len(result),
                                                                                                       test_name,
                                                                                                       pprint.pformat(
                                                                                                           result)))


def report_testcasehtml(test_name, result):
    '''
    This function will generate a html
    :param test_name:
    :param result:
    :return:
    '''
    # TODO we need to add link to jira if test failed in order to create a new bug
    test_results = dict(result)
    result_colours = {'SUCCESS': 'lime', 'FAILED': 'red', 'ERROR': 'yellow'}
    t = HTML.Table(header_row=[test_name, 'Result'])
    for test_id in sorted(test_results):
        # create the colored cell:
        color = result_colours[test_results[test_id]]
        colored_result = HTML.TableCell(test_results[test_id], bgcolor=color)
        # append the row with two cells:
        t.rows.append([test_id, colored_result])
    htmlcode = str(t)
    files.write_file('results-{0}-{1}'.format(test_name, time.strftime("%Y%m%d-%H%M%S")), 'html', htmlcode, 'html')

# class TextReportHandler():
#     def __init__(self, parser):
#         self.parser = parser
#         self.success = 'Success'
#         self.failure = 'Failure'
#
#     def report_testcase(self, test_name, message, result, passed=None):
#         result_str = self.success if result == True else self.failure
#         passed_str = '({0} passed)'.format(passed) if passed != None else ''
#         if result is True:
#             result_str = self.success
#         elif result is False:
#             result_str = self.failure
#         elif result is None:
#             result_str = self.failure
#
#         print self.test_name
#
#         f_suite = self.cfg['formatting']['text']['suite']
#         f_message = self.cfg['formatting']['text']['message']
#         f_result = self.cfg['formatting']['text']['result']
#         print '%d. %s: %s %s %s %s' % (
#         self.id, self.suite.ljust(f_suite), message, '.' * (f_message - len(message)), result_str.rjust(f_result),
#         passed_str)
#
#     def finish_report(self):
#         print 'Total tests: %d Passed: %d Failed: %d Skipped: %d' % (self.id, self.passed, self.failed, self.skipped)
