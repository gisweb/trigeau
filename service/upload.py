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
from sld import base,layer,rule,style_arc,style_node,style_subcatchment

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


    @cherrypy.expose
    def trigeau_sld(self,resultid=''):
        """
        sld per tematizzare i risultati
        """

        connection = psycopg2.connect(**conn)
        cursor = connection.cursor()
        s_layer=''

        v=resultid.split('-')
        lay=v[0]
        resultid=v[1]
 
        if lay=='arc':
            sql="SELECT 'result_arc' as layer_name,'arc_style' as layer_style,arc_id as element_id,mfull_dept*100 as val FROM plonegis.rpt_arcflow_sum WHERE result_id=%s;"
            print (sql %(resultid, ))
            cursor.execute(sql,(resultid, )) 
            rows=cursor.fetchall()
            s_rule=''
            for row in rows:
                element_id = row[2]
                coeff = row[3]
                color="#ff0000"
                if coeff <= 50:
                    color="#7bfd7b"
                elif coeff<=70:
                    color="#7bdddd"
                elif coeff<=80:
                    color="#ff7f00"
                s_style = (style_arc %color).strip()    
                s_rule = (s_rule + rule%(element_id, s_style, )).strip()
            s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()

        if lay=='node':
            sql="SELECT 'result_node' as layer_name,'node_style' as layer_style,node_id as element_id,tot_flood*1000 as val FROM plonegis.rpt_nodeflooding_sum WHERE result_id=%s;"
            cursor.execute(sql,(resultid, )) 
            rows=cursor.fetchall()
            s_rule=''
            for row in rows:
                element_id = row[2]
                coeff = row[3]
                color="#232323"
                if coeff <= 1:
                    color="#2323f7"
                elif coeff<=5:
                    color="#535353"
                elif coeff<=10:
                    color="#325780"
                s_style = (style_node %color).strip()
                s_rule = (s_rule + rule%(element_id, s_style, )).strip()
            s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()

        if lay=='sub':
            sql="SELECT 'result_subcatchment' as layer_name,'subcatcments_style' as layer_style,subc_id as element_id,runoff_coe as val FROM plonegis.rpt_subcathrunoff_sum WHERE result_id=%s;"
            cursor.execute(sql,(resultid, )) 
            rows=cursor.fetchall()
            s_rule=''
            for row in rows:
                element_id = row[2]
                coeff = row[3]
                color="#7bbcbc"
                if coeff <= 0.13:
                    color="#fdfdfd"
                elif coeff<=0.48:
                    color="#ddfddd"
                elif coeff<=0.96:
                    color="#7bdddd"
                s_style = (style_subcatchment %color).strip()
                s_rule = (s_rule + rule%(element_id, s_style, )).strip()
            s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()   

        cursor.close()   

        s_result = (base %s_layer).strip()

        connection.close()


        return s_result


        """
        0.13 #fdfdfd 
        0.48 #ddfddd #232323
        0.96 #7bdddd #232323
        1 
        """






    def calcoloArea(self,imp,tipo,areaS):
        imp=int(imp)
        areaS=float(areaS)
        area=0
        params={"pp":[0.05,0.2],"tv":[0.8,0.667]}
        coeff=params[tipo][0] if imp<45 else params[tipo][0]
        area=imp*coeff
        return area

    def parseRow(self,line,sezione):
        """
        fa il parse della riga

        """
        conf={
            'RG':[0,17,30,43,56,75,330,343,356],
            'SC':[0,17,34,51,68,81,98,115,149],
            'LD':[0,17,34,47,66,79,92,105,118,131]
        }
        row=[]
        if sezione not in conf:
            return []

        v=conf[sezione]
        for i in range (0,len(v)-1):
            start=v[i]
            end=v[i+1]
            s=line[start:end]
            if s not in["","\n"]:
                row.append(s)
        return row
    
    @cherrypy.expose
    def simulazione(self,rete='CS',schema='H',imp='15',regime='CAM',anni='2',convpp='',convtv='',callback='',_=''):

        #apro il file di base e sostituisco i valori
        filePath = "/apps/trigeau/data"
        fileName = "%s/%s_%s.inp" %(filePath,rete,schema)
        fileName = "%s/%s_%s.inp" %(filePath,rete,schema)

        zona="Chicago"

        rsRandom = randomString()

        sxInpFile = "/tmp/%s_%s_%s_sx.inp" %(rete,schema,rsRandom)
        dxInpFile = "/tmp/%s_%s_%s_dx.inp" %(rete,schema,rsRandom)

        sxInpFile = "/tmp/%s_%s_sx.inp" %(rete,schema)
        dxInpFile = "/tmp/%s_%s_dx.inp" %(rete,schema)

        llsx=[]
        lldx=[]
        leadUsage=[]#array co i leadusage calcolati

        html=''

        fileInp = open(fileName, 'r') 
        lines = fileInp.readlines()
        index=0
        for line in lines:
            if line.strip()=='[RAINGAGES]':
                idxRainGages = index
            if line.strip()=='[SUBCATCHMENTS]':
                idxSubCatchments = index
            if line.strip()=='[LID_USAGE]':
                idxLidUsage = index
            if line.strip()=='[ADJUSTMENTS]':
                idxAdjustments = index


            llsx.append(line)
            index=index+1


        #cambio le righe a sx
        v=self.parseRow(lines[idxRainGages+3],'RG')
        s='"%s/%s-%s%sY.txt"'%(filePath,regime,zona,anni)
        s=s.ljust(255,' ')
        v[5]=str(s)
        s="%s-RG"%regime
        s=s.ljust(13,' ')
        v[6]=str(s)
        llsx[idxRainGages+3]="".join(v)

        index = idxSubCatchments+3
        v=self.parseRow(lines[index],'SC')
        summArea=0
        while v!=[]:
            if v[0][:1] == "S":
                #cambio la riga su file sx                        
                s="%s.0000"%imp
                s=s.ljust(13,' ')
                v[4]=str(s)

                #genero i dati per LID_USAGE
                if convpp:
                    area=self.calcoloArea(imp,"pp",v[3])*float(convpp)
                    summArea=summArea+area
                    area='{:.4f}'.format(area)
                    lid=[
                        v[0],
                        "PP".ljust(17,' '),
                        "2".ljust(13,' '),
                        area.ljust(19,' '),
                        "5.0000".ljust(13,' '),
                        "10.0000".ljust(13,' '),                                
                        "0.0000".ljust(13,' '),
                        "0".ljust(13,' '),
                        " ".ljust(13,' ')
                    ]
                    leadUsage.append(lid)

                if convtv:
                    area=self.calcoloArea(imp,"tv",v[3])*float(convtv)
                    summArea=summArea+area
                    area='{:.4f}'.format(area)
                    lid=[
                        v[0],
                        "TV".ljust(17,' '),
                        "1".ljust(13,' '),
                        area.ljust(19,' '),
                        "11.0000".ljust(13,' '),
                        "30.0000".ljust(13,' '),
                        "0.0000".ljust(13,' '),
                        "0".ljust(13,' '),
                        " ".ljust(13,' ')
                    ]
                    leadUsage.append(lid)

            llsx[index]="".join(v)+"\n"
            index=index+1
            v=self.parseRow(lines[index],'SC')

        fsx = open(sxInpFile, 'w')
        fsx.writelines(llsx)
        fsx.close() 

        #FILE DI DX
        #genero le righe di dx partendo dalle modifiche a sx
        #copio iol file di sx fino a LID_USAGE
        for i in range(0,idxLidUsage+3):
            lldx.append(llsx[i])

        #cambio le righe subcatchment
        index = idxSubCatchments+3
        v=self.parseRow(lines[index],'SC')
        while v!=[]:
            if v[0][:1] == "S":
                #cambio la riga su file dx       
                area=float(v[3])*pow(10,4)
                impdx=66#(area*imp-summArea)/(area-summArea)                
                s="%s.0000"%impdx
                s=s.ljust(13,' ')
                v[4]=str(s)

            lldx[index]="".join(v)+"\n"
            index=index+1
            v=self.parseRow(lines[index],'SC')
 
        
        #aggiungo LID_USAGE nuovo calcolato
        for row in leadUsage:
            lldx.append("".join(row)+"\n")

        #copio le ultime righe da 2 righe prima di adjusteents alla fine
        for i in range(idxAdjustments-2,len(lines)-1):
            lldx.append(lines[i])

        fdx = open(dxInpFile, 'w')
        fdx.writelines(lldx)
        fdx.close() 


        result=dict(success=0)

        st=SWMM5Simulation(str(sxInpFile))
        files=st.getFiles()
        if isfile(files[1]):
            print files[1]
            result["sx"]=self.parseReport(files[1])

        st=SWMM5Simulation(str(dxInpFile))
        files=st.getFiles()
        if isfile(files[1]):
            print files[1]
            result["dx"]=self.parseReport(files[1])

    @cherrypy.expose
    def parseReport(self,reportfile="/tmp/CS_H_dxlbijUu.rpt"):

        fileRep = open(reportfile, 'r') 
        lines = fileRep.readlines()
        index = 0 
        for line in lines:
            if line.strip()=='Subcatchment Runoff Summary':
                idxRunoff = index
            index=index+1


        ll=[]
        index=idxRunoff+8
        v=self.parseRow(lines[index],'SC')
        while v!=[]:
            ll.append(v)
            index=index+1
            v=self.parseRow(lines[index],'SC')
 

        return str(ll)
























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
