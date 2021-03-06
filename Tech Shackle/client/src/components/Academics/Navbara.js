import React from 'react'
import {Navbar} from 'react-bootstrap'

function Navbara() {
    return (
        <div>
            <div className="middle">
            <Navbar  bg="white" expand="lg">
<Navbar.Brand href="#home"><img class="img-fluid" src={process.env.PUBLIC_URL+"logo.png"}></img></Navbar.Brand>
  
  
</Navbar>
            </div>
        </div>
    )
}

export default Navbara
