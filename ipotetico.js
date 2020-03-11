'use strict';

var dt = require('./myfirstmodule');
var pp = require('./modules/maps')
var chr = require('./modules/charts')

const GISCLIENT_URL = "http://trigeau.servergis.it/gisclient/";
const QGIS_URL = "http://trigeau.servergis.it/cgi-bin/qgis_mapserv.fcgi";
const BASE_PATH = "/home/qgis/projects/world/";
var mapset_prestazioni;
var layer_0;
var resultLayer;
var lay_vuoto = 'vuoto.vuoto';
var map1,map2;
var rete,regime;
var MAPSET,PROJECT;


/// inizializzo
$.ajax({
  url: '/getExtent',
  dataType: "jsonp",
  data:{"schema_id":"inscostiero_light"},
  jsonpCallback: "jsoncallback",
  async: false,
  success: pp.initMaps

})

//NUOVO IPOTETICO
function setFileInp(){

  $("#loading-gif").show();
  $("#setFileInp").attr("disabled","disabled")


  $.ajax({
    url: "/simulazione",
    dataType: "jsonp",
    data:{
      "imp":$('[name=sup_impermeabile]:checked').val(),
      "schema_id":$('[name=rete]:checked').val() + "_" + $('[name=regime]:checked').attr("schema"),
      "anni":$('[name=tempi_ritorno]:checked').val(),
      "convpp":$('[name=conv_pp]:checked').val(),
      "convtv":$('[name=conv_tv]:checked').val()
    },
    jsonpCallback: "jsoncallback",
    async: false,
    success: pp.updateMaps

  })

}

function setMeteoriche(){
  var drwh = $('[name=riuso_meteoriche]:checked').val();
  console.log(drwh)
  if (drwh=="SI")
    $(".scenari").css('visibility', 'hidden');
  else
    $(".scenari").css('visibility', 'visible');

}

function setImpermeabile(){
  var imp = $('[name=sup_impermeabile]:checked').val();
  $('[name=conv_pp]').each(function(){
    if ($(this).attr("disabled","disabled")){
    }
  })
  $('[name=conv_tv]').each(function(){
    if ($(this).attr("disabled","disabled")){
    }
  })
  if (imp=="15"){
    $("#conv_pp_100").removeAttr('disabled');
    $("#conv_tv_100").removeAttr('disabled');
  }
  else if (imp=="30"){
    $("#conv_pp_100").removeAttr('disabled');
    $("#conv_tv_100").removeAttr('disabled');
    $("#conv_pp_50").removeAttr('disabled');
    $("#conv_tv_50").removeAttr('disabled');
  }
  else if (imp=="45"){
    $("#conv_pp_100").removeAttr('disabled');
    $("#conv_tv_100").removeAttr('disabled');
    $("#conv_pp_50").removeAttr('disabled');
    $("#conv_tv_50").removeAttr('disabled');
    $("#conv_pp_30").removeAttr('disabled');
    $("#conv_tv_30").removeAttr('disabled');    
  }
 else{
    $("#conv_pp_100").removeAttr('disabled');
    $("#conv_tv_100").removeAttr('disabled');
    $("#conv_pp_50").removeAttr('disabled');
    $("#conv_tv_50").removeAttr('disabled');
    $("#conv_pp_30").removeAttr('disabled');
    $("#conv_tv_30").removeAttr('disabled');    
    $("#conv_pp_20").removeAttr('disabled');
    $("#conv_tv_20").removeAttr('disabled');      
  }
}

$('#setFileInp').click(setFileInp);

$('[name=riuso_meteoriche]').change(function(){
  setMeteoriche();
})
$('[name=sup_impermeabile]').change(function(){
  setImpermeabile();
})






