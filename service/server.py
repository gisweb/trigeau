import cherrypy
from swmm5.swmm5tools import SWMM5Simulation

import os
import os.path

import cherrypy
from cherrypy.lib import static

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)


class FileDemo(object):

    @cherrypy.expose
    def index(self):
        return """
        <html><body>
            <h2>Upload a file</h2>
            <form action="upload" method="post" enctype="multipart/form-data">
            filename: <input type="file" name="myFile" /><br />
            <input type="submit" />
            </form>
            <h2>Download a file</h2>
            <a href='download'>This one</a>
        </body></html>
        """

    @cherrypy.expose
    def upload(self, myFile):
        out = """<html>
        <body>
            myFile length: %s<br />
            myFile filename: %s<br />
            myFile mime-type: %s
        </body>
        </html>"""

        # Although this just counts the file length, it demonstrates
        # how to read large files in chunks instead of all at once.
        # CherryPy reads the uploaded file into a temporary file;
        # myFile.file.read reads from that.
        size = 0

        import pdb;pdb.set_trace()
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)

        return out % (size, myFile.filename, myFile.content_type)


    @cherrypy.expose
    def download(self):
        path = os.path.join(absDir, 'pdf_file.pdf')
        return static.serve_file(path, 'application/x-download',
                                 'attachment', os.path.basename(path))





class Root(object):
    @cherrypy.expose
    def index(self):


        st=SWMM5Simulation('../data/CS_H.inp')




        import pdb;pdb.set_trace()






        
        return 'OKK'
 
 



     
     
        rep = open('./data/CS_H.rpt', 'r') 
        Lines = rep.readlines() 
        count = 0
        html=""
        # Strips the newline character 
        for line in Lines: 
            if line.strip()=="LID Control Summary":
                prt=1
            elif line.strip()=="":
                prt=0
            if prt:
                html = html +  line.strip() + '<br />' 
            
            
        return html
        

tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')

'''
cherrypy.config.update({'server.socket_port': 8090,
                        'engine.autoreload.on': False,
                        'log.access_file': './access.log',
                        'log.error_file': './error.log'})
'''

cherrypy.quickstart(FileDemo(), config=tutconf)
