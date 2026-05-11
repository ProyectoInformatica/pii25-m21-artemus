<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "esp_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if(isset($_GET['valor'])) {
    $valor = $_GET['valor'];
    $sql = "INSERT INTO sensor_data (valor) VALUES ($valor)";
    
    if ($conn->query($sql) === TRUE) {
        echo "Data inserted successfully";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
}
$conn->close();
?>
