'use strict';

import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {Image as ImageLayer} from 'ol/layer';
import {defaults as defaultInteractions} from 'ol/interaction';
import ImageWMS from 'ol/source/ImageWMS';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';
import TileLayer from 'ol/layer/Tile';
import XYZSource from 'ol/source/XYZ';
import {fromLonLat} from 'ol/proj';
import {register} from 'ol/proj/proj4';
import proj4 from 'proj4';
import Projection from 'ol/proj/Projection';

var chr = require('./charts')

proj4.defs('EPSG:3003','+proj=tmerc +lat_0=0 +lon_0=9 +k=0.9996 +x_0=1500000 +y_0=0 +ellps=intl +units=m +no_defs +towgs84=-104.1,-49.1,-9.9,0.971,-2.917,0.714,-11.68');
register(proj4);

var projection = new Projection({
  code: 'EPSG:3003'
});



export function initMaps ( response=null ){

	console.log(response)

	var sxFilter = 'view_node:"schema_id" = \'' + response.schema + '\';'
	sxFilter = sxFilter + 'view_arc:"schema_id" = \'' + response.schema + '\';'
	sxFilter = sxFilter + 'view_subcatchment:"schema_id" = \'' + response.schema + '\';'

	console.log(sxFilter)

	globalThis.wmsLayersx = new ImageLayer({
	  source: new ImageWMS({
	    url: 'http://www.trigeau.servergis.it/cgi-bin/qgis_mapserv.fcgi?',
	    params: {
	      'MAP':'/home/qgis/projects/trigeau/trigeau.qgz',
	      'LAYERS': 'view_subcatchment,view_arc,view_node',
	      'FILTER': sxFilter,
	      'TRANSPARENT': true,
	    },
	    serverType: 'qgis'                                         
	  })
	});

	var dxFilter = 'view_node_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.result + '\';'
	dxFilter = dxFilter + 'view_arc_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.result + '\';'
	dxFilter = dxFilter + 'view_subcatchment_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.result + '\''

	globalThis.wmsLayerdx = new ImageLayer({
	  source: new ImageWMS({
	    url: 'http://www.trigeau.servergis.it/cgi-bin/qgis_mapserv.fcgi?',
	    params: {
	      'MAP':'/home/qgis/projects/trigeau/trigeau.qgz',
	      'LAYERS': 'view_subcatchment_sum,view_arc_sum,view_node_sum',
	      'FILTER': dxFilter,
	      'TRANSPARENT': true,
	    },
	    serverType: 'qgis'                                         
	  })
	});

	globalThis.Mapview = new View({
	  projection: 'EPSG:3857',
	  center: [response.x, response.y],
	  zoom: 18
	})

	var sxMap = new Map({
	  target: 'principale',
	  layers: [wmsLayersx],
	  view:globalThis.Mapview

	});

	var dxMap = new Map({
	  target: 'secondaria',
	  layers: [wmsLayerdx],
	  view: globalThis.Mapview
	});

}


export function updateMaps ( response ){

  var view = globalThis.Mapview

  $("#loading-gif").hide();
  $("#setFileInp").removeAttr("disabled")

  console.log(response)

  if (response.success==0){
  	alert(response.message)
  	return
  }


	var sxFilter = 'view_node:"schema_id" = \'' + response.schema + '\';'
	sxFilter = sxFilter + 'view_arc:"schema_id" = \'' + response.schema + '\';'
	sxFilter = sxFilter + 'view_subcatchment:"schema_id" = \'' + response.schema + '\';'

	var dxFilter = 'view_node_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.resultid + '\';'
	dxFilter = dxFilter + 'view_arc_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.resultid + '\';'
	dxFilter = dxFilter + 'view_subcatchment_sum:"schema_id" = \'' + response.schema + '\' and "result_id" = \'' + response.resultid + '\''

  var wms1 = globalThis.wmsLayersx.getSource();
  wms1.updateParams({ 'FILTER': sxFilter });

  var wms2 = globalThis.wmsLayerdx.getSource();
  wms2.updateParams({ 'FILTER': dxFilter });

  view.setZoom(18)
  if (response.x){
  	view.setCenter([response.x, response.y])
  }
  wms1.refresh();
  wms2.refresh();


  chr.updateCharts( response );

  //pulsanti report
  if (response.sxresult.rpt){
  	$("#getRepsx").removeAttr("disabled");
  	$("#getRepsx a").attr("href",globalThis.SERVICE_URL + "/getfile?filename=" + response.sxresult.rpt);
  }
  if (response.dxresult.rpt){
  	$("#getRepdx").removeAttr("disabled");
  	$("#getRepdx a").attr("href",globalThis.SERVICE_URL + "/getfile?filename=" + response.dxresult.rpt);
  }


}


