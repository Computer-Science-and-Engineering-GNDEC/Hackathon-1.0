import React, { Component } from 'react'
import {Card, ListGroup,ListGroupItem,Container,Row,Col,Nav,Navbar,NavDropdown,Button} from 'react-bootstrap'
import './News.css';

export class News extends Component {
    render() {
        return (
                <div className="cards">
           
           <Container>
  <Row>
    <Col sm={9} style={{padding:'50px 10px 50px 80px'}}>
    <div className="newscolor" >
            <h2>NEWS</h2>
        </div>
    <div className="row">
        
                    <div className="col-4">
                    <Card style={{ width: 'auto' }}>
  <Card.Img variant="top" src={process.env.PUBLIC_URL+"card1.jpeg"} />
  <Card.Body>
    <Card.Title>Card Title</Card.Title>
    <Card.Text>
      Some quick example text to build on the card title and make up the bulk of
      the card's content.
    </Card.Text>
  </Card.Body>
  
  <Card.Body>
    <Card.Link href="#">Card Link</Card.Link>
    <Card.Link href="#">Another Link</Card.Link>
  </Card.Body>
</Card>

                </div>
                <div className="col-4">
                <Card style={{ width: 'auto' }}>
  <Card.Img variant="top" src={process.env.PUBLIC_URL+"card2.jpg"} />
  <Card.Body>
    <Card.Title>Card Title</Card.Title>
    <Card.Text>
      Some quick example text to build on the card title and make up the bulk of
      the card's content.
    </Card.Text>
  </Card.Body>
  
  <Card.Body>
    <Card.Link href="#">Card Link</Card.Link>
    <Card.Link href="#">Another Link</Card.Link>
  </Card.Body>
</Card>
                </div>
                <div className="col-4">
                <Card style={{ width: 'auto' }}>
  <Card.Img variant="top" src={process.env.PUBLIC_URL+"card2.jpg"} />
  <Card.Body>
    <Card.Title>Card Title</Card.Title>
    <Card.Text>
      Some quick example text to build on the card title and make up the bulk of
      the card's content.
    </Card.Text>
  </Card.Body>
  
  <Card.Body>
    <Card.Link href="#">Card Link</Card.Link>
    <Card.Link href="#">Another Link</Card.Link>
  </Card.Body>
</Card>
                </div>
                </div>

    </Col>


    <Col sm={3} style={{padding:'50px'}}>
        <div className="newscolor">
            <h2>EVENTS</h2>
        </div>
        <div>
        <Card style={{ width: '18rem' }}>
  <Card.Img variant="top" src={process.env.PUBLIC_URL+"card1.jpeg"} />
  <Card.Body>
    <Card.Title>Card Title</Card.Title>
    <Card.Text>
      Some quick example text to build on the card title and make up the bulk of
      the card's content.
    </Card.Text>
  </Card.Body>
  
  <Card.Body>
    <Card.Link href="#">Card Link</Card.Link>
    <Card.Link href="#">Another Link</Card.Link>
  </Card.Body>
</Card>
        </div>
    </Col>
  </Row>
</Container>


<div className="Director">
<div className="container">

            <div>
                <div className="newscolor" style={{padding:'30px 20px 10px 80px'}} >
                    <h2><b>MESSAGE FROM THE PRINCIPAL</b></h2>
                </div>
                <div className="row"style={{padding:'30px 20px 10px 60px'}}>
                    <div className="col-4" >
                    <Card style={{ width: '20rem' }}>
  <Card.Img variant="top" src={process.env.PUBLIC_URL+"principal.jpg"}/>
</Card>
                    </div>
                    <div className="col-7">
                    <Card>

  <Card.Body>
    <blockquote className="blockquote mb-1">
      <p style={{fontSize:'50%'},{padding:'3px'}}>
        {' '}
        Welcome to Guru Nanak Dev Engineering College, Ludhiana(an autonomous college under UGC Act),
         established in 1956, was set up under the aegis of Nankana Sahib Education Trust, devoted to
         the cause of rural education to meet the growing demand for technical and professional manpower 
         and industries. We are proud that this institution has consistently maintained its tradition of
          excellence in the field of technical education till date. The college has been declared an autonomous 
         college by UGC, New Delhi on 17.8.2012. The college has privilege of starting Ph.D degree under Quality Improvement
         Programme (QIP) by AICTE, New Delhi. The college has been accredited with ‘A’ Grade by NAAC. The college has attained 
        ISO 9001:2015 Certification and the UG programmes are accredited by IEI. Recently, the Institute has been awarded following 
        ranking by India Today.{' '}
      </p>
      <footer className="blockquote-footer">
    <cite title="Source Title">Dr. Sehijpal Singh</cite>
      </footer>
    </blockquote>
  </Card.Body>
</Card>
                        
                    </div>
                </div>
            </div>
            </div>

</div>  

<div>
    <footer>
    <Navbar bg="light" expand="lg">
  <Navbar.Brand href="#home">GNDEC-Ludhiana</Navbar.Brand>
  <Navbar.Toggle aria-controls="basic-navbar-nav" />
  <Navbar.Collapse id="basic-navbar-nav">
    <Nav className="mr-auto">
      <Nav.Link href="#home">Home</Nav.Link>
      <Nav.Link href="#link">Link</Nav.Link>
      
    </Nav>
  </Navbar.Collapse>
</Navbar>
    </footer>
</div>

  </div>
        )
    }
}

export default News
