import os
import os.path

class SimpleHtmlFilelistGenerator:
    # start from this directory
    base_dir = None

    def __init__(self):
        self.base_dir = 'html'

    def print_html_header(self):
        print '''<html>
<body>
<code>
'''

    def print_html_footer(self):
        print '''</code>
</body>
</html>
'''

    def processDirectory(self, args, dirname, filenames):
        for filename in sorted(filenames):
            rel_path = os.path.join(dirname, filename)

            if os.path.isfile(rel_path):
                href = "<a href=\"%s\">%s</a>" % (filename, filename)
                print '&nbsp;' * 4, href, '<br>'

    def start(self):
        self.print_html_header()
        os.path.walk(self.base_dir, self.processDirectory, None)
        self.print_html_footer()

gen = SimpleHtmlFilelistGenerator()
gen.start()

