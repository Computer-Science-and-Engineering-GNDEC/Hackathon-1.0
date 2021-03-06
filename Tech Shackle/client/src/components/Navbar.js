import React, { Component } from 'react'
import {Navbar,NavDropdown,Nav,Form,FormControl,Button,Carousel} from 'react-bootstrap' 
import './Navbar.css';



export class Navb extends Component {
    render() {
        return (
            <div className="front">
                  <div className="topmenu">
                <Navbar bg="danger" expand="lg">

  <Navbar.Toggle aria-controls="basic-navbar-nav" />
  <Navbar.Collapse id="basic-navbar-nav">
    <Nav className="ml-auto">
      <Nav.Link href="#home">Alumini</Nav.Link>
      <Nav.Link href="#link">Contact</Nav.Link>
      <Nav.Link href="#link">Gallery</Nav.Link>
      
    </Nav>
    
  </Navbar.Collapse>
</Navbar>



            </div>

            <div className="middle">
            <Navbar bg="primary" expand="lg">
<Navbar.Brand href="#home"><img src={process.env.PUBLIC_URL+"logo.png"}></img></Navbar.Brand>
  <Navbar.Toggle aria-controls="basic-navbar-nav" />
  
</Navbar>
            </div>

            <div className="bottom">
            <Navbar bg="light" expand="lg">
  
  <Navbar.Toggle aria-controls="basic-navbar-nav" />
  <Navbar.Collapse id="basic-navbar-nav">
    <Nav className="ml-auto">
    <NavDropdown title="ABOUT US" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Principal Desk</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Administration</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Mission</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.4">Vision</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.5">Goals</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.6">Annual Reports</NavDropdown.Item>
        
        
      </NavDropdown>

      <NavDropdown title="ADMISSION" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Course Offered</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Enquiry Cum Registration</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Information Brochure</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.4">Frequently Asked Questions</NavDropdown.Item>
      </NavDropdown>

      <NavDropdown title="ACADEMICS" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
      </NavDropdown>

      <NavDropdown title="EXAMINATION" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
      </NavDropdown>

      <NavDropdown title="DEPARTMENTS" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
      </NavDropdown>

      <NavDropdown title="FACILITIES" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
      </NavDropdown>

      <NavDropdown title="RESEARCH" id="basic-nav-dropdown">
        <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
        <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
      </NavDropdown>
    </Nav>
    
  </Navbar.Collapse>
</Navbar>
            </div>
            <div className="container">
            <div>
                <div className="row">
                    <div className="col-3">Notice
                    </div>
                    <div className="col-9">
                        <marquee>Notice Board</marquee>
                        
                    </div>
                </div>
            </div>
            </div>
            
            <div className="slider">
                
            <Carousel fade>
  <Carousel.Item>
    <img
      className="d-block w-100"
      src={process.env.PUBLIC_URL+"campus3.jpg"}
      alt="First slide"
    />
    <Carousel.Caption>
      <h3>First slide label</h3>
      <p>Nulla vitae elit libero, a pharetra augue mollis interdum.</p>
    </Carousel.Caption>
  </Carousel.Item>
  <Carousel.Item>
    <img
      className="d-block w-100"
      src={process.env.PUBLIC_URL+"campus.jpeg"}
      alt="Second slide"
    />

    <Carousel.Caption>
      <h3>Second slide label</h3>
      <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    </Carousel.Caption>
  </Carousel.Item>
  <Carousel.Item>
    <img
      className="d-block w-100"
      src={process.env.PUBLIC_URL+"pc.jpg"}
      alt="Third slide"
    />

    <Carousel.Caption>
      <h3>Third slide label</h3>
      <p>Praesent commodo cursus magna, vel scelerisque nisl consectetur.</p>
    </Carousel.Caption>
  </Carousel.Item>
</Carousel>

            </div>
            
            </div>
          
        )
    }
}

export default Navb
