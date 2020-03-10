# -*- coding: UTF-8 -*-
import psycopg2
from config import conn

base="""
<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:se="http://www.opengis.net/se" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.1.0/StyledLayerDescriptor.xsd">
%s
</StyledLayerDescriptor>
"""

layer="""
  <NamedLayer>
    <se:Name>%s</se:Name>
    <UserStyle>
      <se:Name>%s</se:Name>
      <se:FeatureTypeStyle>
      	%s
      </se:FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
"""

rule="""
<se:Rule>
  <ogc:Filter>
     <ogc:PropertyIsEqualTo>
       <ogc:PropertyName>%s</ogc:PropertyName>
       <ogc:Literal>%s</ogc:Literal>
     </ogc:PropertyIsEqualTo>
   </ogc:Filter>
   %s
</se:Rule>
"""

style_arc="""
  <se:LineSymbolizer>
    <se:Stroke>
      <se:SvgParameter name="stroke">%s</se:SvgParameter>
      <se:SvgParameter name="stroke-width">4</se:SvgParameter>
      <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
      <se:SvgParameter name="stroke-linecap">square</se:SvgParameter>
    </se:Stroke>
  </se:LineSymbolizer>
"""

style_node="""
  <se:PointSymbolizer>
    <se:Graphic>
      <se:Mark>
        <se:WellKnownName>circle</se:WellKnownName>
        <se:Fill>
          <se:SvgParameter name="fill">#2323f7</se:SvgParameter>
        </se:Fill>
        <se:Stroke>
          <se:SvgParameter name="stroke">%s</se:SvgParameter>
          <se:SvgParameter name="stroke-width">0.5</se:SvgParameter>
        </se:Stroke>
      </se:Mark>
      <se:Size>7</se:Size>
    </se:Graphic>
  </se:PointSymbolizer>
"""

style_subcatchment="""
  <se:PolygonSymbolizer>
    <se:Fill>
      <se:SvgParameter name="fill">%s</se:SvgParameter>
    </se:Fill>
    <se:Stroke>
      <se:SvgParameter name="stroke">#232323</se:SvgParameter>
      <se:SvgParameter name="stroke-width">1</se:SvgParameter>
      <se:SvgParameter name="stroke-linejoin">bevel</se:SvgParameter>
    </se:Stroke>
  </se:PolygonSymbolizer>
"""


def generaSld(resultid=''):
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
        sql="SELECT 'view_arc' as layer_name,'arc_style' as layer_style,arc_id,mfull_dept*100 as val FROM plonegis.rpt_arcflow_sum WHERE result_id=%s;"
        print (sql %(resultid, ))
        cursor.execute(sql,(resultid, )) 
        rows=cursor.fetchall()
        s_rule=''
        for row in rows:
            arc_id = row[2]
            coeff = row[3]
            color="#ff0000"
            if coeff <= 50:
                color="#7bfd7b"
            elif coeff<=70:
                color="#7bdddd"
            elif coeff<=80:
                color="#ff7f00"
            s_style = (style_arc %color).strip()    
            s_rule = (s_rule + rule%('arc_id',arc_id, s_style, )).strip()
        s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()

    if lay=='node':
        sql="SELECT 'view_node' as layer_name,'node_style' as layer_style,node_id,tot_flood*1000 as val FROM plonegis.rpt_nodeflooding_sum WHERE result_id=%s;"
        cursor.execute(sql,(resultid, )) 
        rows=cursor.fetchall()
        s_rule=''
        for row in rows:
            node_id = row[2]
            coeff = row[3]
            color="#232323"
            if coeff <= 1:
                color="#2323f7"
            elif coeff<=5:
                color="#535353"
            elif coeff<=10:
                color="#325780"
            s_style = (style_node %color).strip()
            s_rule = (s_rule + rule%('node_id',node_id, s_style, )).strip()
        s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()

    if lay=='sub':
        sql="SELECT 'view_subcatchment' as layer_name,'subcatcments_style' as layer_style,subc_id,runoff_coe as val FROM plonegis.rpt_subcathrunoff_sum WHERE result_id=%s;"
        cursor.execute(sql,(resultid, )) 
        rows=cursor.fetchall()
        s_rule=''
        for row in rows:
            subc_id = row[2]
            coeff = row[3]
            color="#7bbcbc"
            if coeff <= 0.13:
                color="#fdfdfd"
            elif coeff<=0.48:
                color="#ddfddd"
            elif coeff<=0.96:
                color="#7bdddd"
            s_style = (style_subcatchment %color).strip()
            s_rule = (s_rule + rule%('subc_id',subc_id, s_style, )).strip()
        s_layer = s_layer + (layer %(row[0], row[1], s_rule, )).strip()   

    cursor.close()   

    s_result = (base %s_layer).strip()

    connection.close()


    return s_result