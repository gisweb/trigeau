'use strict';

//x parte server attivare source service/bin activate e lanciare python swmm.py
//x parte client da /apps/trigeau lanciare yarn start
//xbuild yarn run build dopo aver vuotato dist poi copio i file in dist
var dt = require('./myfirstmodule');
var pp = require('./modules/maps')

const GISCLIENT_URL = "http://trigeau.servergis.it/gisclient/";
const QGIS_URL = "http://trigeau.servergis.it/cgi-bin/qgis_mapserv.fcgi";
const BASE_PATH = "/home/qgis/projects/world/";

//globalThis.SERVICE_URL = "http://localhost:4080"
globalThis.SERVICE_URL = "http://www.trigeau.servergis.it"

var mapset_prestazioni;
var layer_0;
var resultLayer;
var lay_vuoto = 'vuoto.vuoto';
var map1,map2;
var rete,regime;
var MAPSET,PROJECT;


/// inizializzo
$.ajax({
  url: globalThis.SERVICE_URL + '/getExtent',
  dataType: "jsonp",
  data:{"schema_id":"inscostiero_light"},
  jsonpCallback: "jsoncallback",
  async: false,
  success: pp.initMaps

})

$("#getRepsx a").attr("disabled","disabled")
$("#getRepdx a").attr("disabled","disabled")
$("#getRepsx a").removeAttr("href")
$("#getRepdx a").removeAttr("href")


//NUOVO IPOTETICO
function setFileInp(){

  $("#loading-gif").css("display", "block");
  $("#setFileInp").attr("disabled","disabled")

  $.ajax({
    url: globalThis.SERVICE_URL + '/simulazione',
    dataType: "jsonp",
    data:{
      "imp":$('[name=sup_impermeabile]:checked').val(),
      "schema_id":$('[name=rete]:checked').val() + "_" + $('[name=regime]:checked').attr("schema"),
      "anni":$('[name=tempi_ritorno]:checked').val(),
      "regime":$('[name=regime]:checked').val(),
      "convpp":$('[name=conv_pp]:checked').val(),
      "convtv":$('[name=conv_tv]:checked').val(),
      "drwh":$('[name=riuso_meteoriche]:checked').val()
    },
    jsonpCallback: "jsoncallback",
    async: false,
    success: pp.updateMaps

  })

}

function setMeteoriche(){
  var drwh = $('[name=riuso_meteoriche]:checked').val();
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
  $("#conv_pp_0").removeAttr('disabled');
  $("#conv_tv_0").removeAttr('disabled');

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






