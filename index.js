import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import {Image as ImageLayer, Tile as TileLayer} from 'ol/layer';
import {defaults as defaultInteractions} from 'ol/interaction';
import ImageWMS from 'ol/source/ImageWMS';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';
import Chart from 'chart.js';
import inputSpinner from 'bootstrap-input-spinner';

var GISCLIENT_URL = "http://trigeau.servergis.it/gisclient/";
var MAPSET = getUrlParameter('mapset');
var PROJECT = getUrlParameter('project');
var mapset_prestazioni;
var layer_0;
var resultLayer;
var lay_vuoto = 'vuoto.vuoto';
var map1,map2;
var rete,regime;

function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

if (!MAPSET){
  MAPSET = $('[name=rete]:checked').val()
}

var flag = $('[name=regime]:checked').attr("zona");




//Inizializzazione della mappa con json GC
$.ajax({
  url: GISCLIENT_URL + 'services/gcmap.php',
  dataType: "jsonp",
  data:{"project":PROJECT, "mapset":MAPSET},
  jsonpCallback: "jsoncallback",
  async: false,
  success: initMap

})

//Setto i dati nsi, nfi per la mappa di base
$.ajax({
  url: GISCLIENT_URL + 'template/trigeau/info.php',
  dataType: "jsonp",
  data:{"mapset":MAPSET},
  jsonpCallback: "jsoncallback2",
  async: false,
  success: function (response){
    mapset_prestazioni = response;
  }

})

$(".myspin").inputSpinner();


var ctx = document.getElementById('myChart');

var chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'radar',

    // The data for our dataset
    data: {
        labels: ['VR', 'PR', 'NSR', 'NFR'],
        datasets: [
        {
            label: 'Base',
            data: [100,100,100,100]
        },       
        {
            label: 'Prestazioni',
            borderColor: 'rgba(0,60,136,0.5)',
            data: [0,0,0,0]
        }
        ]
    },

    // Configuration options go here
    options: {}
});


//NUOVO IPOTETICO
function setFileInp(){

  console.log(this)

  $.ajax({
    url: "http://127.0.0.1:8080/upload",
    dataType: "jsonp",
    data:{
      "imp":$('[name=sup_impermeabile]:checked').val(),
      "regime":$('[name=regime]:checked').val(),
      "schema":$('[name=regime]:checked').attr("schema"),
      "anni":$('[name=tempi_ritorno]:checked').val()
    },
    jsonpCallback: "jsoncallback",
    async: false,
    success: initMap

  })


}




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

  if (!layer_0){
    return
  }

  var anni = $('[name=tempi_ritorno]:checked').val();
  var vasca = $('[name=vasca]:checked').val();
  var scenario = $("#scenario").val();
  var supImp = $("#sup_imp").val();
  var supConv = $("#sup_conv").val();

  var elenco=[];
  var elenco2=[];

  var ll = ["lay_coe_defl","lay_stress_net","lay_nodeflood"];
  //var ll = ["lay_coe_defl","lay_stress_net"];



  var layerName,layerGroup;
  var layers;
  var layers2;

  if (flag){
    var regione = $('[name=regime]:checked').attr("zona");
    var intervento = $('[name=intervento]:checked').val();
    for (var i=0;i<ll.length;i++){
      elenco.push('grp_risultati_'+regione+'cs.'+ll[i]+'_' + anni + 'y');
      elenco2.push('grp_risultati_'+regione+intervento+'.'+ll[i]+'_' + anni + 'y');
    }
  }
  else{
    if (vasca == 'piena'){
      layerGroup = 'grp_risultati_vp';
    } 
    else{
      layerGroup = 'grp_risultati';
    }
    for (var i=0;i<ll.length;i++){
      elenco.push(layerGroup+'.'+ll[i]+'_' + anni + 'y');
    }
  }

  if (elenco.length>0){
    layers = elenco.join(',');
  }
  else{
    layers = lay_vuoto;
  }

  if (elenco2.length>0){
    layers2 = elenco2.join(',');
  }
  else{
    layers2 = lay_vuoto;
  }

  if(!flag){
    layers2=layers;
  }

  if (scenario){
    MAPSET=scenario;
  }

  var wms1 = layer_0.getSource();
  wms1.updateParams({'LAYERS': ''});
  wms1.updateParams({'LAYERS': layers});
  wms1.refresh();

  var wms2 = resultLayer.getSource();
  wms2.updateParams({'MAP':MAPSET,'LAYERS': ''});
  wms2.updateParams({'MAP':MAPSET, 'LAYERS': layers2});
  wms2.refresh();

  var url=(flag)?'template/trigeau/info2.php':'template/trigeau/info.php';

  $.ajax({
    url: GISCLIENT_URL + url,
    dataType: "jsonp",
    data:{"mapset":MAPSET,"anni":anni,"vasca":vasca,"regime":$('[name=regime]:checked').val(),"zona":$('[name=regime]:checked').attr("zona")},
    jsonpCallback: "jsoncallback",
    async: false,
    success: setPrestazioni
  })

  console.log(MAPSET)
  console.log(layers);
  console.log(layers2);


}

$('#setFileInp').click(setFileInp);


$('#scenario').change(function(){
  setLayers();
})
$('[name=tempi_ritorno]').change(function(){
  setLayers();
})
$('[name=livelli]').change(function(){
  setLayers();
})
$('[name=vasca]').change(function(){
  setLayers();
})
$('[name=regime]').change(function(){
  setLayers();
})
$('[name=rete]').change(function(){
  setLayers();
})
$('[name=regime]').change(function(){
  setLayers();
})
$('[name=intervento]').change(function(){
  setLayers();
})

function setPrestazioni( response ){
  var x,resp,nsr,nfr,pr,vr;
  var nsi0=0;
  var nfi0=0;
  var nsiS=0;
  var nfiS=0;
  var pr0=0;
  var vr0=0;
  var prS=0;
  var vrS=0;  
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


  if (flag){
    for (resp in response){
      if (resp.indexOf('_CS_')>-1){
        nsi0=response[resp]["nsi"]||0;
        nfi0=response[resp]["nfi"]||0;
        pr0=response[resp]["pr"]||0;
        vr0=response[resp]["vr"]||0;
      }else{
        if (resp.indexOf('TOS')>-1)
          resp='T';
        if (resp.indexOf('LIG')>-1)
          resp='L';
        var intervento = $('[name=intervento]:checked').val().toUpperCase();
        intervento = '_'+intervento+'_';
        if (resp.indexOf(intervento)>-1){
          nsiS=response[resp]["nsi"]||0;
          nfiS=response[resp]["nfi"]||0;
          vrS=response[resp]["vr"]||0;
          prS=response[resp]["pr"]||0;          
        }
      }
    }
  }
  else{
    for (x in mapset_prestazioni){
      if (x.indexOf('_'+anni+'Y')>-1){
        nsi0=mapset_prestazioni[x]["nsi"]||0;
        nfi0=mapset_prestazioni[x]["nfi"]||0;
        pr0=mapset_prestazioni[x]["pr"]||0;
        vr0=mapset_prestazioni[x]["vr"]||0;
        for (resp in response){
          if (resp.indexOf('TOS')>-1)
            resp='T';
          if (resp.indexOf('LIG')>-1)
            resp='L';
          nsiS=response[resp]["nsi"]||0;
          nfiS=response[resp]["nfi"]||0;
          vrS=response[resp]["vr"]||0;
          prS=response[resp]["pr"]||0;
        }
      }
    }
  }

  if (nsi0!=0){
    nsr = ((nsi0 - nsiS)/nsi0)*100;
  }
  else{
    nsr = 100;
  }
  if (nfi0!=0){
    nfr = ((nfi0 - nfiS)/nfi0)*100;
  }
  else{
    nfr = 100;
  }
  if (pr0!=0){
    pr = ((pr0 - prS)/pr0)*100;
  }
  else{
    pr = 100;
  }
  if (vr0!=0){
    vr = ((vr0 - vrS)/vr0)*100;
  }
  else{
    vr = 100;
  }

  $("#nsi0").text((nsi0*100).toFixed(2) + ' %');
  $("#nfi0").text((nfi0*100).toFixed(2) + ' %');
  $("#nsiS").text((nsiS*100).toFixed(2) + ' %');
  $("#nfiS").text((nfiS*100).toFixed(2) + ' %');
  $("#nsr").text((nsr).toFixed(2) + ' %');
  $("#nfr").text((nfr).toFixed(2) + ' %');
  $("#pr").text((pr).toFixed(2) + ' %');
  $("#vr").text((vr).toFixed(2) + ' %');


  //Aggiorna il grafico
  chart.data.datasets[1].data = [vr,pr,nsr,nfr];
  chart.update();

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

  if (!flag){
    var baseLayer = new TileLayer({
      source: new OSM()
    });
  }
  else{
    var baseLayer = new TileLayer({
      source: new XYZ({
         url: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAoMBgDTD2qgAAAAASUVORK5CYII="
      })
    })
  }

  var sottoBacini =  new ImageLayer({
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_subcatchment'},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  var areaStudio =  new ImageLayer({

      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_area_studio'},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  if (flag){
    var reteLayer =  new ImageLayer({
        source: new ImageWMS({
          url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
          params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_rete_' + $('[name=regime]:checked').val()},
          ratio: 1,
          serverType: 'mapserver'
        })
      })
  }
  else{
    var reteLayer =  new ImageLayer({
        source: new ImageWMS({
          url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
          params: {'PROJECT':PROJECT,'MAP':MAPSET,'LAYERS': 'grp_rete'},
          ratio: 1,
          serverType: 'mapserver'
        })
      })
  }

  layer_0 = new ImageLayer({
      source: new ImageWMS({
        url: 'http://trigeau.servergis.it/gisclient/services/owsgw.php',
        params: {'PROJECT':PROJECT,'MAP':MAPSET},
        ratio: 1,
        serverType: 'mapserver'
      })
    })

  resultLayer =  new ImageLayer({
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

  //var map1Layers = ;
  //var map1Layers = [sottoBacini,areaStudio,reteLayer,layer_0];


  map1 = new Map({
    interactions: defaultInteractions({
      onFocusOnly: true
    }),
    target: 'principale',
    layers: [baseLayer,sottoBacini,areaStudio,reteLayer,layer_0],
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
