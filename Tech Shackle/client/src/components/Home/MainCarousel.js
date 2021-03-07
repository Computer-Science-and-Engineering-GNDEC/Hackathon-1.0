import React, { Component } from 'react'
import {Carousel} from 'react-bootstrap'
import './MainCarousel'

export class MainCarousel extends Component {
    render() {
        return (
            <div>
                 <div className="slider">

<Carousel fade>
<Carousel.Item >
<img
className="d-block w-100"
src={process.env.PUBLIC_URL+"campus3.jpg"}
alt="First slide"
/>
<Carousel.Caption>
<h3>First slide label</h3>
</Carousel.Caption>
</Carousel.Item>
<Carousel.Item>
<img
className="d-block w-100"
src={process.env.PUBLIC_URL+"campus.jpeg"}
alt="Second slide"
/>

<Carousel.Caption>
<h3>CATALYZING CAREER</h3>

</Carousel.Caption>
</Carousel.Item>
<Carousel.Item>
<img
className="d-block w-100"
src={process.env.PUBLIC_URL+"c1.jpg"}
alt="Third slide"
/>

<Carousel.Caption>
<h3>Third slide label</h3>

</Carousel.Caption>
</Carousel.Item>
</Carousel>
            </div>
            </div>
        )
    }
}

export default MainCarousel
