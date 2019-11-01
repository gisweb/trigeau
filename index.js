import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {Image as ImageLayer, Tile as TileLayer} from 'ol/layer';
import {defaults as defaultInteractions} from 'ol/interaction';
import ImageWMS from 'ol/source/ImageWMS';
import OSM from 'ol/source/OSM';


var GISCLIENT_URL = "http://trigeau.servergis.it/gisclient/";
var MAPSET = "camogli_gisweb";
var PROJECT = "trigeau";
var mapset_prestazioni;
var layer_0;
var resultLayer;
var lay_vuoto = 'vuoto.vuoto';
var map1,map2;

//Inizializzazione della mappa con json GC
$.ajax({
  url: GISCLIENT_URL + 'services/gcmap.php',
  dataType: "jsonp",
  data:{"mapset":MAPSET},
  jsonpCallback: "jsoncallback",
  async: false,
  success: initMap

})

//Setto i dati nsi, nfi per la mappa di base
$.ajax({
  url: GISCLIENT_URL + 'template/trigeau/info.php',
  dataType: "jsonp",
  data:{"scenario":MAPSET},
  jsonpCallback: "jsoncallback2",
  async: false,
  success: function (response){
    mapset_prestazioni = response;
    console.log(mapset_prestazioni)
  }

})

function getLivelliSelezionati(){
  var elenco=[];
  $('[name=livelli]').each(function(){
    if ($(this).is(":checked")){
      elenco.push($(this).val())
    }
  })
  return elenco
}

function setLayers(){

  var anni = $('[name=tempi_ritorno]:checked').val();
  var vasca = $('[name=vasca]:checked').val();
  var scenario = $("#scenario").val();
  var elenco=[];
  var layerName;
  var layers;
  if (anni!='0'){  
    $('[name=livelli]').each(function(){
      if ($(this).is(":checked")){
        layerName = $(this).val();
        if (vasca == 'piena'){
          layerName = layerName.replace('grp_risultati','grp_risultati_vp');
        } 
        layerName = layerName + '_' + anni + 'y';
        elenco.push(layerName)
      }
    });
  }

  if (elenco.length>0){
    layers = elenco.join(',');
  }
  else{
    layers = lay_vuoto;
  }

  console.log(scenario + ' ' + layers);

  var wms1 = layer_0.getSource();
  wms1.updateParams({'LAYERS': ''});
  wms1.updateParams({'LAYERS': layers});
  wms1.refresh();

  var wms2 = resultLayer.getSource();
  wms2.updateParams({'MAP':scenario,'LAYERS': ''});
  wms2.updateParams({'MAP':scenario, 'LAYERS': layers});
  wms2.refresh();

  $.ajax({
    url: GISCLIENT_URL + 'template/trigeau/info.php',
    dataType: "jsonp",
    data:{"scenario":scenario,"anni":anni,"vasca":vasca},
    jsonpCallback: "jsoncallback",
    async: false,
    success: setPrestazioni
  })


}

$('#scenario').change(function(){

  setLayers();
  //console.log(map1.getView().getCenter())

})

$('[name=tempi_ritorno]').change(function(){

  setLayers();
  //console.log(map1.getView().getCenter())

})

$('[name=livelli]').click(function(){

  setLayers();
  
})

$('[name=vasca]').click(function(){

  setLayers();
  
})


function setPrestazioni( response ){
  var x,resp,nsr,nfr;
  var nsi0=0;
  var nfi0=0;
  var nsiS=0;
  var nfiS=0;
  var anni = $('[name=tempi_ritorno]:checked').val();

  if (anni=='0'){
    $("#nsi0").text("");
    $("#nfi0").text("");
    $("#nsiS").text("");
    $("#nfiS").text("");    
    $("#nsr").text("");
    $("#nfr").text("");
    return;
  }

  for (x in mapset_prestazioni){
    if (x.indexOf('_'+anni+'Y')>-1){
      nsi0=mapset_prestazioni[x]["nsi"]||0;
      nfi0=mapset_prestazioni[x]["nfi"]||0;
      for (resp in response){
        nsiS=response[resp]["nsi"]||0;
        nfiS=response[resp]["nfi"]||0;
      }
    }
  }

  if (nsi0!=0){
    nsr = (((nsi0 - nsiS)/nsi0)*100).toFixed(2) + ' %';
  }
  else{
    nsr = "Errore: NSIo = 0 o indefinito"
  }

  if (nfi0!=0){
    nfr = (((nfi0 - nfiS)/nfi0)*100).toFixed(2) + ' %';
  }
  else{
    nfr = "Errore: NFIo = 0 o indefinito"
  }

  $("#nsi0").text((nsi0*100).toFixed(2) + ' %');
  $("#nfi0").text((nfi0*100).toFixed(2) + ' %');
  $("#nsiS").text((nsiS*100).toFixed(2) + ' %');
  $("#nfiS").text((nfiS*100).toFixed(2) + ' %');
  $("#nsr").text(nsr);
  $("#nfr").text(nfr);

}

function initMap( response ){
  for (var i=0; i<response.mapsets.length;i++){
    if (response.mapsets[i].mapset_name != MAPSET){
      $('#scenario')
        .append($("<option></option>")
          .attr("value",response.mapsets[i].mapset_name)
          .text(response.mapsets[i].mapset_title)); 
    }
  }

  var options = response.mapOptions

  var roadLayer = new TileLayer({
    source: new OSM()
  });

  var sottoBacini =  new ImageLayer({
      extent: [
        1019789.1483398619,
        5518775.906779552,
        1020400.6445660581,
        5519387.403005749
      ],
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_subcatchment'},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  var areaStudio =  new ImageLayer({
      extent: [
        1019789.1483398619,
        5518775.906779552,
        1020400.6445660581,
        5519387.403005749
      ],
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_area_studio'},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  var reteLayer =  new ImageLayer({
      extent: [
        1019789.1483398619,
        5518775.906779552,
        1020400.6445660581,
        5519387.403005749
      ],
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_rete'},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  layer_0 =  new ImageLayer({
      extent: [
        1019789.1483398619,
        5518775.906779552,
        1020400.6445660581,
        5519387.403005749
      ],
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  resultLayer =  new ImageLayer({
      extent: [
        1019789.1483398619,
        5518775.906779552,
        1020400.6445660581,
        5519387.403005749
      ],
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET},
        ratio: 1,
        serverType: 'mapserver'
      })
    })


  var view = new View({
    center: options.center,
    zoom: options.levelOffset
  });

  map1 = new Map({
    interactions: defaultInteractions({
      onFocusOnly: true
    }),
    target: 'principale',
    layers: [roadLayer,sottoBacini,areaStudio,reteLayer,layer_0],
    view: view
  });

  map2 = new Map({
    interactions: defaultInteractions({
      onFocusOnly: true
    }),
    target: 'secondaria',
    layers: [sottoBacini,areaStudio,reteLayer,resultLayer],
    view: view
  });

}
