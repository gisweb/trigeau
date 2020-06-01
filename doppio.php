<?php
require_once "../../../config/config.php";
require_once ROOT_PATH . 'lib/GCService.php';

$gcService = GCService::instance();
$gcService->startSession();
$db = GCApp::getDB();

# nomi dei nodi
if (!((strpos ($_REQUEST["mapset"],"solarussa"))===False)){
    $nodo1='25';
    $nodo2='27';
}
if (!((strpos ($_REQUEST["mapset"],"toulon"))===False)){
    $nodo1='89';
    $nodo2='90';
}
$result=[];
$errors=[];
$val="";
try {
    $sql="SELECT * FROM ".$_REQUEST["mapset"].".v_trigeau_nsi";
    if(isset($_REQUEST["anni"])){
        $sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y'";
    }      
#   echo $sql; 
    $stmt = $db->prepare($sql);
    $stmt->execute();
    while($row = $stmt->fetch(PDO::FETCH_ASSOC)){
        $result[$row["result_id"]]=array("nsi"=>floatval($row["nsi"]));
    }   
} catch (Exception $e) {
    $errors[] = $e;
}

try {
    $sql="SELECT * FROM ".$_REQUEST["mapset"].".v_trigeau_nfi";
    if(isset($_REQUEST["anni"])){
        $sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y'";
    }   
#   echo $sql; 
    $stmt = $db->prepare($sql);
    $stmt->execute();
    while($row = $stmt->fetch(PDO::FETCH_ASSOC)){
        $result[$row["result_id"]]=array("nfi"=>floatval($row["nfi"]));
    }   
} catch (Exception $e) {
    $errors[] = $e;
}

try {
    $sql="SELECT * FROM ".$_REQUEST["mapset"].".rpt_outfallflow_sum";
    if(isset($_REQUEST["anni"])){
        $sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y'";
    }
    else{
        $mapset=$_REQUEST["mapset"];
        $sql = "(SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%2Y' ORDER BY max_flow DESC)
            UNION
            (SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%5Y' ORDER BY max_flow DESC)
            UNION
            (SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%10Y' ORDER BY max_flow DESC);";
    }
#    echo $sql;
    $stmt = $db->prepare($sql);
    $stmt->execute();
    while($row = $stmt->fetch(PDO::FETCH_ASSOC)){
        $key=$row["node_id"]==$nodo1?"n1":"n2";
        $result[$row["result_id"]]["pr"][$key] = floatval($row["max_flow"]);
        $result[$row["result_id"]]["vr"][$key] = floatval($row["total_vol"]);
    }   
} catch (Exception $e) {
    $errors[] = $e;
}



header("Content-Type: application/json; Charset=UTF-8");


if(empty($_REQUEST["callback"]))
    die(json_encode($result));
else
    die($_REQUEST["callback"]."(".json_encode($result).")");

?>
