import React, { Component } from 'react'
import {Carousel} from 'react-bootstrap'

export class MainCarousel extends Component {
    render() {
        return (
            <div>
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

export default MainCarousel
