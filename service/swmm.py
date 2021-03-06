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
from sld import generaSld
import json


localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

config = {
    'global' : {
        'server.socket_host' : '127.0.0.1',
        'server.socket_port' : 4080
    }
}

def randomString(stringLength=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



class App:

    result_id=datetime.today().strftime("%Y%m%d%H%M%S")

    @cherrypy.expose
    def trigeau_sld(self,resid=''):
        return generaSld(resid)

    @cherrypy.expose
    def getExtent(self,schema_id,callback='',_=''):
        """
        """
        """
        connection = psycopg2.connect(**conn)
        cursor = connection.cursor()
        sql="select round(st_x(st_centroid(st_envelope(st_transform(the_geom,3857))))::numeric,2) as x,\
        round(st_y(st_centroid(st_envelope(st_transform(the_geom,3857))))::numeric,2) as y\
        from plonegis.view_subcatchment where schema_id=%s;"
        cursor.execute(sql,(schema_id, )) 
        row=cursor.fetchone()
        cursor.close()   
        connection.close()
        x=float(row[0]);y=float(row[1])
        """
        x=0;y=0
        if "inscostiero" in schema_id:
            y=5519111;x=1020126
        elif "ins_collinare" in schema_id:
            y=5519015;x=1020126
        elif "ins_montano" in schema_id:
            y=5519015;x=1020400
     
        if callback:
            return callback + '(' + json.dumps(dict(success=1,schema=schema_id,x=x,y=y)) + ')'
        else:
            return dict(success=1,schema=schema_id,x=x,y=y)
    
    def saveData(self,rows=[],result_id='',schema_id='',table=''):
        """
        """

        try:
            connection = psycopg2.connect(**conn)

            cursor = connection.cursor()

            '''
            #import pdb;pdb.set_trace()
            

            sql="select * from plonegis."+table+" where schema_id=%s and result_id=%s"
            scenario='inscostiero_light'
            result='pippo'

            cursor.execute(sql,[scenario,result]) 
            results=cursor.fetchall()

            return results

            '''
            sqlInsert=""
            if table=='rpt_subcathrunoff_sum':
                sqlInsert="INSERT INTO plonegis."+table+"\
                    (result_id,schema_id,subc_id,tot_precip,tot_runon,tot_evap,tot_infil,tot_runoff,tot_runofl,peak_runof,runoff_coe)\
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            elif table=='rpt_nodeflooding_sum':
                sqlInsert="INSERT INTO plonegis."+table+"\
                    (result_id,schema_id,node_id,hour_flood,max_rate,time_days,time_hour,tot_flood,max_ponded)\
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            elif table=='rpt_arcflow_sum':
                sqlInsert="INSERT INTO plonegis."+table+"\
                    (result_id,schema_id,arc_id,arc_type,max_flow,time_days,time_hour,max_veloc,mfull_flow,mfull_dept)\
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            elif table=='indici':
                sqlInsert="INSERT INTO plonegis."+table+" (result_id,schema_id,nfi,nsi,pr,vr,reportfile) values (%s,%s,%s,%s,%s,%s,%s);"
    

            sql="DELETE FROM plonegis.%s WHERE schema_id='%s' and right(result_id,2)='%s';" %(table,schema_id,result_id[-2:])
            cursor.execute(sql) 
            connection.commit()

            for row in rows:
                row=tuple([result_id,schema_id]+row)
                print (sqlInsert %row)
                cursor.execute(sqlInsert,row) 

            connection.commit()

        except (Exception, psycopg2.Error) as error :
            print  ("Error while connecting to PostgreSQL", error)

        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print ("PostgreSQL connection is closed")

    def getArea(self,imp,tipo,areaS,conv):
        imp=int(imp)
        conv=int(conv)
        areaS=float(areaS)
        area=0
        params={"pp":[0.05,0.2],"tv":[0.8,0.667]}
        coeff=params[tipo][0] if imp<45 else params[tipo][1]
        area=areaS*imp*coeff*conv #area moltiplicata per 10^4
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
            if s not in["","\n","\r\n"]:
                row.append(s)
        return row

    @cherrypy.expose
    def simulazione(self,schema_id='',imp='15',regime='CAM',anni='2',drwh='',convpp='',convtv='',callback='',_=''):

        self.callback=callback
        inpPath = "/apps/trigeau/data"

        self.result_id=datetime.today().strftime("%Y%m%d%H%M%S")


        #self.path = inpPath

        #se drwh richiamo la stesa funzione per modificare il drwh
        #if drwh and drwh!="DRWH_OK":

        #apro il file di base e sostituisco i valori
        if drwh=='SI':  
            if int(imp)<30:
                return self.render(result=dict(success=0,message='Superficie impermeabile deve essere > 15%'))

            dxresult = self.simulazione(schema_id=schema_id,imp=imp,regime=regime,anni=anni,drwh='DX',callback=callback)
            #drwh='DX'
            #print 'DRWH SI'
            fileName = "%s/%s.inp" %(inpPath,schema_id)
            
        elif drwh=='DX': 
            #print 'DRWH DX' 
            fileName = "%s/%s_drwh.inp" %(inpPath,schema_id)
            imp=int((int(imp)-30)/0.7)
        else:      
            #print 'DRWH NO'    
            fileName = "%s/%s.inp" %(inpPath,schema_id)

        zona="Chicago"

        rsRandom = randomString()

        #mi calcolo l'extent
        ret = self.getExtent(schema_id=schema_id)
        xCenter=0;yCenter=0
        if ret:
            xCenter=ret["x"]
            yCenter=ret["y"]

        sxInpFile = "/tmp/%s_%s_sx.inp" %(schema_id,rsRandom)
        dxInpFile = "/tmp/%s_%s_dx.inp" %(schema_id,rsRandom)

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
            if line.strip()=='[LID_CONTROLS]':
                idxLidControls = index
            if line.strip()=='[LID_USAGE]':
                idxLidUsage = index
            if line.strip()=='[ADJUSTMENTS]':
                idxAdjustments = index


            llsx.append(line)
            index=index+1


        #cambio le righe a sx
        v=self.parseRow(lines[idxRainGages+3],'RG')
        s='"%s/raingage/%s-%s%sY.txt"'%(inpPath,regime,zona,anni)
        s=s.ljust(255,' ')
        v[5]=str(s)
        s="RG_%s"%regime
        s=s.ljust(13,' ')
        v[6]=str(s)
        llsx[idxRainGages+3]="".join(v)

        index = idxSubCatchments+3
        v=self.parseRow(lines[index],'SC')
        summAreaLid=dict()
        areaPP=areaTV=0
        while v!=[]:
            if v[0][:1] == "S":
                #cambio la riga su file sx                        
                s="%s.0000"%imp
                s=s.ljust(13,' ')
                v[4]=str(s)

                #genero i dati per LID_USAGE
                if convpp:
                    areaPP=self.getArea(imp,"pp",v[3],convpp)
                    areaLid='{:.4f}'.format(areaPP)
                    lid=[
                        v[0],
                        "PP".ljust(17,' '),
                        "1".ljust(13,' '),
                        areaLid.ljust(19,' '),
                        "5.0000".ljust(13,' '),
                        "5.0000".ljust(13,' '),                                
                        "0.0000".ljust(13,' '),
                        "0".ljust(13,' '),
                        " ".ljust(13,' ')
                    ]
                    leadUsage.append(lid)

                if convtv:
                    areaTV=self.getArea(imp,"tv",v[3],convtv)
                    areaLid='{:.4f}'.format(areaTV)
                    lid=[
                        v[0],
                        "TV".ljust(17,' '),
                        "1".ljust(13,' '),
                        areaLid.ljust(19,' '),
                        "11.0000".ljust(13,' '),
                        "30.0000".ljust(13,' '),
                        "0.0000".ljust(13,' '),
                        "0".ljust(13,' '),
                        " ".ljust(13,' ')
                    ]
                    leadUsage.append(lid)

                summAreaLid[v[0]]=areaPP+areaTV

            llsx[index]="".join(v)+"\n"
            index=index+1
            v=self.parseRow(lines[index],'SC')

        try:
            fsx = open(sxInpFile, 'w')
            fsx.writelines(llsx)
            fsx.close() 
        except IOError as err:
            return self.render(result=dict(success=0,message='IOError:%s %s' %(err.args[-1], sxInpFile)))


        #SIMULAZIONE FILE DI SX
        try:
            st=SWMM5Simulation(str(sxInpFile))
            files=st.getFiles()
            if isfile(files[1]):
                print (files[1])
                sxdx='sx'
                if drwh=='DX':
                    sxdx='dx'
                sxresult = self.parseReport(schema_id,sxdx,files[1],sxInpFile)
        except Exception as err:
            return self.render(result=dict(success=0,message='SWMM5Error:%s %s' %(err, sxInpFile)))

        
        #SE DRWH ESCO
        if drwh == 'DX':
            print 'RITORNO SXRESULT'
            return sxresult
        elif drwh == 'SI':
            return self.render(result=dict(success=1,schema=schema_id,x=xCenter,y=yCenter,resultid=self.result_id,sxresult=sxresult,dxresult=dxresult))

        #ALTRIMENTI SE NON PASSO NE PP NE TV ESCO
        elif not convpp+convtv:
            return self.render(result=dict(success=0,message='MANCA PP O TV'))

        print 'FILE DI DX'
        #genero le righe di dx partendo dalle modifiche a sx
        #copio il file di sx fino a LID_CONTROLS
        for i in range(0,idxLidControls+3):
            lldx.append(llsx[i])

        #cambio le righe subcatchment
        index = idxSubCatchments+3
        v=self.parseRow(lines[index],'SC')
        while v!=[]:
            if v[0][:1] == "S":
                #cambio la riga su file dx       
                area=float(v[3])*pow(10,4)
                areaimp=(area*float(imp))/100
                impdx= int(((areaimp-summAreaLid[v[0]])/(area-summAreaLid[v[0]]))*100)  
                s="%s.0000"%impdx
                s=s.ljust(13,' ')
                v[4]=str(s)

            lldx[index]="".join(v)+"\n"
            index=index+1
            v=self.parseRow(lines[index],'SC')
 
        #aggiungo la sezione costante dei lid_controls
        #import pdb;pdb.set_trace()
        flead = open(inpPath + '/lead_controls.inp','r')
        lldx = lldx + flead.readlines()
        flead.close()

        #aggiungo LID_USAGE nuovo calcolato
        for row in leadUsage:
            lldx.append("".join(row)+"\n")

        #copio le ultime righe da 2 righe prima di adjusteents alla fine
        for i in range(idxAdjustments-2,len(lines)-1):
            lldx.append(lines[i])

        try:
            fdx = open(dxInpFile, 'w')
            fdx.writelines(lldx)
            fdx.close() 
        except IOError as err:
            return self.render(result=dict(success=0,message='IOError:%s %s' %(err.args[-1], dxInpFile)))


        try:
            st=SWMM5Simulation(str(dxInpFile))
            files=st.getFiles()
            if isfile(files[1]):
                print (files[1])
                dxresult = self.parseReport(schema_id,'dx',files[1],dxInpFile)
        except Exception as err:
            return self.render(result=dict(success=0,message='SWMM5Error:%s %s' %(err, dxInpFile)))


        return self.render(result=dict(success=1,schema=schema_id,x=xCenter,y=yCenter,resultid=self.result_id,sxresult=sxresult,dxresult=dxresult))


    def parseReport(self,schema_id,sxdx,reportfile="",inpfile=""):

        result_id=self.result_id+'_'+sxdx
        fileRep = open(reportfile, 'r') 
        lines = fileRep.readlines()
        index = 0 
        for line in lines:

            if line.strip()=='Node Summary':
                idxNodeSum = index

            if line.strip()=='Subcatchment Runoff Summary':
                idxSub = index

            if line.strip()=='Node Flooding Summary':
                idxNodeFlood = index     

            if line.strip()=='Outfall Loading Summary':
                idxNodeOutfall = index     

            if line.strip()=='Link Flow Summary':
                idxLink = index

            index=index+1


        ll=[]
        index=idxNodeSum+5
        v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]
        while v!=[]:
            if v[1]=='JUNCTION':
                ll.append(v)
            index=index+1
            v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]

        nodeCount=len(ll)   

        ll=[]
        index=idxSub+8
        v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]
        while v!=[]:
            ll.append(v)
            index=index+1
            v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]

        self.saveData(table='rpt_subcathrunoff_sum',rows=ll,result_id=result_id,schema_id=schema_id)

        ll=[]
        llMaxRate = []
        nsi=0
        nfi=0
        index=idxNodeFlood+3
        if lines[index].strip()!="No nodes were flooded.":
            index=index+7
            v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]
            while v!=[]:
                try:
                    if float(v[2])>0 and float(v[1])<0.9:
                        llMaxRate.append(v)
                except:
                    pass
                ll.append(v)
                index=index+1
                v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]
            if nodeCount>0:
                nfi=float(len(llMaxRate))/nodeCount

            self.saveData(table='rpt_nodeflooding_sum',rows=ll,result_id=result_id,schema_id=schema_id)


        ll=[]
        count08 = 0
        index = idxLink + 8
        v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]
        while v!=[]:
            try:
                if float(v[7])>=0.8:
                    count08=count08+1
            except:
                pass
            if v[1]=='CONDUIT':
                ll.append(v)
            index=index+1
            v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']]        
 
        if len(ll)>0:
            nsi=count08/float(len(ll))

        self.saveData(table='rpt_arcflow_sum',rows=ll,result_id=result_id,schema_id=schema_id)


        index = idxNodeOutfall + 8
        v=[x.strip() for x in lines[index].split(' ') if x.strip() not in ['','\n']] 
        pr=0;vr=0
        if len(v)>0:
            try:
                pr=float(v[3])
                vr=float(v[4])
            except:
                pass

        ###salvo gli indici
        self.saveData(table='indici',rows=[[nfi,nsi,pr,vr,reportfile]],result_id=result_id,schema_id=schema_id)
        
        return dict(nfi=nfi,nsi=nsi,pr=pr,vr=vr,rpt=reportfile,inp=inpfile)


    def render(self,result):
        """
        restituisce i risultati
        """
        if self.callback:
            return self.callback + '(' + json.dumps(result) + ')'
        else:
            return json.dumps(result)


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
    def getfile(self,filename=''):

        path = os.path.join(absDir, filename)
        return static.serve_file(path, 'application/x-download',
                                 'attachment', os.path.basename(path))


    @cherrypy.expose
    def query(self,scenario):

        params = cherrypy.request.params

        try:

            connection = psycopg2.connect(**conn)

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties

            # Print PostgreSQL version
            cursor.execute("SELECT version();")  
            record = cursor.fetchone()


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
