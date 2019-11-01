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
	$sql="SELECT * FROM ".$_REQUEST["scenario"].".v_trigeau_nsi";
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
		$result[$row["result_id"]]=array("nsi"=>floatval($row["nsi"]."0"));
	}	
} catch (Exception $e) {
    $errors[] = $e;
}

try {
	$sql="SELECT * FROM ".$_REQUEST["scenario"].".v_trigeau_nfi";
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
		$result[$row["result_id"]]=array("nfi"=>floatval($row["nfi"]."0"));
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
