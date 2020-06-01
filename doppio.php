<?php
require_once "../../../config/config.php";
require_once ROOT_PATH . 'lib/GCService.php';

$gcService = GCService::instance();
$gcService->startSession();
$db = GCApp::getDB();

$result=[];
$errors=[];
$val="";
try {
	$sql="SELECT * FROM ".$_REQUEST["mapset"].".v_trigeau_nsi";
	if(isset($_REQUEST["anni"])){
		$sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y_%'";
	}
	if(isset($_REQUEST["vasca"])){
		if ($_REQUEST["vasca"] == "vuota"){
			$val = "01";
		}
		if ($_REQUEST["vasca"] == "piena"){
			$val = "08";
		}
		$sql = $sql ." AND result_id LIKE '%_$val'";
	}		
#	echo $sql; 
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
		$sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y_%'";
	}	
	if(isset($_REQUEST["vasca"])){
		if ($_REQUEST["vasca"] == "vuota"){
			$val = "01";
		}
		if ($_REQUEST["vasca"] == "piena"){
			$val = "08";
		}
		$sql = $sql ." AND result_id LIKE '%_$val'";
	}
#	echo $sql; 
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
		$sql = $sql ." WHERE result_id LIKE '%_".$_REQUEST["anni"]."Y_%'";
		if(isset($_REQUEST["vasca"])){
			if ($_REQUEST["vasca"] == "vuota"){
				$val = "01";
			}
			if ($_REQUEST["vasca"] == "piena"){
				$val = "08";
			}
			$sql = $sql ." AND result_id LIKE '%_$val' ORDER BY max_flow DESC LIMIT 1";
		}
	}
	else{
		$mapset=$_REQUEST["mapset"];
		$sql = "(SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%2Y' ORDER BY max_flow DESC LIMIT 1)
			UNION
			(SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%5Y' ORDER BY max_flow DESC LIMIT 1)
			UNION
			(SELECT * FROM $mapset.rpt_outfallflow_sum WHERE result_id LIKE '%10Y' ORDER BY max_flow DESC LIMIT 1);";
	}
	$stmt = $db->prepare($sql);
	$stmt->execute();
	while($row = $stmt->fetch(PDO::FETCH_ASSOC)){
		$result[$row["result_id"]]["pr"] = floatval($row["max_flow"]);
		$result[$row["result_id"]]["vr"] = floatval($row["total_vol"]);
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
