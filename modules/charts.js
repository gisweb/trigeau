'use strict';
import Chart from 'chart.js';

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


export function setPrestazioni( response ){
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
