
<?php
$username= $_POST['username'];
$password= $_POST['password'];
//
$link = mysqli_connect("localhost", "root", "", "aclogin") or die($link);
$username= stripcslashes($username);
$password =stripcslashes($password);
$username =mysqli_real_escape_string($link,$username);
$password= mysqli_real_escape_string($link,$password);
//
mysqli_connect( "localhost","root","");
mysqli_select_db( $link, "aclogin");
//

$result = mysqli_query ($link, "select * from users where username = '$username' and password= '$password'")
          or die("failed to query database ".mysqli_error($link));
if (!$result) {
    printf("Error: %s\n", mysqli_error($con));
    exit();
}

$row= mysqli_fetch_array($result);
if($row['username']==$username && $row['password']== $password){
    echo "Login success!! Welcome".$row['username'];

}else{
    echo "Failed try{
    }
    catch(Exception $e){

    }";
}
?>