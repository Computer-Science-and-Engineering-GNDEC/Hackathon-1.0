import React from 'react'
import { Form, Button } from 'react-bootstrap'
import './Login.css'


function Login() {
  return (
    <div className="lb">
      <Form className="container">
        <Form.Group controlId="formBasicEmail">
          <Form.Label className="login">Login Using College Username/Password</Form.Label>
          <Form.Control type="email" placeholder="Enter email" className="txt" />
          <Form.Text className="text-muted">
    </Form.Text>
        </Form.Group>

        <Form.Group controlId="formBasicPassword">
          <Form.Control type="password" placeholder="Password" />
        </Form.Group>
        <div style={{ display: 'flex' }}>
          <Button variant="info" size='sm' type="submit"  style={{marginLeft:'41%'}} >
            Sign In
           </Button>
        </div>
      </Form>
    </div>
  )
}

export default Login
