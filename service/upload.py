#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
1 ATTIVARE IL VENV source bin/activate
2 lanciare python upload.py

per la produzione usare supervisord

Url di prove
http://127.0.0.1:8080/simulazione?callback=jsoncallback&rete=CS&imp=15&regime=CAM&schema=H&anni=2

"""



import os
import cherrypy
from cherrypy.lib import static
from swmm5.swmm5tools import SWMM5Simulation
import psycopg2
from config import conn
from os.path import isfile
from datetime import datetime
import random
import string

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

config = {
    'global' : {
        'server.socket_host' : '127.0.0.1',
        'server.socket_port' : 8080
    }
}

def randomString(stringLength=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



class App:

    def pippo(self,f):
        line=f.readline()
        print line
        line=f.readline()
        print line        
        line=f.readline()
        print line        
        line=f.readline()
        print line        
        line=f.readline()
        print line

        print randomString()

    @cherrypy.expose
    def readData(self,f,sessionTitle=''):
        """
        legge tutta la sezione di dati del titolo partendo dal titolo fino alle righe vuote
        """
        

        # Open a file
        fileName="../data/CS_H.inp"
        f = open(fileName, "r")

        line = f.readline()
        while line.strip()!="[SUBCATCHMENTS]":
            line=f.readline()
        f.readline()
        f.readline()
        line=f.readline()

        count=1
        data=[]
        v=[x for x in line.split(' ') if x not in ['','\n']]
        while v!=[]:
            data.append(v)
            line=f.readline()
            v=[x for x in line.split(' ') if x not in ['','\n']]

            ##s mi perdo qualcosa non va in loop
            count=count+1
            if count==1000000:
                break

        print data

        self.pippo(f)


        line=f.readline()
        print line
        line=f.readline()
        print line        
        line=f.readline()
        print line        
        line=f.readline()
        print line        
        line=f.readline()
        print line

        # Close opend file
        f.close()

        return randomString()
        return str(data)







        with open(fileName) as f:
            for line in f:
                if line.strip()=="[SUBCATCHMENTS]":
                    import pdb;pdb.set_trace()
                    f.seek(1,1)
                    break

        #import pdb;pdb.set_trace()
        index=0
        if index:
            index = index + 8
            while ll[index].strip():
                data = ll[index].split(" ")

                print data
                #s=s + ll[index]
                index=index+1




    @cherrypy.expose
    def simulazione(self,rete='CS',schema='H',imp='15',regime='CAM',anni='2',callback='',_=''):

        #apro il file di base e sostituisco i valori
        fileName = "../data/%s_%s.inp" %(rete,schema)
        zona="Chicago"
        rsRandom = randomString()

        sxInpFile = "/tmp/%s_%s_%s_sx.inp" %(rete,schema,rsRandom)
        dxInpFile = "/tmp/%s_%s_%s_dx.inp" %(rete,schema,rsRandom)


        sxFile = open(sxInpFile, 'w')
        dxFile = open(dxInpFile, 'w')

        with open(fileName) as f:


            newlines=[]
            for line in f:
                if "[RAINGAGES]" in line:
                    print line
                    rgFound=True
                if rgFound and line[:3] == "RG1":
                    s=line[:75]+('"'+path+regime+'-'+zona+anni+'Y.txt"').ljust(212,' ')
                    s=s+(regime + "-RG").ljust(13,' ')
                    s=s + line[300:]
                    line=s
                    print line
                    rgFound=False

                if "[SUBCATCHMENTS]" in line:
                    print line
                    subCatFound=True
                if subCatFound:
                    if line[:1] == "S":
                        line = line[:68] + (imp+".0000").ljust(13,' ') + line[81:]
                        print line
                if line.strip()=="":
                    subCatFound=False

                sxFile.write(line)

            f.close()

        sxFile.close()

        return
        st=SWMM5Simulation(fName)
        files=st.getFiles()
        
        if isfile(files[1]):
            print files[1]
            self.result(files[1])



    def result(self,reportfile):

        with open(reportfile,'r') as ff:

            data=False
            section=False
            s=""
            ll=[line.strip() for line in ff]
            index=0

            for index in range(0,len(ll)):
                if "Subcatchment Runoff Summary" in ll[index]:
                    break

            #import pdb;pdb.set_trace()
            if index:
                index = index + 8
                while ll[index].strip():
                    data = ll[index].split(" ")

                    print data
                    #s=s + ll[index]
                    index=index+1




            return s

            for line in ff:

                if section and data:
                    if not "-" in line:
                        if not "*" in line:
                            s=s+line

                if "Subcatchment Runoff Summary" in line:
                    section=True
                if "LID Performance Summary" in line:
                    section=False
    
                if section:
                    if "Subcatchment" in line:
                        data=True


                    
        return s





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

        
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)

        return out % (size, myFile.filename, myFile.content_type)


    @cherrypy.expose
    def download(self,filename=''):


        with open("/tmp/CS_Huxdkbj.dat", "rb") as f:
            byte = f.read(1)
            while byte != "":
                # Do stuff with byte.
                byte = f.read(1)
                print byte


        return 
        path = os.path.join(absDir, 'saved.txt')
        return static.serve_file(path, 'application/x-download',
                                 'attachment', os.path.basename(path))


    @cherrypy.expose
    def query(self,scenario):

        params = cherrypy.request.params

        try:

            connection = psycopg2.connect(**conn)

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print ( connection.get_dsn_parameters(),"\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")  
            record = cursor.fetchone()
            print ("You are connected to - ", record,"\n")


            #import pdb;pdb.set_trace()

            sql = "SELECT * FROM %s.v_trigeau_nsi" %scenario
            cursor.execute(sql)  
            results = cursor.fetchall()
            print results








        except (Exception, psycopg2.Error) as error :
            print  ("Error while connecting to PostgreSQL", error)

        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print ("PostgreSQL connection is closed")





    @cherrypy.expose
    def upload2(self, ufile):
        # Either save the file to the directory where server.py is
        # or save the file to a given path:
        # upload_path = '/path/to/project/data/'
        upload_path = os.path.dirname(__file__)

        # Save the file to a predefined filename
        # or use the filename sent by the client:
        # upload_filename = ufile.filename
        upload_filename = 'saved.txt'

        upload_file = os.path.normpath(
            os.path.join(upload_path, upload_filename))

        upload_file = '../data/saved.inp'

        size = 0
        with open(upload_file, 'wb') as out:
            while True:
                data = ufile.file.read(8192)
                if not data:
                    break
                out.write(data)
                size += len(data)



        import pdb;pdb.set_trace()       
        st=SWMM5Simulation(upload_file)
        version = st.SWMM5_Version()
        nodes = st.SWMM_Nnodes

        out = '''
File received.
Filename: {}
Length: {}
Mime-type: {}
SVMM-version : {}
''' .format(ufile.filename, size, ufile.content_type, version, data)
        return out


if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', config)
